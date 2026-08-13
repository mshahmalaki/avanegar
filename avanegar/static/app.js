const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const state = {
  file: null,
  job: null,
  result: null,
  mediaRecorder: null,
  recordingChunks: [],
  recordingStartedAt: null,
  recordingTimer: null,
  activeView: "segments",
  capabilities: null,
};

const elements = {
  uploadView: $("#uploadView"),
  selectedView: $("#selectedView"),
  processingView: $("#processingView"),
  resultPanel: $("#resultPanel"),
  dropZone: $("#dropZone"),
  fileInput: $("#fileInput"),
  fileName: $("#fileName"),
  fileMeta: $("#fileMeta"),
  engineState: $("#engineState"),
  recordButton: $("#recordButton"),
  recordLabel: $("#recordLabel"),
  recordTime: $("#recordTime"),
  startButton: $("#startButton"),
  processingStage: $("#processingStage"),
  processingFile: $("#processingFile"),
  progressValue: $("#progressValue"),
  progressLabel: $("#progressLabel"),
  transcriptContent: $("#transcriptContent"),
  resultSummary: $("#resultSummary"),
  warningBanner: $("#warningBanner"),
  warningText: $("#warningText"),
  toast: $("#toast"),
};

const faNumber = new Intl.NumberFormat("fa-IR");

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("show");
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => elements.toast.classList.remove("show"), 2600);
}

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${faNumber.format(Math.ceil(bytes / 1024))} کیلوبایت`;
  return `${faNumber.format((bytes / 1024 / 1024).toFixed(1))} مگابایت`;
}

function formatTime(seconds) {
  const total = Math.max(0, Math.floor(seconds || 0));
  const minutes = Math.floor(total / 60);
  const remainder = total % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`
    .replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[digit]);
}

function selectFile(file) {
  const extension = `.${file.name.split(".").pop().toLowerCase()}`;
  const supported = state.capabilities?.supported_formats || [
    ".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4", ".mpeg", ".flac",
  ];
  if (!supported.includes(extension)) {
    showToast("این فرمت صوتی پشتیبانی نمی‌شود.");
    return;
  }
  const maxMb = state.capabilities?.max_upload_mb || 100;
  if (file.size > maxMb * 1024 * 1024) {
    showToast(`حجم فایل بیشتر از ${faNumber.format(maxMb)} مگابایت است.`);
    return;
  }
  state.file = file;
  elements.fileName.textContent = file.name;
  elements.fileMeta.textContent = `${formatBytes(file.size)} · آماده برای پردازش`;
  elements.uploadView.hidden = true;
  elements.selectedView.hidden = false;
}

function resetApp() {
  state.file = null;
  state.job = null;
  state.result = null;
  elements.fileInput.value = "";
  elements.uploadView.hidden = false;
  elements.selectedView.hidden = true;
  elements.processingView.hidden = true;
  elements.resultPanel.hidden = true;
  elements.warningBanner.hidden = true;
  updateProgress(0, "در حال آماده‌سازی فایل صوتی");
  $("#workspace").scrollIntoView({ behavior: "smooth", block: "center" });
}

function updateProgress(progress, stage) {
  const value = Math.max(0, Math.min(100, progress || 0));
  elements.progressValue.style.width = `${value}%`;
  elements.progressLabel.textContent = `${faNumber.format(value)}٪`;
  elements.processingStage.textContent = stage;
}

async function loadCapabilities() {
  try {
    const response = await fetch("/api/capabilities");
    if (!response.ok) {
      throw new Error(`Capabilities request failed with HTTP ${response.status}`);
    }
    state.capabilities = await response.json();
    const isDemo = state.capabilities.engine === "demo";
    elements.engineState.className = `engine-state ${isDemo ? "demo" : "ready"}`;
    elements.engineState.removeAttribute("title");
    elements.engineState.innerHTML = `<span class="status-dot"></span>${
      isDemo ? "حالت نمایشی" : `مدل ${state.capabilities.model}`
    }`;
    const maxLabel = $(".format-list span:last-child");
    maxLabel.textContent = `تا ${faNumber.format(state.capabilities.max_upload_mb)} مگابایت`;
  } catch (error) {
    console.error("AvaNegar API is unavailable:", error);
    elements.engineState.className = "engine-state disconnected";
    elements.engineState.title =
      "Backend را با دستور avanegar --reload اجرا کنید و صفحه را دوباره بارگذاری کنید.";
    elements.engineState.innerHTML =
      '<span class="status-dot"></span>API در دسترس نیست';
  }
}

