import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import pino from 'pino';
import { createServer } from 'http';
import OpenAI from 'openai';
import { config } from 'dotenv';
import { LLMHandler } from './llm-handler.js';

config();

// Setup logger
const logger = pino({
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
    },
  },
});

const app = express();
const httpServer = createServer(app);
const wss = new WebSocketServer({ server: httpServer });

// Create LLM handler
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

// Create LLM handler
const llmHandler = new LLMHandler(openai, logger);

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ extended: true }));

// Routes
app.get('/.identity', (req, res) => {
  res.json({
    name: 'Calendar Booking Agent Server',
    version: '1.0.0',
    signature: 'mcp-browser-connector-24x7',
  });
});

app.post('/process-query', async (req, res) => {
  try {
    const { query } = req.body;
    
    if (!query) {
      return res.status(400).json({ error: 'No query provided' });
    }
    
    logger.info({ query }, 'Processing calendar query');
    
    const result = await llmHandler.processCalendarQuery(query);
    
    return res.json({ result });
  } catch (error) {
    logger.error({ error }, 'Error processing query');
    return res.status(500).json({ error: 'Failed to process query' });
  }
});

// WebSocket connection for browser communication
wss.on('connection', (ws) => {
  logger.info('Browser client connected');
  
  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      logger.info({ type: data.type }, 'Received message from browser');
      
      if (data.type === 'calendar-action-complete') {
        // Handle action completed notification
        logger.info({ action: data.action }, 'Calendar action completed');
      } else if (data.type === 'calendar-action-error') {
        // Handle action error notification
        logger.error({ error: data.error }, 'Calendar action error');
      }
    } catch (error) {
      logger.error({ error }, 'Error processing websocket message');
    }
  });
  
  ws.on('close', () => {
    logger.info('Browser client disconnected');
  });
});

// Start server
const PORT = process.env.PORT || 3025;
httpServer.listen(PORT, () => {
  logger.info(`Server listening on port ${PORT}`);
}); 