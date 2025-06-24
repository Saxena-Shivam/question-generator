import streamlit as st
from pymongo import MongoClient
import random
import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# --- Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
groq_api_key = os.getenv("GROQ_API_KEY")
client1 = Groq(api_key=groq_api_key)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_questions = client["Questions"]["subjects"]
collection_textbooks = client["Textbooks"]["content"]

# --- Session State ---
if "questions" not in st.session_state:
    st.session_state.questions = []

# --- Functions ---
def fetch_textbook_content(class_selected, subject_selected, topic):
    try:
        doc = collection_textbooks.find_one({
            "class": int(class_selected),
            "subject_name": subject_selected,
            "topic": topic
        })
        return doc["textbook"].strip() if doc and doc.get("textbook") else ""
    except Exception as e:
        st.error(f"Error fetching textbook content: {e}")
        return ""

def classify_performance(score):
    if score <= 49:
        return "Weak"
    elif 50 <= score <= 74:
        return "Good"
    else:
        return "Excellent"

def get_difficulty_marks(level):
    if level == "Weak":
        return [("1m", 1, "easy"), ("2m", 2, "easy"), ("3m", 3, "easy"), ("5m", 5, "medium")]
    elif level == "Good":
        return [("5m", 5, "medium"), ("2m", 2, "easy"), ("10m", 10, "hard")]
    else:
        return [("10m", 10, "hard"), ("5m", 5, "medium")]

def get_questions_from_db(class_selected, subject_selected, mark, topic, count, used_questions, difficulty=None):
    questions = []
    try:
        doc = collection_questions.find_one({"class": class_selected, "subject_name": subject_selected})
        if not doc:
            return []
        for t in doc["topics"]:
            if t.get("topic_name", t.get("topic")) == topic:
                pool = [
                    q for q in t["questions"]
                    if q["marks"] == int(mark.replace("m", ""))
                    and (difficulty is None or q.get("difficulty") == difficulty)
                    and q["question"] not in used_questions
                ]
                selected = random.sample(pool, min(count, len(pool))) if pool else []
                questions.extend(selected)
                used_questions.update(q["question"] for q in selected)
        return questions
    except Exception as e:
        st.error(f"Error fetching questions from DB: {e}")
        return []

