// content-script.js
let lastSelection = "";
let messageQueue = [];
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Enhanced Chrome API check with fallback
const isChromeAvailable = () => {
  try {
    return (
      typeof chrome !== "undefined" &&
      typeof chrome.runtime?.sendMessage === "function" &&
      chrome.runtime?.id
    );
  } catch (e) {
    return false;
  }
};

// Safe message sender with error boundaries
const sendMessageToRuntime = async (message) => {
  if (!isChromeAvailable()) {
    console.warn("Chrome API not available - running in non-extension context");
    return false;
  }

  try {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          console.log("Extension error:", chrome.runtime.lastError);
          resolve(false);
        } else {
          resolve(true);
        }
      });
    });
  } catch (error) {
    console.error("Critical runtime error:", error);
    return false;
  }
};

// Selection handler with debouncing
const handleSelection = async (selection) => {
  if (selection && selection !== lastSelection) {
    lastSelection = selection;
    if (isChromeAvailable()) {
      await sendMessageToRuntime({
        type: "SELECTION_CHANGED",
        text: selection,
      });
    }
  }
};

// Initialize only in extension context
if (isChromeAvailable()) {
  document.addEventListener("mouseup", () => {
    const selection = window.getSelection().toString().trim();
    handleSelection(selection);
  });

  document.addEventListener("mousedown", () => {
    if (!window.getSelection().toString().trim()) {
      lastSelection = "";
      handleSelection("");
    }
  });
} else {
  console.warn("Content script loaded in non-extension context");
}
