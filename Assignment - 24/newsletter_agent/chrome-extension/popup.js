document.addEventListener('DOMContentLoaded', function() {
    const commandInput = document.getElementById('commandInput');
    const executeButton = document.getElementById('executeButton');
    const statusDiv = document.getElementById('status');
    const commandHistory = document.getElementById('commandHistory');
    const settingsButton = document.getElementById('settingsButton');
    const examplesList = document.querySelector('.examples-section ul');

    // Load command history from storage
    chrome.storage.local.get(['commandHistory'], function(result) {
        if (result.commandHistory) {
            result.commandHistory.forEach(command => {
                addCommandToHistory(command);
            });
        }
    });

    // Load settings
    chrome.storage.local.get(['apiUrl'], function(result) {
        if (!result.apiUrl) {
            // Set default API URL if not set
            chrome.storage.local.set({ apiUrl: 'http://localhost:8000' });
        }
    });

    // Handle example commands
    if (examplesList) {
        examplesList.addEventListener('click', function(e) {
            if (e.target.tagName === 'LI') {
                commandInput.value = e.target.textContent;
                commandInput.focus();
            }
        });
    }

    executeButton.addEventListener('click', async function() {
        const command = commandInput.value.trim();
        if (!command) return;

        // Update status
        statusDiv.textContent = 'Processing calendar request...';
        statusDiv.style.color = '#2196F3';

        try {
            // Get settings to use with command
            const settings = await getSettings();
            
            // Check if confirmation is required before proceeding
            if (settings.confirmBeforeAction) {
                if (!confirm(`Execute calendar command: "${command}"?`)) {
                    statusDiv.textContent = 'Command cancelled';
                    statusDiv.style.color = '#555';
                    return;
                }
            }

            // Send command to background script
            const response = await chrome.runtime.sendMessage({
                action: 'executeCommand',
                command: command,
                targetSite: 'calendar.google.com',
                settings: settings
            });

            // Update status based on response
            if (response.success) {
                statusDiv.textContent = response.result && response.result.message ? 
                    response.result.message : 'Calendar updated successfully!';
                statusDiv.style.color = '#4CAF50';
                
                // Clear input if auto-clear is enabled
                if (settings.autoClearInput) {
                    commandInput.value = '';
                }

                // Add command to history
                addCommandToHistory(command);
                saveCommandToHistory(command);
            } else {
                statusDiv.textContent = 'Error: ' + (response.error || 'Unknown error occurred');
                statusDiv.style.color = '#f44336';
            }
        } catch (error) {
            statusDiv.textContent = 'Error: ' + error.message;
            statusDiv.style.color = '#f44336';
        }
    });

    // Handle command history clicks
    commandHistory.addEventListener('click', function(e) {
        if (e.target.tagName === 'LI') {
            commandInput.value = e.target.textContent;
        }
    });

    // Settings button click handler
    settingsButton.addEventListener('click', function() {
        chrome.runtime.openOptionsPage();
    });

    function addCommandToHistory(command) {
        const li = document.createElement('li');
        li.textContent = command;
        commandHistory.insertBefore(li, commandHistory.firstChild);
    }

    function saveCommandToHistory(command) {
        chrome.storage.local.get(['commandHistory'], function(result) {
            const history = result.commandHistory || [];
            history.unshift(command);
            // Keep only last 10 commands
            if (history.length > 10) {
                history.pop();
            }
            chrome.storage.local.set({ commandHistory: history });
        });
    }

    // Get all settings from storage
    async function getSettings() {
        return new Promise((resolve) => {
            chrome.storage.local.get([
                'apiUrl', 
                'defaultDuration', 
                'defaultReminder', 
                'autoClearInput',
                'confirmBeforeAction'
            ], function(result) {
                resolve({
                    apiUrl: result.apiUrl || 'http://localhost:8000',
                    defaultDuration: result.defaultDuration || '30',
                    defaultReminder: result.defaultReminder || '30',
                    autoClearInput: result.autoClearInput !== false, // Default to true
                    confirmBeforeAction: result.confirmBeforeAction !== false // Default to true
                });
            });
        });
    }
}); 