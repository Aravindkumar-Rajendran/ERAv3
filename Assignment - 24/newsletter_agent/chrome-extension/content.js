// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    try {
        if (request.action === 'getPageInfo') {
            const pageInfo = document.documentElement.outerHTML;
            sendResponse(pageInfo);
        } else if (request.action === 'clickElement') {
            const result = clickElement(request.selector);
            sendResponse({ success: result });
        } else if (request.action === 'extractContent') {
            const content = extractContent(request.selector);
            sendResponse({ content: content });
        } else if (request.action === 'fillElement') {
            const result = fillElement(request.selector, request.value);
            sendResponse({ success: result });
        } else if (request.action === 'selectOption') {
            const result = selectOption(request.selector, request.value);
            sendResponse({ success: result });
        } else if (request.action === 'pressKey') {
            const result = pressKey(request.key);
            sendResponse({ success: result });
        }
    } catch (error) {
        // Ignore Google Sign-In and FedCM related errors
        if (!error.message.includes('GSI') && !error.message.includes('FedCM')) {
            console.error('Content script error:', error);
        }
        sendResponse({ error: error.message });
    }
    return true;
});

// Function to get element information
function getElementInfo(element) {
    return {
        tagName: element.tagName,
        id: element.id,
        className: element.className,
        text: element.textContent,
        xpath: getXPath(element)
    };
}

// Helper function to get XPath of an element
function getXPath(element) {
    if (element.id) {
        return `//*[@id="${element.id}"]`;
    }
    if (element === document.body) {
        return '/html/body';
    }

    let ix = 1;
    const siblings = element.parentNode.childNodes;

    for (let sibling of siblings) {
        if (sibling === element) {
            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + ix + ']';
        }
        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
            ix++;
        }
    }
}

// Function to click an element with Google Calendar-specific handling
function clickElement(selector) {
    try {
        // Check if we're in Google Calendar
        const isGoogleCalendar = window.location.href.includes('calendar.google.com');
        
        // Directly handle common Google Calendar actions with better selectors
        if (isGoogleCalendar) {
            // Handle common Google Calendar selectors
            if (selector === '.create-event-button' || selector.includes('create-event')) {
                console.log('Using Google Calendar specific selectors for create event');
                
                // Try these selectors in order
                const createButtonSelectors = [
                    'div[aria-label="Create"]', // Main create button
                    'div[aria-label="Create event"]', // Alternative label
                    'button[aria-label="Create"]', // Button variant
                    'div[role="button"][data-tooltip="Create"]', // Old UI tooltip
                    '.fab.createEventButton', // Old UI class
                    // Try finding buttons with + symbol
                    'div[role="button"] > span:contains("+")',
                    // Most generic - any element containing "Create" text
                    'div[role="button"]:contains("Create")'
                ];
                
                // Try each selector
                for (const createSelector of createButtonSelectors) {
                    const element = findElementBySelector(createSelector);
                    if (element) {
                        element.click();
                        return true;
                    }
                }
            }
        }
        
        // Fall back to regular selector
        const element = document.querySelector(selector);
        if (element) {
            element.click();
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Error clicking element:', error);
        return false;
    }
}

// Helper function to find elements using different strategies
function findElementBySelector(selector) {
    try {
        // Try standard querySelector first
        let element = document.querySelector(selector);
        if (element) return element;
        
        // For :contains pseudo-selector (jQuery-like)
        if (selector.includes(':contains(')) {
            const parts = selector.split(':contains(');
            const baseSelector = parts[0];
            const searchText = parts[1].slice(0, -1); // remove closing parenthesis
            
            const elements = document.querySelectorAll(baseSelector);
            for (const el of elements) {
                if (el.textContent.includes(searchText)) {
                    return el;
                }
            }
        }
        
        // Try by aria-label
        if (selector.includes('aria-label=')) {
            const label = selector.match(/aria-label="([^"]*)"/)[1];
            return document.querySelector(`[aria-label="${label}"]`);
        }
        
        // Try by role and text content
        if (selector.includes('role=') && selector.includes('text=')) {
            const role = selector.match(/role="([^"]*)"/)[1];
            const text = selector.match(/text="([^"]*)"/)[1];
            const elements = document.querySelectorAll(`[role="${role}"]`);
            for (const el of elements) {
                if (el.textContent.includes(text)) {
                    return el;
                }
            }
        }
        
        return null;
    } catch (e) {
        console.error('Error in findElementBySelector:', e);
        return null;
    }
}

// Function to extract content from an element
function extractContent(selector) {
    try {
        const element = document.querySelector(selector);
        return element ? element.textContent : null;
    } catch (error) {
        console.error('Error extracting content:', error);
        return null;
    }
}

// Function to fill an element
function fillElement(selector, value) {
    try {
        const element = document.querySelector(selector);
        if (element && (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {
            element.value = value;
            // Dispatch input/change events for reactivity
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            
            // For Google Calendar's special inputs, also trigger blur event
            if (window.location.href.includes('calendar.google.com')) {
                element.dispatchEvent(new Event('blur', { bubbles: true }));
                
                // For Google Calendar, sometimes we need to wait and press Enter to confirm the input
                setTimeout(() => {
                    element.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    }));
                }, 500);
            }
            
            return true;
        }
        
        // For divs that act as contenteditable fields
        if (element && element.getAttribute('contenteditable') === 'true') {
            element.textContent = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Error filling element:', error);
        return false;
    }
}

// Function to select an option from a dropdown
function selectOption(selector, value) {
    try {
        const element = document.querySelector(selector);
        if (element && element.tagName === 'SELECT') {
            // Set the value
            element.value = value;
            
            // Dispatch change event
            element.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        
        // Handle Google Calendar's custom dropdowns which are often divs with role="listbox"
        if (element && (element.getAttribute('role') === 'listbox' || element.getAttribute('role') === 'combobox')) {
            // Click to open the dropdown
            element.click();
            
            // Wait a bit for the dropdown to open
            setTimeout(() => {
                // Find the option with the matching text
                const options = document.querySelectorAll('[role="option"]');
                for (const option of options) {
                    if (option.textContent.toLowerCase().includes(value.toLowerCase())) {
                        option.click();
                        return;
                    }
                }
                
                // If no match found, try more generic options that might exist in calendar
                const allOptions = document.querySelectorAll('[role="menuitem"], [role="option"], li');
                for (const option of allOptions) {
                    if (option.textContent.toLowerCase().includes(value.toLowerCase())) {
                        option.click();
                        return;
                    }
                }
            }, 500);
            
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('Error selecting option:', error);
        return false;
    }
}

// Function to press a key
function pressKey(key) {
    try {
        // Create and dispatch keyboard event
        const event = new KeyboardEvent('keydown', {
            key: key,
            code: `Key${key.toUpperCase()}`,
            keyCode: key.charCodeAt(0),
            which: key.charCodeAt(0),
            bubbles: true,
            cancelable: true
        });
        
        // Send to active element (usually focused input)
        document.activeElement.dispatchEvent(event);
        
        // Also try Enter key for submission if key is 'Enter'
        if (key === 'Enter') {
            const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true,
                cancelable: true
            });
            document.activeElement.dispatchEvent(enterEvent);
        }
        
        return true;
    } catch (error) {
        console.error('Error pressing key:', error);
        return false;
    }
} 