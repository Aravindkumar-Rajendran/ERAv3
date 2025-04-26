// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Update this with your FastAPI server URL
const CALENDAR_URL = 'https://calendar.google.com/';
const MAX_ACTION_ATTEMPTS = 5; // Maximum number of action attempts before stopping

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'executeCommand') {
        executeCommand(request.command, request.targetSite, request.settings)
            .then(response => sendResponse(response))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Required for async response
    }
});

async function executeCommand(command, targetSite, settings) {
    let tab;
    try {
        // Get initial tab information
        [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Navigate to Google Calendar if not already there
        if (!tab.url.includes(targetSite)) {
            await chrome.tabs.update(tab.id, { url: CALENDAR_URL });
            await waitForTabLoad(tab.id);
            [tab] = await chrome.tabs.query({ active: true, currentWindow: true }); // Re-query after load
        }

        let currentUrl = tab.url;
        let currentContent = await getPageContent(tab.id);
        let actionHistory = []; // Initialize action history array
        let consecutiveFailedActions = 0; // Track failed actions
        let previousAction = null; // Track the previous action to detect loops
        let actionAttemptCount = {}; // Count attempts for each action type

        // Add calendar-specific context to the command
        let enrichedCommand = enrichCalendarCommand(command, settings);
        
        // Initial call to /execute with calendar context
        const initialResponse = await fetch(`${settings.apiUrl || API_BASE_URL}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: enrichedCommand,
                url: currentUrl,
                tabId: tab.id,
                pageContent: currentContent,
                context: {
                    type: 'calendar',
                    defaultDuration: settings.defaultDuration,
                    defaultReminder: settings.defaultReminder
                }
            })
        });

        if (!initialResponse.ok) {
            throw new Error(`HTTP error! status: ${initialResponse.status}`);
        }
        
        let currentResult = await initialResponse.json();
        actionHistory.push(currentResult); // Add initial result to history

        // Loop as long as the backend provides an action in the latest result
        while (currentResult && currentResult.action) {
            const actionToPerform = currentResult.action;
            console.log('Performing calendar action:', actionToPerform);
            
            // Check for action loop (same action type and selector)
            const actionKey = `${actionToPerform.type}-${actionToPerform.selector || 'no-selector'}`;
            actionAttemptCount[actionKey] = (actionAttemptCount[actionKey] || 0) + 1;
            
            // If we've tried the same action too many times, stop
            if (actionAttemptCount[actionKey] > MAX_ACTION_ATTEMPTS) {
                console.warn(`Action ${actionKey} attempted too many times (${actionAttemptCount[actionKey]}). Breaking out of potential loop.`);
                currentResult = { 
                    message: `Could not complete the operation. The action "${actionToPerform.type}" was unsuccessful.`,
                    error: "Max retries reached for this action."
                };
                break;
            }
            
            // Perform the action and get success status
            const actionSuccess = await performAction(actionToPerform, tab.id);
            
            // Handle failed actions (when selectors don't exist)
            if (actionSuccess === false) {
                consecutiveFailedActions++;
                console.warn(`Action failed: ${actionToPerform.type} on ${actionToPerform.selector || 'unknown'}`);
                
                // If we've failed too many consecutive actions, break out
                if (consecutiveFailedActions >= 3) {
                    console.error("Too many consecutive failed actions, stopping execution");
                    currentResult = { 
                        message: "Could not complete the calendar operation. Please try again with different wording.",
                        error: "Multiple actions failed."
                    };
                    break;
                }
                
                // For Google Calendar specifically, try to use the "+" button if we can't find a custom selector
                if (actionToPerform.type === 'click' && 
                    actionToPerform.selector?.includes('create-event') && 
                    window.location.href.includes('calendar.google.com')) {
                    console.log("Trying fallback click on Google Calendar's + button");
                    await chrome.tabs.sendMessage(tab.id, {
                        action: 'clickElement',
                        selector: 'div[aria-label="Create"]'
                    });
                }
            } else {
                consecutiveFailedActions = 0; // Reset failed counter on success
            }

            // Wait for potential page updates/navigation
            let navigated = false;
            if (actionToPerform.type === 'navigate') {
                await waitForTabLoad(tab.id);
                navigated = true;
            } else if (['click', 'fill', 'select_option'].includes(actionToPerform.type)) {
                await new Promise(resolve => setTimeout(resolve, 1500)); // Wait for possible page changes
                const [updatedTab] = await chrome.tabs.query({ active: true, currentWindow: true });
                if (updatedTab && updatedTab.id === tab.id && updatedTab.url !== currentUrl) {
                    await waitForTabLoad(tab.id);
                    navigated = true;
                }
            }

            // If navigation happened, update tab info and URL
            if (navigated) {
                 const [finalTab] = await chrome.tabs.query({ active: true, currentWindow: true });
                 if (finalTab && finalTab.id === tab.id) {
                     currentUrl = finalTab.url;
                 } else {
                     console.warn("Tab changed or closed during action sequence.");
                     currentResult = { message: "Calendar operation interrupted." };
                     break;
                 }
            }

            // Get updated content after waiting/navigation
            currentContent = await getPageContent(tab.id);
            
            // Update previous action for loop detection
            previousAction = actionToPerform;

            // Call /next_action with the full history
            const nextResponse = await fetch(`${settings.apiUrl || API_BASE_URL}/next_action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: enrichedCommand,
                    url: currentUrl,
                    tabId: tab.id,
                    pageContent: currentContent,
                    actionHistory: actionHistory,
                    actionSuccess: actionSuccess, // Flag to indicate if the last action succeeded
                    context: {
                        type: 'calendar',
                        defaultDuration: settings.defaultDuration,
                        defaultReminder: settings.defaultReminder
                    }
                })
            });

            if (!nextResponse.ok) {
                throw new Error(`HTTP error on /next_action! status: ${nextResponse.status}`);
            }
            
            currentResult = await nextResponse.json();
            actionHistory.push(currentResult); // Add the new result to history
            
            // If the result indicates completion, add a friendly message
            if (currentResult && !currentResult.action) {
                if (!currentResult.message) {
                    if (command.toLowerCase().includes('schedule') || command.toLowerCase().includes('create')) {
                        currentResult.message = "Calendar event created successfully!";
                    } else if (command.toLowerCase().includes('update') || command.toLowerCase().includes('change') || command.toLowerCase().includes('move')) {
                        currentResult.message = "Calendar event updated successfully!";
                    } else if (command.toLowerCase().includes('delete') || command.toLowerCase().includes('cancel') || command.toLowerCase().includes('remove')) {
                        currentResult.message = "Calendar event deleted successfully!";
                    } else {
                        currentResult.message = "Calendar operation completed successfully!";
                    }
                }
            }
        }
        
        // Command sequence finished, return the last result
        return { success: true, result: currentResult };

    } catch (error) {
        console.error('Error executing calendar command:', error);
        const tabId = tab ? tab.id : 'unknown';
        console.error(`Error details: Command='${command}', TabID='${tabId}', Error='${error.message}'`);
        return { success: false, error: error.message };
    }
}

