import os
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Dict, List, Optional
import json
from logging_config import logger
from dotenv import load_dotenv

load_dotenv()

class OpenAIHandler:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def analyze_command(self, command: str, page_content: str, previous_action: Optional[Dict] = None) -> Dict:
        try:
            prompt = f"""
            You are a browser automation expert. Analyze the following command in the context of the actual webpage content.
            
            Command: {command}
            
            Previous Action: {json.dumps(previous_action) if previous_action else "None"}
            
            Current Page Content:
            {page_content[:4000]}  # Limit content length to avoid token limits
            
            Return a JSON response with the following structure:
            {{
                "action": {{
                    "type": "click|fill|extract|navigate|scroll|screenshot",
                    "selector": "CSS selector or XPath (must be valid for the actual page content)",
                    "value": "optional value for fill actions",
                    "url": "optional URL for navigate actions"
                }},
                "confidence": 0.0-1.0,
                "explanation": "brief explanation of the action and why this specific selector was chosen",
                "isComplete": true/false  # Set to true if this is the final action needed
            }}
            
            Important:
            1. Only use selectors that are actually present in the page content
            2. Verify the selectors against the actual HTML structure
            3. If unsure about a selector, set a lower confidence score
            4. For fill actions, ensure the target element is an input field
            5. For click actions, ensure the target is clickable
            6. Consider the previous action when determining the next action
            7. Set isComplete to true only when the command is fully executed
            """
            
            # Log the input to LLM
            logger.info("\n" + "="*80 + "\nLLM Input:\n" + "="*80)
            logger.info(f"Command: {command}")
            if previous_action:
                logger.info(f"Previous Action: {json.dumps(previous_action)}")
            logger.info("\nPage Content Preview (first 500 chars):")
            logger.info(page_content[:500] + "..." if len(page_content) > 500 else page_content)
            logger.info("="*80 + "\n")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a browser automation expert that analyzes commands and returns precise actions based on actual page content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=self.max_tokens,
                response_format={ "type": "json_object" }  # Force JSON response
            )
            
            # Parse and validate the response
            if not response or not response.choices or not response.choices[0].message:
                raise ValueError("Invalid response from OpenAI API")
                
            content = response.choices[0].message.content
            
            # Remove markdown code block tags if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()  # Remove any extra whitespace
            
            try:
                result = json.loads(content)
                
                # Validate required fields
                if not isinstance(result, dict):
                    raise ValueError("Response is not a JSON object")
                    
                if 'action' not in result:
                    raise ValueError("Response missing 'action' field")
                    
                if not isinstance(result['action'], dict):
                    raise ValueError("'action' field must be an object")
                    
                if 'type' not in result['action']:
                    raise ValueError("Action missing 'type' field")
                
                # Log the output from LLM
                logger.info("\n" + "="*80 + "\nLLM Output:\n" + "="*80)
                logger.info(f"Confidence: {result.get('confidence', 0)}")
                logger.info("\nAction:")
                action = result.get('action', {})
                logger.info(f"- Type: {action.get('type')}")
                if action.get('selector'):
                    logger.info(f"  Selector: {action.get('selector')}")
                if action.get('url'):
                    logger.info(f"  URL: {action.get('url')}")
                if action.get('value'):
                    logger.info(f"  Value: {action.get('value')}")
                logger.info(f"\nExplanation: {result.get('explanation', 'No explanation provided')}")
                logger.info(f"Is Complete: {result.get('isComplete', False)}")
                logger.info("="*80 + "\n")
                
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
                logger.error(f"Raw response: {content}")
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            except ValueError as e:
                logger.error(f"Invalid response structure: {str(e)}")
                logger.error(f"Raw response: {content}")
                raise
                
        except Exception as e:
            logger.error(f"Error analyzing command: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_selector(self, description: str, page_content: str) -> str:
        try:
            prompt = f"""
            Generate a reliable CSS selector or XPath for the following element description:
            
            Description: {description}
            Page Content: {page_content[:2000]}
            
            Return a JSON response with the following structure:
            {{
                "selector": "CSS selector or XPath",
                "type": "css|xpath",
                "confidence": 0.0-1.0,
                "explanation": "brief explanation of the selector choice"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a web scraping expert. Generate reliable selectors for web elements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Selector generated", description=description, result=result)
            return result
            
        except Exception as e:
            logger.error(f"Error generating selector: {str(e)}")
            raise 