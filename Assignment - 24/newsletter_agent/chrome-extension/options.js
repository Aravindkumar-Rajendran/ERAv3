document.addEventListener('DOMContentLoaded', function() {
    const apiUrlInput = document.getElementById('apiUrl');
    const defaultDurationSelect = document.getElementById('defaultDuration');
    const defaultReminderSelect = document.getElementById('defaultReminder');
    const autoClearInputCheckbox = document.getElementById('autoClearInput');
    const confirmBeforeActionCheckbox = document.getElementById('confirmBeforeAction');
    const saveButton = document.getElementById('saveButton');

    // Load saved settings
    chrome.storage.local.get([
        'apiUrl', 
        'defaultDuration', 
        'defaultReminder', 
        'autoClearInput',
        'confirmBeforeAction'
    ], function(result) {
        if (result.apiUrl) {
            apiUrlInput.value = result.apiUrl;
        } else {
            apiUrlInput.value = 'http://localhost:8000';
        }

        if (result.defaultDuration) {
            defaultDurationSelect.value = result.defaultDuration;
        }

        if (result.defaultReminder) {
            defaultReminderSelect.value = result.defaultReminder;
        }

        if (result.autoClearInput !== undefined) {
            autoClearInputCheckbox.checked = result.autoClearInput;
        }

        if (result.confirmBeforeAction !== undefined) {
            confirmBeforeActionCheckbox.checked = result.confirmBeforeAction;
        }
    });

    // Save settings
    saveButton.addEventListener('click', function() {
        chrome.storage.local.set({
            apiUrl: apiUrlInput.value,
            defaultDuration: defaultDurationSelect.value,
            defaultReminder: defaultReminderSelect.value,
            autoClearInput: autoClearInputCheckbox.checked,
            confirmBeforeAction: confirmBeforeActionCheckbox.checked
        }, function() {
            // Show save confirmation
            const saveButton = document.getElementById('saveButton');
            const originalText = saveButton.textContent;
            saveButton.textContent = 'Settings Saved!';
            saveButton.disabled = true;
            
            setTimeout(function() {
                saveButton.textContent = originalText;
                saveButton.disabled = false;
            }, 1500);
        });
    });
}); 