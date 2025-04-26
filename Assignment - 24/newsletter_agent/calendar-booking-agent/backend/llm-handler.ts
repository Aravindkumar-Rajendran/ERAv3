import OpenAI from 'openai';
import { Logger } from 'pino';

type CalendarAction = {
  actionType: 'create' | 'update' | 'delete' | 'find';
  steps: {
    tool: string;
    parameters: Record<string, any>;
  }[];
  context: {
    summary?: string;
    description?: string;
    startDate?: string;
    startTime?: string;
    endDate?: string;
    endTime?: string;
    location?: string;
    attendees?: string[];
    eventId?: string;
  };
};

export class LLMHandler {
  private openai: OpenAI;
  private logger: Logger;

  constructor(openai: OpenAI, logger: Logger) {
    this.openai = openai;
    this.logger = logger;
  }

  /**
   * Process natural language calendar query and convert to actionable steps
   */
  async processCalendarQuery(query: string): Promise<CalendarAction> {
    this.logger.info({ query }, 'Processing calendar query with LLM');
    
    try {
      const response = await this.openai.chat.completions.create({
        model: process.env.OPENAI_MODEL || 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: `You are a calendar assistant that helps users manage their Google Calendar events through browser automation.
            
Your task is to:
1. Understand the user's natural language request about calendar management
2. Extract all relevant event details (date, time, title, description, etc.)
3. Generate precise browser automation steps using the available browser tools:
   - navigate (to Google Calendar)
   - click (on buttons, elements)
   - type (in input fields)
   - select_option (from dropdowns)
   - wait (for elements to load)

Available browser automation tools:
- mcp_browser_navigate: Navigate to a URL
- mcp_browser_click: Click on a webpage element
- mcp_browser_type: Type text into a field
- mcp_browser_select_option: Select option from dropdown
- mcp_browser_wait: Wait for specified time in seconds

For each step, provide:
1. The tool to use
2. The exact parameters for each tool call (element reference, text to type, etc.)

Response format must be a valid JSON object with:
{
  "actionType": "create" | "update" | "delete" | "find",
  "steps": [
    {
      "tool": "mcp_browser_navigate",
      "parameters": { "url": "https://calendar.google.com" }
    },
    ...more steps
  ],
  "context": {
    // Event details extracted from the query
    "summary": "Meeting with John",
    "description": "Quarterly review", 
    "startDate": "2023-11-15",
    "startTime": "14:00",
    "endDate": "2023-11-15",
    "endTime": "15:00",
    "location": "Conference Room A",
    "attendees": ["john@example.com"],
    "eventId": "abc123" // Only for update/delete
  }
}`
          },
          {
            role: 'user',
            content: query
          }
        ],
        temperature: 0.2,
        response_format: { type: 'json_object' }
      });

      const content = response.choices[0]?.message?.content;
      
      if (!content) {
        throw new Error('No content in LLM response');
      }

      const calendarAction = JSON.parse(content) as CalendarAction;
      this.logger.info({ actionType: calendarAction.actionType }, 'Calendar action determined by LLM');
      
      return calendarAction;
    } catch (error) {
      this.logger.error({ error }, 'Error in LLM processing');
      throw error;
    }
  }
} 