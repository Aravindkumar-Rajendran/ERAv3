document.addEventListener('DOMContentLoaded', () => {
  const toggleCheckbox = document.getElementById('toggleExtension');
  const applyButton = document.getElementById('applyChanges');

  chrome.storage.sync.get('enabled', ({ enabled }) => {
    toggleCheckbox.checked = enabled;
  });

  applyButton.addEventListener('click', () => {
    const enabled = toggleCheckbox.checked;
    chrome.storage.sync.set({ enabled }, () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'toggleExtension', enabled });
        chrome.tabs.reload(tabs[0].id);
      });
    });
  });
});
