import re
import math
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# Additional meeting filler and generic verbs to exclude from topics
CUSTOM_STOP_WORDS = {
    'good', 'morning', 'afternoon', 'evening', 'everyone', 'hello', 'hi', 'thanks', 
    'thank', 'team', 'meeting', 'going', 'will', 'can', 'also', 'let', 'lets', 'us', 
    'yes', 'no', 'okay', 'ok', 'think', 'said', 'asked', 'would', 'could', 'should', 
    'like', 'today', 'well', 'just', 'get', 'got', 'make', 'sure', 'know', 'see',
    'want', 'need', 'needs', 'take', 'come', 'way', 'say', 'says', 'talking', 'talk',
    'agreed', 'decided', 'conduct', 'finish', 'used', 'using', 'complete', 'prepare',
    'discussed', 'regarding', 'around', 'about', 'another', 'first', 'second', 'next'
}

class MeetingAnalyzer:
    def __init__(self):
        # Known day / time expressions for deadline extraction
        self.deadline_pattern = re.compile(
            r'\b(?:by|before|on|due|until|target|for)\s+'
            r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|'
            r'tomorrow|today|next week|this week|end of day|EOD|end of week|EOW|'
            r'\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)|'
            r'\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b',
            re.IGNORECASE
        )
        
        # Direct temporal regex standalone
        self.standalone_deadline_pattern = re.compile(
            r'\b(by\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|tomorrow|today|next week|this week|EOD|end of day)|'
            r'before\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|tomorrow|next week)|'
            r'on\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)|'
            r'tomorrow|next week|this week)\b',
            re.IGNORECASE
        )

        # Regex patterns for Action Item indicators
        self.action_modal_pattern = re.compile(
            r'\b(will|needs? to|has to|have to|should|must|is responsible for|are responsible for|'
            r'tasked with|assigned to|takes? care of|is going to|are going to|shall|assigned|todo|to-do)\b',
            re.IGNORECASE
        )

        # Common Action Verbs
        self.action_verb_pattern = re.compile(
            r'\b(complete|prepare|build|test|deploy|fix|create|design|implement|update|'
            r'review|write|setup|organize|deliver|finish|refactor|document|configure|handle|resolve|work on)\b',
            re.IGNORECASE
        )

        # Decision indicators
        self.decision_pattern = re.compile(
            r'\b(decided|agreed|resolved|concluded|approved|settled on|selected|finalized|chose|decision is|agreed to|decided to)\b',
            re.IGNORECASE
        )

        # Issue / Blocker indicators
        self.issue_pattern = re.compile(
            r'\b(issue|blocker|failing|failed|error|bug|problem|causing|not working|unable to|delayed|stuck|bottleneck|risk|failure|broken|down|crash|causing an issue)\b',
            re.IGNORECASE
        )

        # Question indicators
        self.question_reporting_pattern = re.compile(
            r'\b(asked|wondered|inquired|questioned|asking)\b',
            re.IGNORECASE
        )

    def split_sentences(self, text):
        """Splits transcript into clean, non-empty sentences."""
        if not text or not text.strip():
            return []
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        return sentences

    def extract_topics(self, sentences, top_n=6):
        """Extract key topics/keywords using TF-IDF."""
        if not sentences:
            return []
        
        full_text = " ".join(sentences)
        if not full_text.strip():
            return []

        try:
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            stop_words = list(ENGLISH_STOP_WORDS.union(CUSTOM_STOP_WORDS))

            vectorizer = TfidfVectorizer(
                stop_words=stop_words,
                ngram_range=(1, 2),
                max_features=50,
                token_pattern=r'(?u)\b[A-Za-z]{3,}\b'
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            scores = tfidf_matrix.sum(axis=0).A1
            word_scores = zip(feature_names, scores)
            
            sorted_words = sorted(word_scores, key=lambda x: x[1], reverse=True)
            
            selected_topics = []
            seen_tokens = set()
            
            for word, score in sorted_words:
                tokens = word.lower().split()
                # Ensure it's not a generic stop word
                if any(t in CUSTOM_STOP_WORDS for t in tokens):
                    continue

                formatted_topic = word.title()
                if not any(t in seen_tokens for t in tokens):
                    selected_topics.append(formatted_topic)
                    for t in tokens:
                        seen_tokens.add(t)
                if len(selected_topics) >= top_n:
                    break
            
            return selected_topics
        except Exception:
            words = re.findall(r'\b[A-Za-z]{4,}\b', full_text.lower())
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            stop_words = ENGLISH_STOP_WORDS.union(CUSTOM_STOP_WORDS)
            filtered = [w.title() for w in words if w not in stop_words]
            counts = Counter(filtered)
            return [item[0] for item in counts.most_common(top_n)]

    def extract_action_items(self, sentences):
        """Extract action items, assignee, deadline, and clean task description."""
        action_items = []

        for sentence in sentences:
            # Skip if sentence is explicitly a question reporting sentence ("Priya asked whether...")
            if self.question_reporting_pattern.search(sentence) or sentence.strip().endswith('?'):
                continue

            has_modal = bool(self.action_modal_pattern.search(sentence))
            has_verb = bool(self.action_verb_pattern.search(sentence))

            # Sentence must contain explicit action modal or verb commitment
            if not (has_modal or has_verb):
                continue

            assignee = "Not detected"
            deadline = "Not detected"

            # 1. Extract Deadline
            deadline_match = self.deadline_pattern.search(sentence)
            if deadline_match:
                deadline = deadline_match.group(0).strip().title()
            else:
                standalone_match = self.standalone_deadline_pattern.search(sentence)
                if standalone_match:
                    deadline = standalone_match.group(0).strip().title()

            # 2. Extract Assignee
            assignee_match = re.search(
                r'\b(?:assigned to|responsible for|handled by|owner:?)\s+([A-Z][a-zA-Z]+)',
                sentence
            )
            if assignee_match:
                assignee = assignee_match.group(1).title()
            else:
                front_part = sentence.split('.')[0]
                name_match = re.search(r'^\s*([A-Z][a-z]+)\s+(?:will|needs? to|has to|should|is|shall|must|is going to)', front_part)
                if name_match:
                    name_candidate = name_match.group(1)
                    if name_candidate.lower() not in {'good', 'the', 'this', 'that', 'we', 'our', 'they', 'team'}:
                        assignee = name_candidate
                else:
                    if re.search(r'\b(we|team|our team)\s+(?:will|need to|should|must|are going to)\b', sentence, re.IGNORECASE):
                        assignee = "Team"

            # 3. Clean Task Description
            task = sentence
            if assignee != "Not detected" and assignee != "Team":
                task_part = re.sub(r'^\s*' + re.escape(assignee) + r'\s+(?:will|needs? to|has to|should|must|is responsible for|is going to|shall)\s+', '', task, flags=re.IGNORECASE)
                if task_part != task:
                    task = task_part

            # Remove deadline phrase from task string if deadline was detected
            if deadline != "Not detected":
                task = re.sub(re.escape(deadline), '', task, flags=re.IGNORECASE)
                task = re.sub(r'\b(by|before|on|due|until|target)\s*$', '', task, flags=re.IGNORECASE)

            task = task.strip().rstrip('.,!?').strip()
            if task:
                task = task[0].upper() + task[1:]

            if len(task.split()) >= 2:
                action_items.append({
                    "task": task,
                    "assignee": assignee,
                    "deadline": deadline,
                    "source": sentence
                })

        return action_items

    def extract_decisions(self, sentences):
        """Extract decision-related sentences."""
        decisions = []
        for sentence in sentences:
            if self.decision_pattern.search(sentence):
                decisions.append(sentence.strip())
        return decisions

    def extract_questions(self, sentences):
        """Extract questions or sentence inquiries."""
        questions = []
        for sentence in sentences:
            is_q_mark = sentence.strip().endswith('?')
            is_reporting_q = bool(self.question_reporting_pattern.search(sentence))
            starts_with_q = bool(re.match(r'^\s*(Can|Could|Would|Should|What|When|Where|Why|How|Is|Are|Do|Does|Did)\b', sentence, re.IGNORECASE))
            
            if is_q_mark or is_reporting_q or starts_with_q:
                questions.append(sentence.strip())
        return questions

    def extract_issues(self, sentences):
        """Extract issues, problems, or blockers."""
        issues = []
        for sentence in sentences:
            if self.issue_pattern.search(sentence):
                issues.append(sentence.strip())
        return issues

    def score_important_sentences(self, sentences, top_n=4):
        """Score and rank important sentences in transcript."""
        if not sentences:
            return []

        try:
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
            stop_words = list(ENGLISH_STOP_WORDS.union(CUSTOM_STOP_WORDS))
            
            vectorizer = TfidfVectorizer(stop_words=stop_words)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            scored_sentences = []
            for idx, sentence in enumerate(sentences):
                row = tfidf_matrix.getrow(idx)
                base_score = row.sum()
                
                bonus = 0.0
                if self.action_modal_pattern.search(sentence):
                    bonus += 0.5
                if self.decision_pattern.search(sentence):
                    bonus += 0.5
                if self.issue_pattern.search(sentence):
                    bonus += 0.4
                
                word_count = len(sentence.split())
                final_score = (base_score + bonus) / max(1, math.log(word_count + 1))
                scored_sentences.append({
                    "sentence": sentence,
                    "score": round(float(final_score), 3)
                })
            
            scored_sentences.sort(key=lambda x: x["score"], reverse=True)
            return scored_sentences[:top_n]
        except Exception:
            scored = []
            for s in sentences:
                score = len(s.split()) * 0.1
                scored.append({"sentence": s, "score": round(score, 2)})
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_n]

    def analyze(self, transcript_text):
        """Executes full NLP pipeline on meeting transcript."""
        if not transcript_text or not transcript_text.strip():
            return {
                "topics": [],
                "action_items": [],
                "decisions": [],
                "questions": [],
                "issues": [],
                "important_sentences": [],
                "statistics": {
                    "word_count": 0,
                    "sentence_count": 0,
                    "action_item_count": 0,
                    "decision_count": 0,
                    "question_count": 0,
                    "issue_count": 0,
                    "topic_count": 0
                }
            }

        sentences = self.split_sentences(transcript_text)
        words = re.findall(r'\b\w+\b', transcript_text)
        word_count = len(words)

        topics = self.extract_topics(sentences, top_n=6)
        action_items = self.extract_action_items(sentences)
        decisions = self.extract_decisions(sentences)
        questions = self.extract_questions(sentences)
        issues = self.extract_issues(sentences)
        important_sentences = self.score_important_sentences(sentences, top_n=4)

        statistics = {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "action_item_count": len(action_items),
            "decision_count": len(decisions),
            "question_count": len(questions),
            "issue_count": len(issues),
            "topic_count": len(topics)
        }

        return {
            "topics": topics,
            "action_items": action_items,
            "decisions": decisions,
            "questions": questions,
            "issues": issues,
            "important_sentences": important_sentences,
            "statistics": statistics
        }
