/* ==========================================================================
   AI Meeting Intelligence & Action Item Extraction System - JavaScript
   Features:
     - Web Speech API Live Audio Transcription
     - Dynamic Flask API /analyze Integration
     - Real-time Word Counter & Status Banner
     - Dynamic UI Rendering for Action Items, Decisions, Topics, Questions, Issues
   ========================================================================== */

let recognition = null;
let isRecording = false;

// Initialize Web Speech API on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    initSpeechRecognition();
    updateWordCount();
    setupNavListeners();
});

/* --------------------------------------------------------------------------
   WEB SPEECH API SETUP & CONTROLS
   -------------------------------------------------------------------------- */
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn("Web Speech API is not supported in this browser.");
        return;
    }

    try {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isRecording = true;
            updateRecordingUI(true);
            showBanner("Microphone active. Listening to speech...", "info");
        };

        recognition.onresult = (event) => {
            const textarea = document.getElementById("transcript-input");
            let finalTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript + " ";
                }
            }

            if (finalTranscript) {
                // Append text neatly
                if (textarea.value && !textarea.value.endsWith(" ")) {
                    textarea.value += " ";
                }
                textarea.value += finalTranscript;
                updateWordCount();
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            let msg = "Speech recognition error occurred.";
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                msg = "Microphone access was denied. Please allow microphone permissions in your browser.";
            } else if (event.error === 'no-speech') {
                msg = "No speech detected. Please speak into your microphone.";
            }
            showBanner(msg, "error");
            stopRecording();
        };

        recognition.onend = () => {
            if (isRecording) {
                // Restart continuous recording if ended unexpectedly
                try {
                    recognition.start();
                } catch (e) {
                    stopRecording();
                }
            } else {
                updateRecordingUI(false);
            }
        };

    } catch (e) {
        console.error("Failed to initialize Speech Recognition:", e);
    }
}

function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    if (!recognition) {
        showBanner("Web Speech API is not supported in your browser. Please paste or type your transcript directly.", "error");
        return;
    }
    try {
        isRecording = true;
        recognition.start();
    } catch (e) {
        console.warn("Recognition already started or error:", e);
        updateRecordingUI(true);
    }
}

function stopRecording() {
    isRecording = false;
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {
            console.warn("Error stopping recognition:", e);
        }
    }
    updateRecordingUI(false);
    showBanner("Recording stopped. Click 'Analyze Meeting' to process transcript.", "info");
}

function updateRecordingUI(active) {
    const btn = document.getElementById("record-toggle-btn");
    const btnText = document.getElementById("record-btn-text");
    const indicator = document.getElementById("recording-indicator");

    if (active) {
        btn.classList.add("recording-active");
        btnText.innerText = "Stop Recording";
        indicator.classList.remove("hidden");
    } else {
        btn.classList.remove("recording-active");
        btnText.innerText = "Record Meeting";
        indicator.classList.add("hidden");
    }
}

/* --------------------------------------------------------------------------
   TRANSCRIPT EDITOR UTILITIES
   -------------------------------------------------------------------------- */
function updateWordCount() {
    const text = document.getElementById("transcript-input").value.trim();
    const wordCount = text ? text.split(/\s+/).length : 0;
    document.getElementById("live-word-count").innerText = `${wordCount} word${wordCount === 1 ? '' : 's'}`;
}

function clearTranscript() {
    document.getElementById("transcript-input").value = "";
    updateWordCount();
    showBanner("Transcript editor cleared.", "info");
}

async function loadSampleTranscript() {
    try {
        const response = await fetch('/sample');
        const data = await response.json();
        if (data.success) {
            document.getElementById("transcript-input").value = data.transcript;
            updateWordCount();
            showBanner("Sample meeting transcript loaded into workspace.", "info");
        }
    } catch (error) {
        console.error("Failed to load sample transcript:", error);
        showBanner("Could not load sample transcript.", "error");
    }
}

/* --------------------------------------------------------------------------
   BACKEND ANALYSIS & DYNAMIC UI UPDATES
   -------------------------------------------------------------------------- */
