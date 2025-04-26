from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from browser_automation import BrowserAutomation
from openai_utils import OpenAIHandler
from logging_config import logger
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    command: str
    url: str
    tabId: int
    pageContent: Optional[str] = None
    previousAction: Optional[Dict] = None

class Action(BaseModel):
    type: str
    selector: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None

class CommandResponse(BaseModel):
    success: bool
    action: Optional[Action] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    explanation: Optional[str] = None
    isComplete: bool = False

# Initialize handlers
browser_automation = BrowserAutomation()
openai_handler = OpenAIHandler()

@app.on_event("startup")
async def startup_event():
    await browser_automation.initialize()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    await browser_automation.close()
    logger.info("Application shutdown")

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        # Check if it's a chrome:// URL
        if url.startswith('chrome://'):
            return False
        # Check if it has at least a scheme and netloc
        return all([result.scheme, result.netloc])
    except:
        return False

@app.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    try:
        logger.info(f"Received command: {request.command}, URL: {request.url}")
        
        # Validate URL
        if not is_valid_url(request.url):
            error_msg = f"Invalid URL: {request.url}"
            logger.error(error_msg)
            return CommandResponse(
                success=False,
                error=error_msg
            )
        
        # Create a new page
        page = await browser_automation.browser.new_page()
        
        try:
            # Step 1: Navigate to the URL
            await page.goto(request.url)
            logger.info(f"Navigated to URL: {request.url}")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            # Get page content if not provided
            page_content = request.pageContent or await page.content()
            
            # Step 2: Analyze the command with page content
            analysis = await openai_handler.analyze_command(request.command, page_content)
            
            if analysis["confidence"] < 0.5:
                logger.warning(f"Low confidence in command analysis: {request.command}, confidence: {analysis['confidence']}")
            
            return CommandResponse(
                success=True,
                action=analysis["action"],
                explanation=analysis["explanation"],
                isComplete=analysis.get("isComplete", False)
            )
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
            
        finally:
            await page.close()
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return CommandResponse(
            success=False,
            error=str(e)
        )

@app.post("/next_action", response_model=CommandResponse)
async def get_next_action(request: CommandRequest):
    try:
        logger.info(f"Getting next action for command: {request.command}")
        
        # Analyze the command with updated page content
        analysis = await openai_handler.analyze_command(
            request.command, 
            request.pageContent,
            previous_action=request.previousAction
        )
        
        return CommandResponse(
            success=True,
            action=analysis["action"],
            explanation=analysis["explanation"],
            isComplete=analysis.get("isComplete", False)
        )
            
    except Exception as e:
        logger.error(f"Error getting next action: {str(e)}")
        return CommandResponse(
            success=False,
            error=str(e)
        )

@app.get("/custom-commands")
async def get_custom_commands():
    try:
        return browser_automation.custom_commands
    except Exception as e:
        logger.error(f"Error getting custom commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 