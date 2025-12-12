const apiUrlInput = document.getElementById("apiUrl");
const textInput = document.getElementById("textInput");
const submitBtn = document.getElementById("submitBtn");
const resultEl = document.getElementById("result");
const statusEl = document.getElementById("status");

function setStatus(message, kind = "info") {
  statusEl.textContent = message;
  statusEl.className = `status ${kind}`;
}

function setResult(content) {
  resultEl.innerHTML = content;
}

function getApiBase() {
  const fromInput = apiUrlInput.value.trim();
  if (fromInput) return fromInput;
  if (window.API_BASE_URL) return window.API_BASE_URL;
  return "";
}

async function classify(text) {
  const apiBase = getApiBase();
  if (!apiBase) {
    throw new Error("Enter the API base URL (api_endpoint output).");
  }

  const url = `${apiBase.replace(/\/+$/, "")}/classify`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`API error ${resp.status}: ${detail}`);
  }
  return resp.json();
}

async function onSubmit() {
  const text = textInput.value.trim();
  if (!text) {
    setStatus("Please enter some text.", "error");
    return;
  }

  setStatus("Calling API...", "info");
  setResult("");
  submitBtn.disabled = true;

  try {
    const data = await classify(text);
    const flag = Boolean(data.has_cognitive_distortion);
    setStatus("Success", "success");
    setResult(
      `<div class="badge ${flag ? "bad" : "good"}">` +
        (flag ? "Cognitive distortion detected" : "No distortion detected") +
      "</div>" +
      `<pre>${JSON.stringify(data, null, 2)}</pre>`
    );
  } catch (err) {
    setStatus(err.message || "Unexpected error", "error");
  } finally {
    submitBtn.disabled = false;
  }
}

submitBtn.addEventListener("click", onSubmit);

document.querySelectorAll(".pill").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    textInput.value = e.target.dataset.text || "";
    textInput.focus();
  });
});