async function analyzeTranscript() {
    const transcriptText = document.getElementById("transcript-input").value.trim();

    if (!transcriptText) {
        showBanner("Please enter or record a meeting transcript before analyzing.", "error");
        return;
    }

    if (isRecording) {
        stopRecording();
    }

    const analyzeBtn = document.getElementById("analyze-btn");
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span class="btn-icon">⏳</span> Processing...`;

    showBanner("Analyzing meeting transcript using Scikit-Learn NLP engine...", "info");

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript: transcriptText })
        });

        const resData = await response.json();

        if (response.ok && resData.success) {
            renderAnalysisResults(resData.data);
            showBanner("Meeting intelligence successfully extracted!", "info");
        } else {
            showBanner(resData.error || "Failed to analyze meeting transcript.", "error");
        }
    } catch (error) {
        console.error("API Error:", error);
        showBanner("Network or backend server connection error.", "error");
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `<span class="btn-icon">⚡</span> Analyze Meeting`;
    }
}

function renderAnalysisResults(data) {
    const stats = data.statistics || {};

    // 1. Render Stats Overview
    document.getElementById("stat-words").innerText = stats.word_count || 0;
    document.getElementById("stat-action-items").innerText = stats.action_item_count || 0;
    document.getElementById("stat-decisions").innerText = stats.decision_count || 0;
    document.getElementById("stat-topics").innerText = stats.topic_count || 0;
    document.getElementById("stat-questions").innerText = stats.question_count || 0;
    document.getElementById("stat-issues").innerText = stats.issue_count || 0;

    // Sidebar Badge Counts
    document.getElementById("nav-action-count").innerText = stats.action_item_count || 0;
    document.getElementById("nav-decision-count").innerText = stats.decision_count || 0;
    document.getElementById("nav-topic-count").innerText = stats.topic_count || 0;
    document.getElementById("nav-question-count").innerText = stats.question_count || 0;
    document.getElementById("nav-issue-count").innerText = stats.issue_count || 0;

    // 2. Render Action Items Table
    const actionTbody = document.getElementById("action-items-tbody");
    document.getElementById("action-table-count").innerText = `${stats.action_item_count || 0} items`;
    actionTbody.innerHTML = "";

    if (data.action_items && data.action_items.length > 0) {
        data.action_items.forEach(item => {
            const tr = document.createElement("tr");

            const assigneeBadge = item.assignee !== "Not detected" 
                ? `<span class="badge-assignee">👤 ${escapeHtml(item.assignee)}</span>` 
                : `<span class="badge-neutral">Not detected</span>`;

            const deadlineBadge = item.deadline !== "Not detected" 
                ? `<span class="badge-deadline">📅 ${escapeHtml(item.deadline)}</span>` 
                : `<span class="badge-neutral">Not detected</span>`;

            tr.innerHTML = `
                <td><strong>${escapeHtml(item.task)}</strong></td>
                <td>${assigneeBadge}</td>
                <td>${deadlineBadge}</td>
                <td><span class="source-text">"${escapeHtml(item.source)}"</span></td>
            `;
            actionTbody.appendChild(tr);
        });
    } else {
        actionTbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="4" class="text-center">No action items detected in transcript.</td>
            </tr>`;
    }

    // 3. Render Decisions Section
    const decisionsList = document.getElementById("decisions-list");
    document.getElementById("decisions-count-badge").innerText = `${stats.decision_count || 0} decisions`;
    decisionsList.innerHTML = "";

    if (data.decisions && data.decisions.length > 0) {
        data.decisions.forEach(decision => {
            const card = document.createElement("div");
            card.className = "decision-card";
            card.innerHTML = `
                <strong>Decision Recorded</strong>
                "${escapeHtml(decision)}"
            `;
            decisionsList.appendChild(card);
        });
    } else {
        decisionsList.innerHTML = `<div class="empty-state">No decisions detected in transcript.</div>`;
    }

    // 4. Render Topics Tags
    const topicsTags = document.getElementById("topics-tags");
    document.getElementById("topics-count-badge").innerText = `${stats.topic_count || 0} topics`;
    topicsTags.innerHTML = "";

    if (data.topics && data.topics.length > 0) {
        data.topics.forEach(topic => {
            const tag = document.createElement("span");
            tag.className = "topic-tag";
            tag.innerText = topic;
            topicsTags.appendChild(tag);
        });
    } else {
        topicsTags.innerHTML = `<div class="empty-state">No key topics extracted.</div>`;
    }

    // 5. Render Questions Section
    const questionsList = document.getElementById("questions-list");
    document.getElementById("questions-count-badge").innerText = `${stats.question_count || 0} questions`;
    questionsList.innerHTML = "";

    if (data.questions && data.questions.length > 0) {
        data.questions.forEach(q => {
            const item = document.createElement("div");
            item.className = "question-item";
            item.innerHTML = `
                <span class="question-bullet">❓</span>
                <span>"${escapeHtml(q)}"</span>
            `;
            questionsList.appendChild(item);
        });
    } else {
        questionsList.innerHTML = `<div class="empty-state">No questions detected in transcript.</div>`;
    }

    // 6. Render Issues / Blockers Section
    const issuesList = document.getElementById("issues-list");
    document.getElementById("issues-count-badge").innerText = `${stats.issue_count || 0} issues`;
    issuesList.innerHTML = "";

    if (data.issues && data.issues.length > 0) {
        data.issues.forEach(issue => {
            const card = document.createElement("div");
            card.className = "issue-card";
            card.innerHTML = `
                <span class="issue-icon">⚠️</span>
                <span>"${escapeHtml(issue)}"</span>
            `;
            issuesList.appendChild(card);
        });
    } else {
        issuesList.innerHTML = `<div class="empty-state">No blockers or issues detected.</div>`;
    }

    // 7. Render Analysis & Important Sentences
    const sentencesList = document.getElementById("important-sentences-list");
    sentencesList.innerHTML = "";

    if (data.important_sentences && data.important_sentences.length > 0) {
        data.important_sentences.forEach(item => {
            const div = document.createElement("div");
            div.className = "ranked-item";
            div.innerHTML = `
                <span class="ranked-item-text">"${escapeHtml(item.sentence)}"</span>
                <span class="rank-score">Score: ${item.score}</span>
            `;
            sentencesList.appendChild(div);
        });
    } else {
        sentencesList.innerHTML = `<div class="empty-state">Sentences will be ranked after meeting analysis.</div>`;
    }

    // Detailed Metrics Breakdown
    const totalSentences = stats.sentence_count || 1;
    const actionDensity = Math.round((stats.action_item_count / totalSentences) * 100);
    const decisionDensity = Math.round((stats.decision_count / totalSentences) * 100);

    document.getElementById("metric-sentences").innerText = totalSentences;
    document.getElementById("metric-action-density").innerText = `${actionDensity}%`;
    document.getElementById("metric-decision-density").innerText = `${decisionDensity}%`;
}

/* --------------------------------------------------------------------------
   UI UTILITIES & NOTIFICATION BANNERS
   -------------------------------------------------------------------------- */
function showBanner(message, type = "info") {
    const banner = document.getElementById("status-banner");
    const bannerText = document.getElementById("banner-text");
    const bannerIcon = document.getElementById("banner-icon");

    bannerText.innerText = message;
    if (type === "error") {
        banner.className = "status-banner banner-error";
        bannerIcon.innerText = "⚠️";
    } else {
        banner.className = "status-banner";
        bannerIcon.innerText = "ℹ️";
    }
}

function closeBanner() {
    document.getElementById("status-banner").classList.add("hidden");
}

function setupNavListeners() {
    const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            navItems.forEach(n => n.classList.remove("active"));
            item.classList.add("active");
        });
    });
}

function scrollToSection(sectionId) {
    const el = document.getElementById(sectionId);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
