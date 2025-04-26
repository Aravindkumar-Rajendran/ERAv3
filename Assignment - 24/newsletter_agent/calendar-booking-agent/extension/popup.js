document.addEventListener('DOMContentLoaded', () => {
  const queryInput = document.getElementById('query-input');
  const submitBtn = document.getElementById('submit-btn');
  const statusMessage = document.getElementById('status-message');
  const loadingSpinner = document.getElementById('loading-spinner');
  const resultArea = document.getElementById('result-area');
  const eventDetails = document.getElementById('event-details');
  const historyList = document.getElementById('history-list');

  // Load history from storage
  loadHistory();

  submitBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();
    
    if (!query) {
      statusMessage.textContent = 'Please enter a calendar request.';
      return;
    }
    
    try {
      // Show loading state
      startLoading('Processing your request...');
      
      // Send the query to the backend
      const response = await sendQueryToBackend(query);
      
      if (!response.result) {
        throw new Error('Invalid response from server');
      }
      
      // Save to history
      saveToHistory(query);
      
      // Display the extracted event details
      displayEventDetails(response.result);
      
      // Send action to background script to execute in Google Calendar
      chrome.runtime.sendMessage({
        type: 'execute-calendar-action',
        action: response.result
      }, (response) => {
        if (response && response.success) {
          updateStatus('Successfully processed your request!');
        } else {
          updateStatus('Error: ' + (response?.error || 'Unknown error occurred'));
        }
      });
      
    } catch (error) {
      console.error('Error processing query:', error);
      updateStatus(`Error: ${error.message}`);
    } finally {
      stopLoading();
    }
  });

  // Handle clicks on history items
  historyList.addEventListener('click', (event) => {
    if (event.target.tagName === 'LI') {
      queryInput.value = event.target.textContent;
    }
  });

  /**
   * Send query to backend server
   */
  async function sendQueryToBackend(query) {
    // Get backend URL from storage
    const { backendUrl } = await chrome.storage.sync.get({
      backendUrl: 'http://localhost:3025'
    });
    
    const response = await fetch(`${backendUrl}/process-query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error: ${response.status} ${errorText}`);
    }
    
    return await response.json();
  }

  /**
   * Display extracted event details in the UI
   */
  function displayEventDetails(result) {
    const { context } = result;
    
    if (!context) {
      return;
    }
    
    // Clear previous details
    eventDetails.innerHTML = '';
    
    // Add event details
    const fields = [
      { label: 'Event Type', value: result.actionType },
      { label: 'Title', value: context.summary },
      { label: 'Date', value: context.startDate },
      { label: 'Time', value: `${context.startTime || ''} ${context.endTime ? '- ' + context.endTime : ''}` },
      { label: 'Location', value: context.location },
      { label: 'Description', value: context.description },
      { label: 'Attendees', value: context.attendees?.join(', ') }
    ];
    
    fields.forEach(field => {
      if (field.value) {
        const row = document.createElement('div');
        row.innerHTML = `<strong>${field.label}:</strong>`;
        
        const valueDiv = document.createElement('div');
        valueDiv.textContent = field.value;
        
        eventDetails.appendChild(row);
        eventDetails.appendChild(valueDiv);
      }
    });
    
    // Show the result area
    resultArea.classList.remove('hidden');
  }

  /**
   * Save query to history
   */
  function saveToHistory(query) {
    chrome.storage.local.get({ history: [] }, (data) => {
      let history = data.history;
      
      // Remove duplicate if exists
      history = history.filter(item => item !== query);
      
      // Add to beginning of array
      history.unshift(query);
      
      // Limit to 10 items
      if (history.length > 10) {
        history = history.slice(0, 10);
      }
      
      // Save back to storage
      chrome.storage.local.set({ history });
      
      // Update the UI
      loadHistory();
    });
  }

  /**
   * Load history from storage and display in UI
   */
  function loadHistory() {
    chrome.storage.local.get({ history: [] }, (data) => {
      historyList.innerHTML = '';
      
      if (data.history.length === 0) {
        const emptyItem = document.createElement('li');
        emptyItem.textContent = 'No recent requests';
        emptyItem.style.cursor = 'default';
        historyList.appendChild(emptyItem);
        return;
      }
      
      data.history.forEach(query => {
        const item = document.createElement('li');
        item.textContent = query;
        historyList.appendChild(item);
      });
    });
  }

  /**
   * Start loading state
   */
  function startLoading(message) {
    statusMessage.textContent = message;
    loadingSpinner.classList.remove('hidden');
    submitBtn.disabled = true;
  }

  /**
   * Stop loading state
   */
  function stopLoading() {
    loadingSpinner.classList.add('hidden');
    submitBtn.disabled = false;
  }

  /**
   * Update status message
   */
  function updateStatus(message) {
    statusMessage.textContent = message;
  }
}); 