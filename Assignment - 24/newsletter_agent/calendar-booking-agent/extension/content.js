// Utilities for navigating and interacting with Google Calendar UI
const calendarHelper = {
  // Wait for an element to be present in the DOM
  async waitForElement(selector, timeout = 10000) {
    return new Promise((resolve, reject) => {
      if (document.querySelector(selector)) {
        return resolve(document.querySelector(selector));
      }

      const observer = new MutationObserver(mutations => {
        if (document.querySelector(selector)) {
          observer.disconnect();
          resolve(document.querySelector(selector));
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });

      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Timeout waiting for element: ${selector}`));
      }, timeout);
    });
  },

  // Take a snapshot of the current page accessibility tree
  async takeSnapshot() {
    // Simple function to convert DOM tree to accessibility snapshot
    const processNode = (node, nodeId = 1) => {
      if (!node || node.nodeType !== Node.ELEMENT_NODE) return null;
      
      const nodeName = node.nodeName.toLowerCase();
      const id = node.id ? `#${node.id}` : '';
      const classes = Array.from(node.classList || []).map(c => `.${c}`).join('');
      const selector = nodeName + id + classes;
      
      const isVisible = !(node.offsetHeight === 0 && node.offsetWidth === 0);
      if (!isVisible) return null;
      
      const role = node.getAttribute('role') || nodeName;
      const text = node.innerText?.trim() || '';
      const ariaLabel = node.getAttribute('aria-label') || '';
      const title = node.getAttribute('title') || '';
      const accessibleName = ariaLabel || title || text;
      
      const result = {
        ref: `node-${nodeId}`, 
        role,
        name: accessibleName,
        selector
      };
      
      if (node.children && node.children.length > 0) {
        let childId = nodeId * 100;
        const children = [];
        for (const child of node.children) {
          const childNode = processNode(child, childId++);
          if (childNode) {
            children.push(childNode);
          }
        }
        if (children.length > 0) {
          result.children = children;
        }
      }
      
      return result;
    };
    
    return processNode(document.body);
  },

  // Find element by name and role from snapshot
  findElement(snapshot, namePattern, role = null) {
    if (!snapshot) return null;
    
    // Check if current node matches
    if (snapshot.name && 
        (namePattern instanceof RegExp ? namePattern.test(snapshot.name) : snapshot.name.includes(namePattern)) &&
        (!role || snapshot.role === role)) {
      return snapshot;
    }
    
    // Search in children
    if (snapshot.children) {
      for (const child of snapshot.children) {
        const result = this.findElement(child, namePattern, role);
        if (result) return result;
      }
    }
    
    return null;
  },

  // Get element by ref from snapshot
  getElementByRef(ref) {
    const snapshot = this._lastSnapshot;
    if (!snapshot) return null;
    
    const findByRef = (node, targetRef) => {
      if (!node) return null;
      
      if (node.ref === targetRef) {
        return document.querySelector(node.selector);
      }
      
      if (node.children) {
        for (const child of node.children) {
          const result = findByRef(child, targetRef);
          if (result) return result;
        }
      }
      
      return null;
    };
    
    return findByRef(snapshot, ref);
  },

  // Click on calendar date grid to create new event
  async clickOnDateGrid(date) {
    // Handle clicking on the date grid to create a new event
    const dateCell = await this.waitForElement(`[data-date="${date}"]`);
    if (dateCell) {
      dateCell.click();
      return true;
    }
    return false;
  },
  
  // Store last snapshot for reference
  _lastSnapshot: null
};

// Handle step execution
async function executeStep(step) {
  console.log('Executing step:', step);
  
  try {
    const { tool, parameters } = step;
    
    switch (tool) {
      case 'mcp_browser_navigate':
        return await handleNavigate(parameters);
        
      case 'mcp_browser_click':
        return await handleClick(parameters);
        
      case 'mcp_browser_type':
        return await handleType(parameters);
        
      case 'mcp_browser_select_option':
        return await handleSelectOption(parameters);
        
      case 'mcp_browser_wait':
        return await handleWait(parameters);
        
      case 'mcp_browser_snapshot':
        return await handleSnapshot();
        
      default:
        throw new Error(`Unknown tool: ${tool}`);
    }
  } catch (error) {
    console.error('Error executing step:', error);
    return { success: false, error: error.message };
  }
}

// Handle navigation to a URL
async function handleNavigate(parameters) {
  const { url } = parameters;
  
  if (!url) {
    throw new Error('URL is required for navigation');
  }
  
  // For content script, we can't navigate directly, so we'll return success
  // and let the background script handle actual navigation
  return { success: true, message: `Ready to navigate to ${url}` };
}

// Handle clicking on an element
async function handleClick(parameters) {
  const { ref, element } = parameters;
  
  if (!ref) {
    throw new Error('Element reference is required for clicking');
  }
  
  // Take snapshot if we don't have one yet
  if (!calendarHelper._lastSnapshot) {
    await handleSnapshot();
  }
  
  // Find the element by ref
  const domElement = calendarHelper.getElementByRef(ref);
  
  if (!domElement) {
    throw new Error(`Element not found: ${element || ref}`);
  }
  
  // Click the element
  domElement.click();
  
  return { success: true, message: `Clicked on ${element || ref}` };
}

// Handle typing into an element
async function handleType(parameters) {
  const { ref, element, text, submit } = parameters;
  
  if (!ref) {
    throw new Error('Element reference is required for typing');
  }
  
  if (!text) {
    throw new Error('Text is required for typing');
  }
  
  // Take snapshot if we don't have one yet
  if (!calendarHelper._lastSnapshot) {
    await handleSnapshot();
  }
  
  // Find the element by ref
  const domElement = calendarHelper.getElementByRef(ref);
  
  if (!domElement) {
    throw new Error(`Element not found: ${element || ref}`);
  }
  
  // Focus and clear the input
  domElement.focus();
  domElement.value = '';
  
  // Type the text
  domElement.value = text;
  
  // Dispatch input event to trigger any listeners
  domElement.dispatchEvent(new Event('input', { bubbles: true }));
  
  // Handle form submission if requested
  if (submit) {
    domElement.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
    domElement.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', bubbles: true }));
    domElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', bubbles: true }));
  }
  
  return { success: true, message: `Typed "${text}" into ${element || ref}` };
}

// Handle selecting an option from a dropdown
async function handleSelectOption(parameters) {
  const { ref, element, values } = parameters;
  
  if (!ref) {
    throw new Error('Element reference is required for selecting options');
  }
  
  if (!values || !Array.isArray(values) || values.length === 0) {
    throw new Error('Values array is required for selecting options');
  }
  
  // Take snapshot if we don't have one yet
  if (!calendarHelper._lastSnapshot) {
    await handleSnapshot();
  }
  
  // Find the element by ref
  const domElement = calendarHelper.getElementByRef(ref);
  
  if (!domElement) {
    throw new Error(`Element not found: ${element || ref}`);
  }
  
  if (domElement.tagName.toLowerCase() === 'select') {
    // Standard select element
    Array.from(domElement.options).forEach(option => {
      option.selected = values.includes(option.value) || values.includes(option.text);
    });
    
    // Dispatch change event
    domElement.dispatchEvent(new Event('change', { bubbles: true }));
  } else {
    // Custom dropdown - click to open, then find and click the option
    domElement.click();
    
    // Wait for dropdown items to appear
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Take a new snapshot to include dropdown options
    await handleSnapshot();
    
    // Find and click the option
    const optionPattern = new RegExp(values[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
    const optionEl = calendarHelper.findElement(calendarHelper._lastSnapshot, optionPattern);
    
    if (optionEl) {
      const optionDomEl = calendarHelper.getElementByRef(optionEl.ref);
      if (optionDomEl) {
        optionDomEl.click();
      } else {
        throw new Error(`Option element DOM node not found: ${values[0]}`);
      }
    } else {
      throw new Error(`Option not found: ${values[0]}`);
    }
  }
  
  return { success: true, message: `Selected option(s) ${values.join(', ')} in ${element || ref}` };
}

// Handle waiting for a specified time
async function handleWait(parameters) {
  const { time } = parameters;
  
  if (!time || isNaN(time)) {
    throw new Error('Time (in seconds) is required for waiting');
  }
  
  await new Promise(resolve => setTimeout(resolve, time * 1000));
  
  return { success: true, message: `Waited for ${time} seconds` };
}

// Handle taking a snapshot of the page
async function handleSnapshot() {
  try {
    const snapshot = await calendarHelper.takeSnapshot();
    calendarHelper._lastSnapshot = snapshot;
    return { success: true, snapshot };
  } catch (error) {
    throw new Error(`Failed to take snapshot: ${error.message}`);
  }
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'execute-step') {
    executeStep(request.step)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    // Return true to indicate we'll send a response asynchronously
    return true;
  }
});

// Initialize when the page loads
window.addEventListener('load', async () => {
  console.log('Calendar Booking Agent content script loaded');
  
  // Take initial snapshot
  try {
    await handleSnapshot();
    console.log('Initial snapshot taken');
  } catch (error) {
    console.error('Failed to take initial snapshot:', error);
  }
}); 