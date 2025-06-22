import streamlit as st
from pymongo import MongoClient
import random
import math

# Initialize session state for generate_pressed
if "generate_pressed" not in st.session_state:
    st.session_state.generate_pressed = False
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
# Get the MongoDB URI from the environment
mongo_uri = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["Questions"]
collection = db["subjects"]

def get_question_distribution(topics, total_questions):
    k = len(topics)
    base = total_questions // k
    remainder = total_questions % k

    # Shuffle topics to randomize who gets extra
    random.shuffle(topics)

    # Assign base + 1 to the first 'remainder' topics
    distribution = {topic: base for topic in topics}
    for i in range(remainder):
        distribution[topics[i]] += 1

    return distribution

def get_questions_from_db(class_selected, subject_selected, mark, distribution_dict):
    result = []
    ai_counter = 1

    doc = collection.find_one({"class": class_selected, "subject_name": subject_selected})
    if not doc:
        return []

    topic_dict = {t["topic_name"]: t["questions"] for t in doc["topics"]}

    for topic, count in distribution_dict.items():
        # Filter questions by selected mark
        questions_with_mark = [
            q["question"] for q in topic_dict.get(topic, [])
            if q["marks"] == int(mark.replace("m", ""))
        ]

        available = len(questions_with_mark)
        needed = count

        # Randomly select available questions (if any)
        selected = random.sample(questions_with_mark, min(needed, available))

        # Fill gap with AI-generated placeholders
        if len(selected) < needed:
            for _ in range(needed - len(selected)):
                selected.append(f"ai_{ai_counter}")
                ai_counter += 1

        result.extend(selected)

    return result

st.title("Question Paper Generator")

# 1️⃣ Select Class (top)
classes = sorted(collection.distinct("class"))
class_selected = st.selectbox("Select Class", classes)

# 2️⃣ Select Subject based on Class
subject_cursor = collection.find({"class": class_selected})
subject_names = sorted({doc["subject_name"] for doc in subject_cursor})
subject_selected = st.selectbox("Select Subject", subject_names)

# 3️⃣ Select Topics based on Class and Subject
topics_cursor = collection.find_one({"class": class_selected, "subject_name": subject_selected})
available_topics = [topic["topic_name"] for topic in topics_cursor["topics"]] if topics_cursor else []
selected_topics = st.multiselect("Select Topics", available_topics)

# 4️⃣ Number of Questions
num_questions = st.number_input("Enter Number of Questions", min_value=1, step=1)

# 5️⃣ Marks per question
marks_per_question = st.radio(
    "Select Marks per Question",
    options=["1m", "2m", "4m", "5m", "10m", "20m"]
)

# Store distribution and questions in session state
if "distribution" not in st.session_state:
    st.session_state.distribution = None
if "questions" not in st.session_state:
    st.session_state.questions = []

# ✅ Button 1: Generate Summary
if st.button("Generate Summary"):
    st.markdown("### Selection Summary")
    st.write(f"**Class:** {class_selected}")
    st.write(f"**Subject:** {subject_selected}")
    st.write(f"**Topics Selected:** {', '.join(selected_topics)}")
    st.write(f"**Number of Questions:** {num_questions}")
    st.write(f"**Marks per Question:** {marks_per_question}")

# ✅ Button 2: Generate Questions
button_label = "Generate Questions" if not st.session_state.generate_pressed else "Generate New Question Paper"
if st.button(button_label):
    st.session_state.distribution = get_question_distribution(selected_topics, num_questions)
    st.session_state.questions = get_questions_from_db(class_selected, subject_selected, marks_per_question, st.session_state.distribution)
    st.session_state.generate_pressed = True

# Show only if questions are generated
if st.session_state.generate_pressed:
    st.write("### Final Question Distribution")
    for topic, count in st.session_state.distribution.items():
        st.write(f"- {topic}: {count} questions")

    st.write("### Selected Questions")
    for q in st.session_state.questions:
        st.write(q)