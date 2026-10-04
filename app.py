import os
from flask import Flask, render_template, request, jsonify
from analyzer import MeetingAnalyzer

app = Flask(__name__)
analyzer = MeetingAnalyzer()

# Path to sample meetings data file
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SAMPLE_FILE = os.path.join(DATA_DIR, 'sample_meetings.txt')

@app.route('/')
def index():
    """Renders the main Meeting Intelligence workspace dashboard."""
    return render_template('index.html')

@app.route('/sample', methods=['GET'])
def get_sample_transcript():
    """Returns the default sample meeting transcript for testing."""
    if os.path.exists(SAMPLE_FILE):
        with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
            sample_text = f.read().strip()
            return jsonify({"success": True, "transcript": sample_text})
    return jsonify({
        "success": True, 
        "transcript": "Good morning everyone. Shakthi will complete the frontend implementation by Friday. Rahul will prepare the database schema by Wednesday. We decided to use PostgreSQL for the project. The login module is still causing an issue. Priya asked whether we can finish testing this week. The team agreed to conduct testing on Thursday."
    })

@app.route('/analyze', methods=['POST'])
def analyze_meeting():
    """API Endpoint: Analyzes meeting transcript and extracts NLP intelligence."""
    try:
        data = request.get_json(silent=True) or {}
        transcript = data.get('transcript', '')

        # Graceful handling for non-string or empty inputs
        if not isinstance(transcript, str):
            transcript = str(transcript)

        # Run NLP analysis pipeline
        result = analyzer.analyze(transcript)
        return jsonify({"success": True, "data": result})

    except Exception as e:
        # Return friendly JSON error response rather than crashing
        return jsonify({
            "success": False,
            "error": f"An error occurred during transcript processing: {str(e)}"
        }), 400

if __name__ == '__main__':
    # Run Flask local web server
    print("Starting AI Meeting Intelligence & Action Item Extraction System...")
    app.run(host='127.0.0.1', port=5000, debug=True)