// Helper function to enrich calendar commands with additional context
function enrichCalendarCommand(command, settings) {
    // Add context about default duration or reminder if not specified in the command
    let enrichedCommand = command;
    
    // If command doesn't mention duration but is about creating an event
    if ((command.includes('schedule') || command.includes('create') || command.includes('set up')) && 
        !command.includes('hour') && !command.includes('minute') && !command.includes('hr')) {
        if (settings.defaultDuration === '30') {
            enrichedCommand += ' for 30 minutes';
        } else if (settings.defaultDuration === '60') {
            enrichedCommand += ' for 1 hour';
        } else {
            enrichedCommand += ` for ${settings.defaultDuration} minutes`;
        }
    }
    
    return enrichedCommand;
}

// Helper function to wait for a tab to finish loading
function waitForTabLoad(tabId) {
    return new Promise((resolve) => {
        const listener = (tabIdUpdated, changeInfo, tab) => {
            if (tabIdUpdated === tabId && changeInfo.status === 'complete') {
                chrome.tabs.onUpdated.removeListener(listener);
                resolve();
            }
        };
        chrome.tabs.onUpdated.addListener(listener);
        
        // Add a timeout to prevent waiting indefinitely
        setTimeout(() => {
            chrome.tabs.onUpdated.removeListener(listener);
            console.warn(`Timeout waiting for tab ${tabId} to load.`);
            resolve();
        }, 15000); // 15 seconds timeout
    });
}

async function getPageContent(tabId) {
    const MAX_RETRIES = 3;
    const RETRY_DELAY_MS = 500;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            // Check if tab exists and is loaded
            const tab = await chrome.tabs.get(tabId);
            if (tab.status !== 'complete') {
                if (attempt === MAX_RETRIES) {
                    console.warn(`Tab ${tabId} not loaded after ${MAX_RETRIES} attempts.`);
                    return '';
                }
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
                continue;
            }

            // Get page content
            const response = await chrome.tabs.sendMessage(tabId, { action: 'getPageInfo' });
            return response;
        } catch (error) {
            if (error.message.includes('Receiving end does not exist') || error.message.includes('Could not establish connection')) {
                if (attempt === MAX_RETRIES) {
                    console.error(`Error getting page content for tab ${tabId} after ${MAX_RETRIES} attempts`);
                    return '';
                }
                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
            } else {
                console.error(`Unexpected error getting page content for tab ${tabId}: ${error.message}`);
                return '';
            }
        }
    }
    return ''; 
}

async function performAction(action, tabId) {
    try {
        let result = false;
        switch (action.type) {
            case 'click':
                // Try the specified selector first
                result = await chrome.tabs.sendMessage(tabId, {
                    action: 'clickElement',
                    selector: action.selector
                });
                return result && result.success;
                
            case 'fill':
                result = await chrome.tabs.sendMessage(tabId, {
                    action: 'fillElement',
                    selector: action.selector,
                    value: action.value
                });
                return result && result.success;
                
            case 'navigate':
                await chrome.tabs.update(tabId, { url: action.url });
                return true; // Assume navigation success
                
            case 'extract':
                const response = await chrome.tabs.sendMessage(tabId, {
                    action: 'extractContent',
                    selector: action.selector
                });
                return response && response.content !== null;
                
            case 'select_option':
                result = await chrome.tabs.sendMessage(tabId, {
                    action: 'selectOption',
                    selector: action.selector,
                    value: action.value
                });
                return result && result.success;
                
            case 'press_key':
                result = await chrome.tabs.sendMessage(tabId, {
                    action: 'pressKey',
                    key: action.key
                });
                return result && result.success;
                
            case 'wait':
                await new Promise(resolve => setTimeout(resolve, action.milliseconds || 1000));
                return true;
                
            default:
                console.warn(`Unknown action type: ${action.type}`);
                return false;
        }
    } catch (error) {
        console.error(`Error performing calendar action ${action.type}:`, error);
        return false; // Return failure instead of throwing
    }
}

// Functions to be executed in the page context
function clickElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.click();
    }
}

function extractContent(selector) {
    const element = document.querySelector(selector);
    return element ? element.textContent : null;
} 