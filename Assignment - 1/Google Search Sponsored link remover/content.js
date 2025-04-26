let observer = null;

function removeSponsoredLinks() {
  const sponsoredElements = document.querySelectorAll('div[data-text-ad="1"]');
  sponsoredElements.forEach(element => element.remove());
}

function startObserver() {
  if (!observer) {
    observer = new MutationObserver(removeSponsoredLinks);
    observer.observe(document.body, { childList: true, subtree: true });
  }
}

function stopObserver() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
}

function updateExtensionState(enabled) {
  if (enabled) {
    removeSponsoredLinks();
    startObserver();
  } else {
    stopObserver();
  }
}

chrome.storage.sync.get('enabled', ({ enabled }) => {
  updateExtensionState(enabled);
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'toggleExtension') {
    updateExtensionState(request.enabled);
  }
});
