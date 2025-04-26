# Calendar Booking Agent

A Chrome extension that uses natural language processing to automate calendar event operations in Google Calendar through browser automation.

## Features

- Create, update, and delete calendar events using natural language
- Process queries like "Schedule a meeting with John tomorrow at 3pm for 1 hour"
- Automatically extract event details like title, date, time, attendees, and location
- Browser automation to interact with Google Calendar
- History of recent requests for quick access
- Real-time status updates

## Architecture

The project consists of two main components:

1. **Chrome Extension**: Provides the user interface for entering natural language queries and displays the extracted event details.
2. **Backend Server**: Processes natural language queries using LLM (Large Language Model) and generates browser automation steps.

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd calendar-booking-agent/backend
   ```

2. Create a `.env` file based on the `.env.example` template and add your OpenAI API key.

3. Install dependencies:
   ```bash
   npm install
   ```

4. Build and start the server:
   ```bash
   npm run build
   npm start
   ```

The server will start at `http://localhost:3025` by default.

### Chrome Extension Setup

1. Navigate to the extension directory:
   ```bash
   cd calendar-booking-agent/extension
   ```

2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right corner
4. Click "Load unpacked" and select the `extension` directory
5. The extension should now be installed and visible in your Chrome toolbar

## Usage

1. Click the Calendar Booking Agent icon in your Chrome toolbar
2. Enter your calendar request in natural language (e.g., "Set up a meeting with the design team on Friday at 2pm for 45 minutes")
3. Click "Process Request"
4. The extension will:
   - Extract event details from your query
   - Display the extracted information
   - Automatically navigate to Google Calendar and create the event

## Examples of Supported Queries

- "Schedule a meeting with John tomorrow at 3pm for 1 hour"
- "Create a dentist appointment on June 15th at 10am"
- "Set up a weekly team meeting every Monday at 9am starting next week"
- "Cancel my meeting with Sarah on Thursday"
- "Move my 2pm meeting today to 4pm"
- "Find my meetings with the marketing team next week"

## Development

### Backend Development

The backend is built with Express.js and TypeScript, with the following key files:
- `server.ts`: Main Express application
- `llm-handler.ts`: Handles processing of natural language with OpenAI

### Extension Development

The Chrome extension consists of:
- `manifest.json`: Extension configuration
- `popup.html/js`: The UI for entering queries
- `background.js`: Handles communication with the backend
- `content.js`: Performs the actual browser automation on Google Calendar

## License

This project is licensed under the MIT License. 