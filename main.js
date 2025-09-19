document.getElementById("scanBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileUpload");
  const urlInput = document.getElementById("mediaUrl").value;
  const loading = document.getElementById("loading");
  const resultBox = document.getElementById("result");
  const scoreSpan = document.getElementById("score");
  const metadataPre = document.getElementById("metadata");

  // Reset outputs and show loader
  loading.classList.remove("hidden");
  resultBox.classList.add("hidden");
  scoreSpan.textContent = "--";
  metadataPre.textContent = "--";
  document.getElementById("status-text").textContent = "";
  document.getElementById("status-icon").className = "status-icon";
  document.getElementById("progress-bar").style.width = "0";
  document.getElementById("ai-percent").textContent = "";

  try {
    let response, data;

    if (fileInput.files.length > 0) {
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formData
      });
    } else if (urlInput) {
      response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ url: urlInput })
      });
    } else {
      alert("Please upload a file or paste a URL.");
      loading.classList.add("hidden");
      return;
    }

    data = await response.json();
    displayResult(data);
  } catch (err) {
    scoreSpan.textContent = "Analysis Failed";
    metadataPre.textContent = "Error: " + err.message;
    document.getElementById("status-text").textContent = "Error Detected";
    document.getElementById("status-icon").className = "status-icon danger";
    document.getElementById("progress-bar").style.width = "0";
    document.getElementById("ai-percent").textContent = "";
  } finally {
    loading.classList.add("hidden");
    resultBox.classList.remove("hidden");
  }
});

function displayResult(data) {
  const scoreSpan = document.getElementById("score");
  const metadataPre = document.getElementById("metadata");
  const statusIcon = document.getElementById("status-icon");
  const statusText = document.getElementById("status-text");
  const progressBar = document.getElementById("progress-bar");
  const aiPercent = document.getElementById("ai-percent");

  // Show the result box
  document.getElementById("result").classList.remove("hidden");

  if (data.error) {
    scoreSpan.textContent = "Analysis Failed";
    metadataPre.textContent = "Error: " + data.error;
    statusText.textContent = "Error Detected";
    statusIcon.className = "status-icon danger";
    progressBar.style.width = "0";
    aiPercent.textContent = "";
    return;
  }

  const score = typeof data.score === "number" ? data.score : 0;
  const ai_usage = typeof data.ai_usage === "number" ? data.ai_usage : (100 - score);
  let status;
  if (score >= 75) {
    status = "Likely Authentic";
    statusIcon.className = "status-icon success";
    progressBar.style.background = "linear-gradient(90deg, #00ff88, #66fcf1)";
  } else if (score <= 40) {
    status = "Likely Fake";
    statusIcon.className = "status-icon danger";
    progressBar.style.background = "linear-gradient(90deg, #ff4d4d, #fcfcfc)";
  } else {
    status = "Inconclusive";
    statusIcon.className = "status-icon";
    progressBar.style.background = "linear-gradient(90deg, #ffc107, #66fcf1)";
  }

  scoreSpan.textContent = `${score}% Real`;
  aiPercent.textContent = `AI Usage: ${ai_usage}%`;
  progressBar.style.width = `${score}%`;

  statusText.textContent = status;
  metadataPre.textContent = JSON.stringify(data, null, 2);
}
