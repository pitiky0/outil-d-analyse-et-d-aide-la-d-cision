// Select individual buttons with more specific selectors
const pcrSubmitButton = document.getElementById("submit-pcr");
const dfcSubmitButton = document.getElementById("submit-dfc");
const reviewHistoryButton = document.getElementById("review-history");
const dictionnaireButton = document.getElementById("dictionnaire-button");

// Attach separate event listeners to each button
pcrSubmitButton.addEventListener("click", handlePCRSubmit);
dfcSubmitButton.getElementById("click", handleDFCSubmit);
reviewHistoryButton.addEventListener("click", handleReviewHistory);
dictionnaireButton.addEventListener("click", handleDictionnaire);

// Define button click handlers (replace placeholders with actual logic)
function handlePCRSubmit() {
  // Code to handle PCR submission
  alert("PCR submission triggered!");
}

function handleDFCSubmit() {
  // Code to handle DFC submission
  alert("DFC submission triggered!");
}

function handleReviewHistory() {
  // Code to handle review history
  alert("Review history triggered!");
}

function handleDictionnaire() {
  window.location.href = this.dataset.href;
}