async function startTranscription() {
  if (!state.file) return;
  elements.selectedView.hidden = true;
  elements.processingView.hidden = false;
  elements.processingFile.textContent = state.file.name;
  updateProgress(4, "در حال بارگذاری فایل");

  const form = new FormData();
  form.append("file", state.file);
  form.append("normalize", $("#normalizeOption").checked);
  form.append("punctuation", true);
  form.append("word_timestamps", true);
  form.append("mark_uncertain", $("#uncertainOption").checked);
  form.append("speaker_labels", $("#speakerOption").checked);

  try {
    const response = await fetch("/api/transcriptions", { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "ارسال فایل ناموفق بود.");
    state.job = payload;
    updateProgress(payload.progress, payload.stage);
    await pollJob(payload.id);
  } catch (error) {
    elements.processingView.hidden = true;
    elements.selectedView.hidden = false;
    showToast(error.message || "خطایی در پردازش فایل رخ داد.");
  }
}

async function pollJob(id) {
  while (true) {
    await new Promise((resolve) => window.setTimeout(resolve, 850));
    const response = await fetch(`/api/transcriptions/${id}`);
    if (!response.ok) throw new Error("وضعیت رونویسی قابل دریافت نیست.");
    const job = await response.json();
    state.job = job;
    updateProgress(job.progress, job.stage);
    if (job.status === "completed") {
      state.result = job.result;
      window.setTimeout(showResult, 350);
      return;
    }
    if (job.status === "failed") {
      throw new Error(job.error || "پردازش صوت ناموفق بود.");
    }
  }
}

function showResult() {
  elements.processingView.hidden = true;
  elements.resultPanel.hidden = false;
  const segments = state.result.segments || [];
  const uncertain = segments.filter((item) => item.uncertain).length;
  const duration = formatTime(state.result.duration);
  elements.resultSummary.textContent =
    `${faNumber.format(segments.length)} بخش · ${duration} دقیقه · زبان فارسی`;

  if (state.result.warnings?.length) {
    elements.warningBanner.hidden = false;
    elements.warningText.textContent = state.result.warnings.join(" ");
  } else if (uncertain) {
    elements.warningBanner.hidden = false;
    elements.warningText.textContent =
      `${faNumber.format(uncertain)} بخش با اطمینان پایین مشخص شده و بهتر است بازبینی شود.`;
  }
  renderTranscript();
  elements.resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderTranscript() {
  if (!state.result) return;
  if (state.activeView === "plain") {
    const paragraph = document.createElement("p");
    paragraph.className = "plain-transcript";
    paragraph.textContent = state.result.text;
    elements.transcriptContent.replaceChildren(paragraph);
    return;
  }

  const fragment = document.createDocumentFragment();
  for (const segment of state.result.segments) {
    const row = document.createElement("article");
    row.className = `segment${segment.uncertain ? " uncertain" : ""}`;

    const time = document.createElement("time");
    time.className = "segment-time";
    time.textContent = formatTime(segment.start);

    const body = document.createElement("div");
    body.className = "segment-body";
    const meta = document.createElement("div");
    if (segment.speaker) {
      const speaker = document.createElement("span");
      speaker.className = "speaker-label";
      speaker.textContent = segment.speaker;
      meta.append(speaker);
    }
    if (segment.confidence != null) {
      const confidence = document.createElement("span");
      confidence.className = "confidence";
      confidence.textContent = `${Math.round(segment.confidence * 100)}%`;
      confidence.title = "میزان اطمینان";
      meta.append(confidence);
    }
    const text = document.createElement("p");
    text.textContent = segment.text;
    body.append(meta, text);
    row.append(time, body);
    fragment.append(row);
  }
  elements.transcriptContent.replaceChildren(fragment);
}

async function toggleRecording() {
  if (state.mediaRecorder?.state === "recording") {
    state.mediaRecorder.stop();
    state.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    return;
  }
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    showToast("مرورگر شما امکان ضبط صدا را پشتیبانی نمی‌کند.");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.recordingChunks = [];
    state.mediaRecorder = new MediaRecorder(stream);
    state.mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size) state.recordingChunks.push(event.data);
    });
    state.mediaRecorder.addEventListener("stop", () => {
      window.clearInterval(state.recordingTimer);
      elements.recordButton.classList.remove("recording");
      elements.recordLabel.textContent = "ضبط صدا با میکروفون";
      const blob = new Blob(state.recordingChunks, { type: state.mediaRecorder.mimeType });
      const extension = state.mediaRecorder.mimeType.includes("ogg") ? "ogg" : "webm";
      selectFile(new File([blob], `ضبط-آوانگار-${Date.now()}.${extension}`, { type: blob.type }));
    });
    state.mediaRecorder.start();
    state.recordingStartedAt = Date.now();
    elements.recordButton.classList.add("recording");
    elements.recordLabel.textContent = "پایان ضبط";
    state.recordingTimer = window.setInterval(() => {
      elements.recordTime.textContent = formatTime((Date.now() - state.recordingStartedAt) / 1000);
    }, 500);
  } catch {
    showToast("اجازهٔ دسترسی به میکروفون داده نشد.");
  }
}

elements.dropZone.addEventListener("click", () => elements.fileInput.click());
elements.dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") elements.fileInput.click();
});
elements.fileInput.addEventListener("change", () => {
  if (elements.fileInput.files[0]) selectFile(elements.fileInput.files[0]);
});
["dragenter", "dragover"].forEach((name) => {
  elements.dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    elements.dropZone.classList.add("dragging");
  });
});
["dragleave", "drop"].forEach((name) => {
  elements.dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    elements.dropZone.classList.remove("dragging");
  });
});
elements.dropZone.addEventListener("drop", (event) => {
  if (event.dataTransfer.files[0]) selectFile(event.dataTransfer.files[0]);
});

$("#removeFile").addEventListener("click", resetApp);
$("#newFileButton").addEventListener("click", resetApp);
elements.startButton.addEventListener("click", startTranscription);
elements.recordButton.addEventListener("click", toggleRecording);

$$(".view-tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    $$(".view-tabs button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.activeView = button.dataset.view;
    renderTranscript();
  });
});

$("#copyButton").addEventListener("click", async () => {
  if (!state.result) return;
  try {
    await navigator.clipboard.writeText(state.result.text);
    showToast("متن در حافظه کپی شد.");
  } catch {
    showToast("کپی خودکار ممکن نبود.");
  }
});

$$("[data-export]").forEach((button) => {
  button.addEventListener("click", () => {
    if (state.job) window.location.href =
      `/api/transcriptions/${state.job.id}/export/${button.dataset.export}`;
  });
});

loadCapabilities();