def generate_ai_question(topic, mark_type, mark_value, difficulty, context):
    prompt = f"""
    Generate a {difficulty}-level question about {topic} for {mark_value} marks based on the following content:
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

def generate_question_paper(class_selected, subject_selected, student_scores, total_marks, min_per_topic, max_per_topic):
    topic_difficulties = []
    for topic, score in student_scores.items():
        perf = classify_performance(score)
        for mark_type, mark_value, difficulty in get_difficulty_marks(perf):
            topic_difficulties.append((topic, mark_type, mark_value, difficulty, perf))

    random.shuffle(topic_difficulties)
    used_questions = set()
    question_paper = []
    marks_so_far = 0
    topic_counts = {topic: 0 for topic in student_scores}

    while marks_so_far < total_marks:
        made_progress = False
        for topic, mark_type, mark_value, difficulty, perf in topic_difficulties:
            if marks_so_far + mark_value > total_marks:
                continue
            if topic_counts[topic] >= max_per_topic:
                continue
            db_qs = get_questions_from_db(class_selected, subject_selected, mark_type, topic, 1, used_questions, difficulty)
            if db_qs:
                q = db_qs[0]
                question_paper.append({
                    "question_text": q["question"],
                    "answer": q.get("answer", ""),
                    "topic": topic,
                    "difficulty": q.get("difficulty", difficulty),
                    "marks": q["marks"],
                    "source": "DB"
                })
                marks_so_far += q["marks"]
                topic_counts[topic] += 1
                made_progress = True
            else:
                context = fetch_textbook_content(class_selected, subject_selected, topic)
                if context:
                    ai_q = generate_ai_question(topic, mark_type, mark_value, difficulty, context)
                    question_paper.append({
                        "question_text": ai_q,
                        "answer": "",
                        "topic": topic,
                        "difficulty": difficulty,
                        "marks": mark_value,
                        "source": "AI"
                    })
                    marks_so_far += mark_value
                    topic_counts[topic] += 1
                    made_progress = True
            if marks_so_far >= total_marks:
                break
        if not made_progress:
            break

    for topic in student_scores:
        while topic_counts[topic] < min_per_topic and marks_so_far < total_marks:
            perf = classify_performance(student_scores[topic])
            for mark_type, mark_value, difficulty in get_difficulty_marks(perf):
                if marks_so_far + mark_value > total_marks:
                    continue
                db_qs = get_questions_from_db(class_selected, subject_selected, mark_type, topic, 1, used_questions, difficulty)
                if db_qs:
                    q = db_qs[0]
                    question_paper.append({
                        "question_text": q["question"],
                        "answer": q.get("answer", ""),
                        "topic": topic,
                        "difficulty": q.get("difficulty", difficulty),
                        "marks": q["marks"],
                        "source": "DB"
                    })
                    marks_so_far += q["marks"]
                    topic_counts[topic] += 1
                    break
                else:
                    context = fetch_textbook_content(class_selected, subject_selected, topic)
                    if context:
                        ai_q = generate_ai_question(topic, mark_type, mark_value, difficulty, context)
                        question_paper.append({
                            "question_text": ai_q,
                            "answer": "",
                            "topic": topic,
                            "difficulty": difficulty,
                            "marks": mark_value,
                            "source": "AI"
                        })
                        marks_so_far += mark_value
                        topic_counts[topic] += 1
                        break
    return question_paper

def format_question_paper(questions):
    formatted = []
    topics = sorted(set(q["topic"] for q in questions))
    for topic in topics:
        formatted.append(f"\n\n### {topic}\n")
        topic_questions = [q for q in questions if q["topic"] == topic]
        for i, question in enumerate(topic_questions, 1):
            formatted.append(f"{i}. ({question['marks']} marks, {question['difficulty']}) {question['question_text']}\nAnswer: {question.get('answer','')}\n")
    return "\n".join(formatted)

# --- Streamlit UI ---
st.set_page_config(page_title="Personalized Question Paper Generator", layout="wide")

# Sidebar for controls
with st.sidebar:
    st.title("Controls")
    # Step 1: Select class and subject
    classes = sorted(collection_questions.distinct("class"))
    class_selected = st.selectbox("Select Class", classes)
    subject_cursor = collection_questions.find({"class": class_selected})
    subject_names = sorted({doc["subject_name"] for doc in subject_cursor})
    subject_selected = st.selectbox("Select Subject", subject_names)
    # Step 2: Paper parameters
    st.subheader("Paper Parameters")
    total_marks = st.number_input("Total Marks", min_value=10, max_value=100, value=80)
    min_per_topic = st.number_input("Minimum Questions per Topic", min_value=0, max_value=10, value=1)
    max_per_topic = st.number_input("Maximum Questions per Topic", min_value=1, max_value=20, value=5)

# Main content area
st.title("📝 Personalized Question Paper Generator")

# Step 2: Input student scores
st.subheader("📊 Enter Student Performance by Topic")
topics_cursor = collection_questions.find_one({"class": class_selected, "subject_name": subject_selected})
available_topics = [topic["topic_name"] for topic in topics_cursor["topics"]] if topics_cursor else []

student_scores = {}
with st.expander("Enter Scores for Each Topic", expanded=True):
    for topic in available_topics:
        student_scores[topic] = st.number_input(
            f"Score (0-100) for {topic}",
            min_value=0,
            max_value=100,
            value=70,
            step=1,
            key=f"score_{topic}"
        )

if st.button("Generate Question Paper", type="primary"):
    with st.spinner("🔍 Generating your personalized question paper..."):
        st.session_state.questions = generate_question_paper(
            class_selected,
            subject_selected,
            student_scores,
            total_marks,
            min_per_topic,
            max_per_topic
        )

# Display results
if st.session_state.questions:
    st.success("✅ Question paper generated successfully!")
    # Summary statistics
    with st.expander("📊 Statistics", expanded=False):
        total_marks_sum = sum(q["marks"] for q in st.session_state.questions)
        db_count = sum(1 for q in st.session_state.questions if q["source"] == "DB")
        ai_count = sum(1 for q in st.session_state.questions if q["source"] == "AI")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Questions", len(st.session_state.questions))
        col2.metric("Total Marks", total_marks_sum)
        col3.metric("AI Questions", ai_count)
    # Question paper display
    st.subheader("📜 Generated Question Paper")
    with st.container():
        topics = sorted(set(q["topic"] for q in st.session_state.questions))
        for topic in topics:
            st.markdown(f"### {topic}")
            topic_questions = [q for q in st.session_state.questions if q["topic"] == topic]
            for i, question in enumerate(topic_questions, 1):
                source_color = "#4CAF50" if question["source"] == "DB" else "#2196F3"
                st.markdown(
                    f"""
                    <div style="
                        padding: 12px;
                        margin-bottom: 15px;
                        border-radius: 8px;
                        background-color: #ffffff;
                        border-left: 5px solid {source_color};
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <div style="
                            font-weight: bold; 
                            font-size: 16px;
                            color: #333333;
                            margin-bottom: 8px;
                        ">
                            {i}. {question["question_text"]}
                        </div>
                        <div style="
                            font-size: 14px; 
                            color: #555555;
                            display: flex;
                            gap: 15px;
                        ">
                            <span><b style="color: #6a1b9a;">Marks:</b> {question["marks"]}</span>
                            <span><b style="color: #6a1b9a;">Difficulty:</b> {question["difficulty"]}</span>
                            <span><b style="color: {source_color};">Source:</b> {question["source"]}</span>
                            <span><b style="color: #00897b;">Answer:</b> {question.get("answer", "")}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    # Download options
    st.subheader("💾 Download Options")
    col1, col2 = st.columns(2)
    with col1:
        # Formatted question paper download
        formatted_paper = format_question_paper(st.session_state.questions)
        st.download_button(
            label="Download as Text File",
            data=formatted_paper,
            file_name="question_paper.txt",
            mime="text/plain",
            help="Download the question paper in a clean text format"
        )
    with col2:
        # CSV download (for detailed analysis)
        df = pd.DataFrame(st.session_state.questions)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV (Detailed)",
            data=csv,
            file_name="question_details.csv",
            mime="text/csv",
            help="Download detailed question data including sources and difficulty"
        )