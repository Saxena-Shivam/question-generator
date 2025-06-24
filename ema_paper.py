import os
from pymongo import MongoClient
from dotenv import load_dotenv
from groq import Groq
import random
import datetime

# --- MongoDB and API Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
groq_api_key = os.getenv("GROQ_API_KEY")
client1 = Groq(api_key=groq_api_key)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_questions = client["Questions"]["subjects"]
collection_textbooks = client["Textbooks"]["content"]
collection_students = client["Students"]["students"]

def calculate_ema(latest, previous=None, alpha=0.7):
    if latest is not None and previous is not None:
        return round(alpha * latest + (1 - alpha) * previous, 1)
    elif latest is not None:
        return float(latest)
    else:
        return 60.0

def get_difficulty_distribution(ema, total_questions):
    if ema is None:  # No exams exist
        easy = int(round(total_questions * 0.33))
        medium = int(round(total_questions * 0.33))
        hard = total_questions - easy - medium
    elif ema < 50:
        easy = int(round(total_questions * 0.5))
        medium = int(round(total_questions * 0.3))
        hard = total_questions - easy - medium
    elif ema < 75:
        easy = int(round(total_questions * 0.2))
        medium = int(round(total_questions * 0.4))
        hard = total_questions - easy - medium
    else:
        easy = int(round(total_questions * 0.2))
        medium = int(round(total_questions * 0.3))
        hard = total_questions - easy - medium
    return {"easy": easy, "medium": medium, "hard": hard}

def fetch_textbook_content(class_selected, subject_selected, topic):
    doc = collection_textbooks.find_one({
        "class": int(class_selected),
        "subject_name": subject_selected,
        "topic": topic
    })
    return doc["textbook"].strip() if doc and doc.get("textbook") else ""

def get_questions_from_db(class_selected, subject_selected, topic, difficulty, count, used_questions):
    questions = []
    try:
        doc = collection_questions.find_one({"class": class_selected, "subject_name": subject_selected})
        if not doc:
            return []
        for t in doc["topics"]:
            if t.get("topic_name", t.get("topic")) == topic:
                pool = [
                    q for q in t["questions"]
                    if q.get("difficulty") == difficulty
                    and q["question"] not in used_questions
                ]
                selected = random.sample(pool, min(count, len(pool))) if pool else []
                questions.extend(selected)
                used_questions.update(q["question"] for q in selected)
        return questions
    except Exception as e:
        print(f"Error fetching questions from DB: {e}")
        return []

def generate_ai_question(topic, marks, difficulty, context):
    prompt = f"""
    Generate a {difficulty}-level question about {topic} for {marks} marks based on the following content:
    {context}
    Provide only the question text, no additional explanations.
    """
    try:
        response = client1.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Question Generation Error: {str(e)}"

def fetch_last_two_exam_scores(student_id, subject, topic, upto_date=None):
    """
    Returns the last two percentage scores for a topic in a subject for a student,
    considering only exams before upto_date (if provided).
    """
    student = collection_students.find_one({"student_id": student_id})
    if not student or "exams" not in student:
        return []
    exams = [e for e in student["exams"] if e["subject"] == subject]
    if upto_date:
        exams = [e for e in exams if e["date"] < upto_date]
    exams.sort(key=lambda x: x["date"], reverse=True)
    scores = []
    for exam in exams:
        for t in exam["topic_scores"]:
            if t["topic"] == topic:
                scores.append(t.get("percentage", 0))
    return scores[:2]

def generate_ema_adaptive_paper(student_id, class_num, subject, topic_ema_map):
    """
    topic_ema_map: dict of {topic: ema_value}
    Number of questions per topic is determined by EMA:
      - EMA < 50: 10 questions
      - EMA < 75: 7 questions
      - EMA >= 75: 5 questions
    """
    result = {
        "student_id": student_id,
        "class": class_num,
        "subject": subject,
        "generated_on": str(datetime.date.today()),
        "question_strategy": "ema_adaptive",
        "questions": []
    }
    used_questions = set()
    for topic, ema in topic_ema_map.items():
        # Decide number of questions per topic based on EMA
        if ema is None:
            total_questions = 6  # Default for no data, can be changed
        elif ema < 50:
            total_questions = 10
        elif ema < 75:
            total_questions = 7
        else:
            total_questions = 5
        dist = get_difficulty_distribution(ema, total_questions)
        for difficulty, count in dist.items():
            # Try to get from DB first
            db_qs = get_questions_from_db(class_num, subject, topic, difficulty, count, used_questions)
            for q in db_qs:
                result["questions"].append({
                    "question_text": q["question"],
                    "answer": q.get("answer", ""),
                    "topic": topic,
                    "difficulty": difficulty,
                    "marks": q["marks"],
                    "source": "DB"
                })
            # If not enough, generate with AI
            if len(db_qs) < count:
                context = fetch_textbook_content(class_num, subject, topic)
                for _ in range(count - len(db_qs)):
                    ai_q = generate_ai_question(topic, 5, difficulty, context)
                    result["questions"].append({
                        "question_text": ai_q,
                        "answer": "",
                        "topic": topic,
                        "difficulty": difficulty,
                        "marks": 5,
                        "source": "AI"
                    })
    return result