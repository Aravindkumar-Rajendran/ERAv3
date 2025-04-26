from playwright.async_api import async_playwright, Page
from typing import Dict, List, Optional, Any
import json
import os
from logging_config import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class BrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.custom_commands = self._load_custom_commands()

    def _load_custom_commands(self) -> Dict:
        try:
            with open(os.getenv("CUSTOM_COMMANDS_FILE", "custom_commands.json"), "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading custom commands: {str(e)}")
            return {"commands": []}

    async def initialize(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch()
            logger.info("Browser automation initialized successfully")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser automation closed")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def execute_actions(self, page: Page, actions: List[Dict]) -> Dict:
        results = []
        for action in actions:
            try:
                result = await self._execute_action(page, action)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing action {action}: {str(e)}")
                raise
        return {"success": True, "results": results}

    async def _execute_action(self, page: Page, action: Dict) -> Dict:
        action_type = action.get("type")
        selector = action.get("selector")
        value = action.get("value")
        url = action.get("url")

        try:
            if action_type == "click":
                # Wait for the element to be visible and clickable
                element = await page.wait_for_selector(selector, state="visible", timeout=10000)
                if element:
                    await element.click()
                    logger.info(f"Clicked element: {selector}")
                    return {"type": "click", "selector": selector, "success": True}
                else:
                    raise ValueError(f"Element not found: {selector}")
            
            elif action_type == "fill":
                # Wait for the input field to be visible and enabled
                element = await page.wait_for_selector(selector, state="visible", timeout=10000)
                if element:
                    # Clear the field first
                    await element.fill("")
                    # Fill with the new value
                    await element.fill(value)
                    logger.info(f"Filled element {selector} with value: {value}")
                    return {"type": "fill", "selector": selector, "value": value, "success": True}
                else:
                    raise ValueError(f"Input field not found: {selector}")
            
            elif action_type == "extract":
                # Wait for the element to be visible
                element = await page.wait_for_selector(selector, state="visible", timeout=10000)
                if element:
                    content = await element.text_content()
                    logger.info(f"Extracted content from {selector}: {content}")
                    return {"type": "extract", "selector": selector, "content": content, "success": True}
                else:
                    raise ValueError(f"Element not found: {selector}")
            
            elif action_type == "navigate":
                await page.goto(url)
                # Wait for the page to load
                await page.wait_for_load_state("networkidle")
                logger.info(f"Navigated to URL: {url}")
                return {"type": "navigate", "url": url, "success": True}
            
            elif action_type == "scroll":
                if value == "bottom":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                elif value == "top":
                    await page.evaluate("window.scrollTo(0, 0)")
                else:
                    await page.evaluate(f"window.scrollTo(0, {value})")
                logger.info(f"Scrolled to position: {value}")
                return {"type": "scroll", "value": value, "success": True}
            
            elif action_type == "screenshot":
                screenshot = await page.screenshot(path=f"screenshots/{selector.replace('/', '_')}.png")
                logger.info(f"Saved screenshot to: screenshots/{selector.replace('/', '_')}.png")
                return {"type": "screenshot", "path": f"screenshots/{selector.replace('/', '_')}.png", "success": True}
            
            elif action_type == "extract_table":
                table_data = await page.evaluate(f"""
                    (selector) => {{
                        const table = document.querySelector(selector);
                        if (!table) return null;
                        
                        const rows = Array.from(table.querySelectorAll('tr'));
                        return rows.map(row => {{
                            const cells = Array.from(row.querySelectorAll('td, th'));
                            return cells.map(cell => cell.textContent.trim());
                        }});
                    }}
                """, selector)
                logger.info(f"Extracted table data from: {selector}")
                return {"type": "extract_table", "selector": selector, "data": table_data, "success": True}
            
            else:
                error_msg = f"Unknown action type: {action_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}")
            raise

    async def execute_custom_command(self, page: Page, command_name: str, parameters: Dict) -> Dict:
        command = next((cmd for cmd in self.custom_commands["commands"] if cmd["name"] == command_name), None)
        if not command:
            error_msg = f"Custom command not found: {command_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Replace parameters in actions
            actions = []
            for action in command["actions"]:
                action_str = json.dumps(action)
                for param, value in parameters.items():
                    action_str = action_str.replace(f"{{{param}}}", str(value))
                actions.append(json.loads(action_str))

            logger.info(f"Executing custom command: {command_name} with parameters: {parameters}")
            return await self.execute_actions(page, actions)
        except Exception as e:
            logger.error(f"Error executing custom command {command_name}: {str(e)}")
            raise 