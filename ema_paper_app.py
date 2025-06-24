import streamlit as st
import pandas as pd
from ema_paper import generate_ema_adaptive_paper, calculate_ema
from student_schema import fetch_last_two_exam_scores, subjects
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# --- Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_students = client["Students"]["students"]
collection_questions = client["Questions"]["subjects"]

# Exam types and syllabus coverage (with dates for filtering)
EXAM_TYPES = [
    {"exam_type": "term1", "label": "Term 1", "syllabus_topics": 1, "date": "2025-05-01"},
    {"exam_type": "mid_term", "label": "Mid Term", "syllabus_topics": 2, "date": "2025-07-01"},
    {"exam_type": "term2", "label": "Term 2", "syllabus_topics": 3, "date": "2025-09-01"},
    {"exam_type": "end_term", "label": "End Term", "syllabus_topics": None, "date": "2025-12-01"},
]

st.set_page_config(page_title="EMA Adaptive Question Paper Generator", layout="wide")

# --- Sidebar: Student, Subject, Exam Type ---
with st.sidebar:
    st.title("EMA Adaptive Paper Controls")

    # Select student
    students = list(collection_students.find({}, {"student_id": 1, "name": 1, "class": 1, "roll_number": 1}))
    student_options = [
        f"{s['student_id']} - {s.get('name','')} (Class {s.get('class','')}, Roll {s.get('roll_number','')})"
        for s in students
    ]
    student_selected = st.selectbox("Select Student", student_options)
    student_id = student_selected.split(" - ")[0] if student_selected else None

    # Get student details
    student_doc = collection_students.find_one({"student_id": student_id}) if student_id else None
    class_num = student_doc["class"] if student_doc else None

    # Subject selection
    subject_names = sorted(collection_questions.distinct("subject_name"))
    subject_selected = st.selectbox("Select Subject", subject_names)

    # Exam type selection
    exam_type_label = st.selectbox(
        "Select Exam Type",
        [e["label"] for e in EXAM_TYPES]
    )
    exam_type = next(e for e in EXAM_TYPES if e["label"] == exam_type_label)
    exam_date = exam_type["date"]

# --- Main Content ---
st.title("📈 EMA Adaptive Question Paper Generator")

# --- Adaptive Topic & EMA Calculation ---
topic_ema_map = {}
if student_doc and subject_selected and exam_type:
    # Get all topics for this subject/class
    subject_obj = next((s for s in subjects if s["subject_name"] == subject_selected), None)
    all_topics = subject_obj["chapters_by_class"].get(class_num, []) if subject_obj else []

    # Determine topics for this exam type
    if exam_type["syllabus_topics"] is None or exam_type["syllabus_topics"] > len(all_topics):
        topics_for_exam = all_topics
    else:
        topics_for_exam = all_topics[:exam_type["syllabus_topics"]]

    # For each topic in the syllabus, calculate EMA from student's past exams *before* this exam
    for topic in topics_for_exam:
        scores = fetch_last_two_exam_scores(student_id, subject_selected, topic, upto_date=exam_date)
        if len(scores) == 2:
            ema = calculate_ema(scores[0], scores[1])
        elif len(scores) == 1:
            ema = calculate_ema(scores[0], None)
        else:
            ema = None  # No data, triggers fallback in get_difficulty_distribution
        topic_ema_map[topic] = ema

if st.button("Generate EMA Adaptive Paper", type="primary"):
    if not student_id or not subject_selected or not topic_ema_map:
        st.warning("No topics found for this student and subject/exam.")
    else:
        with st.spinner("Generating question paper..."):
            paper = generate_ema_adaptive_paper(
                student_id=student_id,
                class_num=class_num,
                subject=subject_selected,
                topic_ema_map=topic_ema_map
            )
            paper["exam_type"] = exam_type["exam_type"]
            st.session_state.questions = paper["questions"]
            st.session_state.paper_meta = paper

# --- Display Results ---
if "questions" in st.session_state and st.session_state.questions:
    st.success("✅ Question paper generated successfully!")
    # Show meta info
    meta = st.session_state.paper_meta
    st.markdown(
        f"**Student ID:** {meta['student_id']} &nbsp;&nbsp; "
        f"**Class:** {meta['class']} &nbsp;&nbsp; "
        f"**Subject:** {meta['subject']} &nbsp;&nbsp; "
        f"**Exam Type:** {meta.get('exam_type','')} &nbsp;&nbsp; "
        f"**Generated on:** {meta['generated_on']}"
    )
    st.markdown(f"**Strategy:** {meta['question_strategy']}")

    # Statistics
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
        def format_question_paper(questions):
            formatted = []
            topics = sorted(set(q["topic"] for q in questions))
            for topic in topics:
                formatted.append(f"\n\n### {topic}\n")
                topic_questions = [q for q in questions if q["topic"] == topic]
                for i, question in enumerate(topic_questions, 1):
                    formatted.append(f"{i}. ({question['marks']} marks, {question['difficulty']}) {question['question_text']}\nAnswer: {question.get('answer','')}\n")
            return "\n".join(formatted)
        formatted_paper = format_question_paper(st.session_state.questions)
        st.download_button(
            label="Download as Text File",
            data=formatted_paper,
            file_name="ema_question_paper.txt",
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
            file_name="ema_question_details.csv",
            mime="text/csv",
            help="Download detailed question data including sources and difficulty"
        )