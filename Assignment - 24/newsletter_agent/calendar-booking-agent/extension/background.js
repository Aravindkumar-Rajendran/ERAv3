// Default server URL
const DEFAULT_SERVER_URL = 'http://localhost:3025';

// Track the active tab where we're executing calendar actions
let currentActionTab = null;

// Server discovery
async function discoverServer() {
  const hosts = ['localhost', '127.0.0.1'];
  const defaultPort = 3025;
  const ports = [defaultPort];
  
  // Add additional ports for discovery
  for (let p = 3026; p <= 3035; p++) {
    ports.push(p);
  }
  
  console.log('Attempting to discover server...');
  
  for (const host of hosts) {
    for (const port of ports) {
      try {
        const url = `http://${host}:${port}/.identity`;
        console.log(`Checking ${url}`);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          
          if (data.signature === 'mcp-browser-connector-24x7') {
            const serverUrl = `http://${host}:${port}`;
            console.log(`Found server at ${serverUrl}`);
            
            // Save the discovered URL to storage
            chrome.storage.sync.set({ backendUrl: serverUrl });
            return serverUrl;
          }
        }
      } catch (error) {
        console.warn(`Failed to connect to ${host}:${port}`, error);
      }
    }
  }
  
  console.warn('No server found during discovery');
  return null;
}

// Get server URL from storage or discover it
async function getServerUrl() {
  const result = await chrome.storage.sync.get('backendUrl');
  let serverUrl = result.backendUrl || DEFAULT_SERVER_URL;
  
  // Test if stored URL is still valid
  try {
    const response = await fetch(`${serverUrl}/.identity`);
    if (response.ok) {
      return serverUrl;
    }
  } catch (error) {
    console.warn('Stored server URL is not valid, attempting discovery...');
  }
  
  // If not valid, try to discover again
  const discoveredUrl = await discoverServer();
  return discoveredUrl || DEFAULT_SERVER_URL;
}

// Execute calendar actions in the proper tab
async function executeCalendarAction(action) {
  try {
    // Get current tab for operations
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
      throw new Error('No active tab found');
    }
    
    // Check if we need to navigate to Google Calendar
    const isCalendarTab = tab.url && tab.url.includes('calendar.google.com');
    
    if (!isCalendarTab) {
      // We need to navigate to Google Calendar first
      await navigateToGoogleCalendar(tab.id);
    } else {
      // We're already on Google Calendar, use this tab
      currentActionTab = tab.id;
    }
    
    // Execute the steps
    for (const step of action.steps) {
      await executeStep(step);
    }
    
    return { success: true, message: 'Calendar action completed successfully' };
  } catch (error) {
    console.error('Error executing calendar action:', error);
    return {
      success: false,
      error: error.message,
    };
  }
}

// Navigate to Google Calendar in the given tab
async function navigateToGoogleCalendar(tabId) {
  return new Promise((resolve, reject) => {
    chrome.tabs.update(tabId, { url: 'https://calendar.google.com/' }, (tab) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      
      currentActionTab = tab.id;
      
      // Wait for the page to load
      const listener = (tabId, changeInfo) => {
        if (tabId === tab.id && changeInfo.status === 'complete') {
          chrome.tabs.onUpdated.removeListener(listener);
          
          // Add extra time for the page to fully initialize
          setTimeout(resolve, 2000);
        }
      };
      
      chrome.tabs.onUpdated.addListener(listener);
    });
  });
}

// Execute a single step in the browser
async function executeStep(step) {
  if (!currentActionTab) {
    throw new Error('No active calendar tab');
  }
  
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(
      currentActionTab,
      {
        type: 'execute-step',
        step
      },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        
        if (response && response.error) {
          reject(new Error(response.error));
          return;
        }
        
        resolve(response);
      }
    );
  });
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'execute-calendar-action') {
    // Execute the calendar action
    executeCalendarAction(message.action)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    // Return true to indicate we'll send a response asynchronously
    return true;
  }
  
  if (message.type === 'discover-server') {
    discoverServer()
      .then(url => sendResponse({ success: !!url, url }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    return true;
  }
});

// Run server discovery on extension installation or update
chrome.runtime.onInstalled.addListener(() => {
  discoverServer().then(url => {
    console.log('Server discovery completed on install:', url || 'Not found');
  });
}); 