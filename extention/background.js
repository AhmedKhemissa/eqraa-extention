// background.js
console.log("Service Worker: Started");

// Create context menu once during installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyze-arabic",
    title: "تحليل الكلمة العربية",
    contexts: ["selection"],
  });
});

// Handle text selection changes
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyze-arabic") {
    const selectedText = info.selectionText.trim();
    chrome.storage.local.set({ selectedWord: selectedText }, () => {
      chrome.action.openPopup();
    });
  }
});

// Update menu visibility based on selection
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SELECTION_CHANGED") {
    const hasArabic = /[\u0600-\u06FF]/.test(message.text);
    chrome.contextMenus.update("analyze-arabic", {
      visible: hasArabic,
    });
  }
  return true;
});
