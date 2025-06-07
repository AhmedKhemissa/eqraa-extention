const elements = {
  loading: document.getElementById("loading"),
  results: document.getElementById("results"),
  error: document.getElementById("error"),
  retryBtn: document.getElementById("retry-btn"),
  wordDisplay: document.getElementById("word-display"),
  cefrLevel: document.getElementById("cefr-level"),
  partOfSpeech: document.getElementById("part-of-speech"),
  lemma: document.getElementById("lemma"),
  definition: document.getElementById("definition"),
  field: document.getElementById("field"),
  synonyms: document.getElementById("synonyms"),
  antonyms: document.getElementById("antonyms"),
  example: document.getElementById("example"),
  context: document.getElementById("context"),
  tabButtons: document.querySelectorAll(".tab-btn"),
  tabPanes: document.querySelectorAll(".tab-pane"),
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const { selectedWord } = await chrome.storage.local.get("selectedWord");
    if (!selectedWord) {
      throw new Error("لم يتم اختيار كلمة");
    }

    showLoading();
    const analysis = await fetchAnalysis(selectedWord);
    updateUI(analysis.data);
    showResults();

    // Set up tab switching
    setupTabs();
  } catch (error) {
    handleError(error.message);
  }
});

// Set up tab switching functionality
function setupTabs() {
  elements.tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons and panes
      elements.tabButtons.forEach((btn) => btn.classList.remove("active"));
      elements.tabPanes.forEach((pane) => pane.classList.remove("active"));

      // Add active class to current button and corresponding pane
      button.classList.add("active");
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });
}

elements.retryBtn?.addEventListener("click", () => {
  window.location.reload();
});

async function fetchAnalysis(word) {
  const response = await fetch("http://localhost:5000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word }),
  });

  if (!response.ok) throw new Error("فشل الاتصال بالخادم");
  return await response.json();
}

function updateUI(data) {
  if (!data || !data.Word) {
    throw new Error("بيانات غير صالحة");
  }

  elements.wordDisplay.textContent = data.Word;
  elements.cefrLevel.textContent = data["CEFR Level"];
  elements.field.textContent = data.Field;
  elements.partOfSpeech.textContent = data["Part of Speech"];
  elements.lemma.textContent = data.Lemma;
  elements.definition.textContent = data.Definition;
  elements.synonyms.textContent = data.Synonyms;
  elements.antonyms.textContent = data.Antonyms;
  elements.example.textContent = data["Phrase Example"];
  elements.context.textContent = data.Context;
}

function showLoading() {
  elements.loading.classList.remove("hidden");
  elements.results.classList.add("hidden");
  elements.error.classList.add("hidden");
}

function showResults() {
  elements.loading.classList.add("hidden");
  elements.results.classList.remove("hidden");
}

function handleError(message) {
  elements.loading.classList.add("hidden");
  elements.results.classList.add("hidden");
  elements.error.classList.remove("hidden");
  elements.error.querySelector("p").textContent = `⚠️ ${message}`;
}
