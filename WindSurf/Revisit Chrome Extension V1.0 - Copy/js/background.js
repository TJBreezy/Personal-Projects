// Initialize extension data when installed
chrome.runtime.onInstalled.addListener(() => {
    // Set up initial storage with default categories
    chrome.storage.local.get(['categories', 'links'], (result) => {
        if (!result.categories) {
            chrome.storage.local.set({
                categories: ['General', 'Work', 'Personal'],
                links: {}
            });
        }
    });
});
