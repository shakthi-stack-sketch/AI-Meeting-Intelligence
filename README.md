# AI Meeting Intelligence & Action Item Extraction System

An academic **Speech-to-Text & Natural Language Processing (NLP)** application that converts unformatted meeting transcripts and audio conversations into structured meeting intelligence, action items, decisions, topics, questions, and blocker insights.

Built completely using **Python, Flask, Scikit-Learn, and standard Browser Web Speech API**, without external LLM/API dependencies or RAG frameworks.

---

## 🌟 Key Features

* **Speech-to-Text (STT) Integration**: Live voice recording and real-time audio transcription powered by the browser's native Web Speech API (`SpeechRecognition`).
* **Transcript Workspace**: Edit, type, paste, or load sample meeting transcripts with live word counting.
* **Topic Extraction**: Extracts key domain terminology and phrases using **TF-IDF (Term Frequency-Inverse Document Frequency)** and N-gram scoring.
* **Action Item Information Extraction**: Automatically identifies commitments, assignees, deadlines, and task descriptions using rule-based NLP patterns.
  * Extracted fields: `Task Description`, `Assignee` (or `"Not detected"`), `Deadline` (or `"Not detected"`), and `Source Sentence`.
* **Decision Extraction**: Detects organizational decisions, technological choices, and consensus statements.
* **Question Extraction**: Identifies inquiries, reporting verbs, and open questions.
* **Issue / Blocker Detection**: Highlights technical problems, failing modules, risks, and deployment bottlenecks.
* **Sentence Importance Ranking**: Scores transcript sentences based on TF-IDF word weight density and semantic markers.
* **Calculated Analytics Dashboard**: Real-time calculated transcript statistics (word count, action density, decision density).

---

## 🎨 Design System & Color Palette

The interface follows a professional **Modern Meeting Workspace / Collaboration Intelligence** design system:

* **Deep Forest Green** (`#1b3b2b`): Primary brand headers, active sidebar navigation, and key accents.
* **Soft Sage Green** (`#88a08c` / `#e6eee8`): Neutral badges, active tags, and subtle highlights.
* **Warm Sand / Beige** (`#f4f1ea`): Workspace panels, toolbars, and card container fills.
* **Dark Charcoal** (`#2c322e`): Clean typography and high-contrast titles.
* **Muted Teal** (`#3a6b6c`): Primary action buttons and metrics indicators.
* **Off-White Background** (`#f9f8f6`): High readability dashboard canvas.

---

## 📁 Architecture & Directory Structure

```
AI-Meeting-Intelligence/
│
├── app.py                      # Flask web application & REST API routes
├── analyzer.py                 # Core NLP & Scikit-Learn extraction engine
├── requirements.txt            # Python dependencies (Flask, scikit-learn)
├── README.md                   # System documentation & usage guide
│
├── data/
│   └── sample_meetings.txt     # Standard academic sample meeting transcript
│
├── templates/
│   └── index.html              # HTML5 meeting workspace UI
│
└── static/
    ├── style.css               # Modern meeting workspace CSS design system
    └── script.js               # Web Speech API & dynamic UI renderer
```

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.8+** installed on your system.
* A modern web browser (Google Chrome, Microsoft Edge, or Safari) for optional live microphone speech recognition.

### 1. Install Dependencies
Navigate to the project directory and install the required lightweight Python libraries:

```bash
pip install -r requirements.txt
```

### 2. Run the Application Server
Start the Flask local development server:

```bash
python app.py
```

### 3. Open in Browser
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 API Endpoint Reference

### `POST /analyze`
Analyzes a meeting transcript and returns structured JSON intelligence.

**Request Body:**
```json
{
  "transcript": "Good morning everyone. Shakthi will complete the frontend implementation by Friday. Rahul will prepare the database schema by Wednesday. We decided to use PostgreSQL for the project. The login module is still causing an issue. Priya asked whether we can finish testing this week."
}
```

**Response JSON:**
```json
{
  "success": true,
  "data": {
    "topics": ["Frontend Implementation", "Database Schema", "Postgresql", "Login Module"],
    "action_items": [
      {
        "task": "Complete the frontend implementation",
        "assignee": "Shakthi",
        "deadline": "Friday",
        "source": "Shakthi will complete the frontend implementation by Friday."
      },
      {
        "task": "Prepare the database schema",
        "assignee": "Rahul",
        "deadline": "Wednesday",
        "source": "Rahul will prepare the database schema by Wednesday."
      }
    ],
    "decisions": [
      "We decided to use PostgreSQL for the project."
    ],
    "questions": [
      "Priya asked whether we can finish testing this week."
    ],
    "issues": [
      "The login module is still causing an issue."
    ],
    "important_sentences": [
      {
        "sentence": "Shakthi will complete the frontend implementation by Friday.",
        "score": 1.485
      }
    ],
    "statistics": {
      "word_count": 56,
      "sentence_count": 6,
      "action_item_count": 2,
      "decision_count": 1,
      "question_count": 1,
      "issue_count": 1,
      "topic_count": 4
    }
  }
}
```

### `GET /sample`
Returns the standard test sample transcript text.

---

## 🛠️ Verification & Testing Checklist

- [x] Dependencies installed (`Flask`, `scikit-learn`).
- [x] Backend server starts cleanly without errors.
- [x] Sample transcript analysis executes and populates all 6 dashboard sections.
- [x] Web Speech API microphone handler catches permission & unsupported browser events gracefully.
- [x] Empty transcript input displays friendly error banner without server exception.
- [x] Missing assignees or deadlines return `"Not detected"` instead of invented values.
- [x] UI adheres strictly to the Forest Green / Sage / Sand / Teal color specification.
