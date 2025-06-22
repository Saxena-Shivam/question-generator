import streamlit as st
from pymongo import MongoClient
import random
from openai import OpenAI
import os
from groq import Groq
from dotenv import load_dotenv
# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
groq_api_key = os.getenv("GROQ_API_KEY")
client1 = Groq(api_key=groq_api_key)
client = MongoClient("mongodb+srv://shivamsaxena562006:LZPRnz4ePeG7utqv@cluster0.7nvtxfb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_questions = client["Questions"]
collection_questions = db_questions["subjects"]
collection_textbooks = client["Textbooks"]["content"]

# Session state init
if "enter_pressed" not in st.session_state:
    st.session_state.enter_pressed = False
if "distribution" not in st.session_state:
    st.session_state.distribution = None
if "questions" not in st.session_state:
    st.session_state.questions = []
if "ai_questions" not in st.session_state:
    st.session_state.ai_questions = []
if "generate_pressed" not in st.session_state:
    st.session_state.generate_pressed = False

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

def get_question_distribution(topics, total_questions):
    try:
        k = len(topics)
        if k == 0:
            return {}
        base = total_questions // k
        remainder = total_questions % k

        random.shuffle(topics)
        distribution = {topic: base for topic in topics}
        for i in range(remainder):
            distribution[topics[i]] += 1

        return distribution
    except Exception as e:
        st.error(f"Error in question distribution: {e}")
        return {}

def get_questions_from_db(class_selected, subject_selected, mark, distribution_dict):
    result = []
    ai_counter = 1
    try:
        doc = collection_questions.find_one({"class": class_selected, "subject_name": subject_selected})
        if not doc:
            return []

        topic_dict = {t.get("topic_name", t.get("topic")): t["questions"] for t in doc["topics"]}

        for topic, count in distribution_dict.items():
            questions_with_mark = [
                q["question"] for q in topic_dict.get(topic, [])
                if q["marks"] == int(mark.replace("m", ""))
            ]
            available = len(questions_with_mark)
            try:
                selected = random.sample(questions_with_mark, min(count, available))
            except ValueError as ve:
                st.warning(f"Not enough questions for topic '{topic}': {ve}")
                selected = questions_with_mark

            if len(selected) < count:
                for _ in range(count - len(selected)):
                    selected.append(f"ai_{ai_counter}")
                    ai_counter += 1

            result.extend(selected)

        return result
    except Exception as e:
        st.error(f"Error fetching questions from DB: {e}")
        return []

def query_openrouter(messages):
    try:
        response = client1.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7
        )

        st.write("Debug - Raw API Response:", response)

        if not response or not hasattr(response, "choices") or not response.choices:
            return "Error: AI returned incomplete response (missing choices)"

        if not hasattr(response.choices[0], "message") or not response.choices[0].message:
            return "Error: AI returned incomplete response (missing message)"

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"

def generate_ai_question_from_text(context, question_type="mcq", num_questions=1, retries=1):
    prompts = {
        "Multiple Choice Questions (MCQs)": f"""Based on this content:
{context}

Generate {num_questions} multiple choice questions. For each question:
- Write the question
- Provide exactly 4 options labeled A), B), C), and D)
- Make sure one option is correct

Format each question exactly like this:
Question: [Question text]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]""",

        "Descriptive": f"""Based on this content:
{context}

Generate {num_questions} descriptive questions that require detailed answers. For each question:
- Focus on analysis and critical thinking
- Require explanation and reasoning

Format: Clear, numbered questions that prompt for detailed explanations.
Example:
1. Explain how [concept] affects [outcome] and analyze its implications.
2. Compare and contrast [elements] and evaluate their significance.""",

        "Fill in the Blanks": f"""Based on this content:
{context}

Generate {num_questions} fill-in-the-blank questions. For each:
- Create a sentence with a key term missing
- Put _____ for the blank
- Show the answer in brackets

Format each exactly like this:
1. The process of _____ helps in maintaining system integrity. [normalization]
2. Gerrard's plan involved using the _____ to escape. [cupboard]""",

        "True/False": f"""Based on this content:
{context}

Generate {num_questions} True/False questions. For each:
- Start each question with \"True or False:\"
- Write a clear, unambiguous question
- Make it directly related to the content

Format each exactly like this:
1. True or False: [Statement]
2. True or False: [Statement]"""
    }

    format_type_map = {
        "mcq": "Multiple Choice Questions (MCQs)",
        "descriptive": "Descriptive",
        "fill_blank": "Fill in the Blanks",
        "true_false": "True/False"
    }

    format_type = format_type_map.get(question_type, "mcq")
    context = context[:3000]  # truncate if too long

    last_error = ""
    for attempt in range(retries + 1):
        try:
            response = query_openrouter([
                {
                    "role": "system",
                    "content": f"You are a question generator for {format_type}. Generate questions in the exact format specified. No explanations or additional text."
                },
                {
                    "role": "user",
                    "content": prompts[format_type]
                }
            ])

            if not response or "Error" in response:
                last_error = response
                continue

            if question_type == "mcq" and (response.count("A)") < 1 or response.count("B)") < 1 or response.count("C)") < 1 or response.count("D)") < 1):
                last_error = "Error: AI returned incomplete MCQ (missing options)"
                continue

            if question_type == "fill_blank" and "_____" not in response:
                last_error = "Error: AI returned invalid Fill in the Blank format"
                continue

            if question_type == "true_false" and "True or False:" not in response:
                last_error = "Error: AI did not follow True/False format"
                continue

            return response.strip()
        except Exception as e:
            last_error = f"Error generating AI question: {e}"
            continue

    return last_error
# 🚀 Title
st.title("Question Paper Generator")

# 🔹 STEP 1 — Class, Subject, Topics
classes = sorted(collection_questions.distinct("class"))
class_selected = st.selectbox("Select Class", classes)

subject_cursor = collection_questions.find({"class": class_selected})
subject_names = sorted({doc["subject_name"] for doc in subject_cursor})
subject_selected = st.selectbox("Select Subject", subject_names)

topics_cursor = collection_questions.find_one({"class": class_selected, "subject_name": subject_selected})
available_topics = [topic["topic_name"] for topic in topics_cursor["topics"]] if topics_cursor else []
selected_topics = st.multiselect("Select Topics", available_topics)

# 👉 ENTER button to move to step 2
if st.button("ENTER"):
    st.session_state.enter_pressed = True

# 🔹 STEP 2 — After pressing ENTER
if st.session_state.enter_pressed:
    st.markdown("---")
    st.subheader("Additional Question Inputs")

    num_fill_blank = st.number_input("Number of Fill in the Blanks", min_value=0, step=1)
    num_mcqs = st.number_input("Number of MCQs", min_value=0, step=1)
    num_true_false = st.number_input("Number of True/False Questions", min_value=0, step=1)

    st.markdown("#### Descriptive Questions")

    if "descriptive_sets" not in st.session_state:
        st.session_state.descriptive_sets = []

    num_desc = st.number_input("Number of Descriptive Questions", min_value=0, step=1, key="desc_num")
    mark_desc = st.radio("Marks per Descriptive Question", ["1m", "2m", "4m", "5m", "10m", "20m"], key="desc_mark")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Add"):
            if num_desc > 0:
                st.session_state.descriptive_sets.append({"count": num_desc, "marks": mark_desc})
    with col2:
        if st.button("✅ Done"):
            st.session_state.generate_pressed = True

    if st.session_state.descriptive_sets:
        st.markdown("**Descriptive Question Sets Added:**")
        for i, d in enumerate(st.session_state.descriptive_sets):
            st.write(f"{i + 1}. {d['count']} questions of {d['marks']}")

    if st.session_state.generate_pressed:
        st.write("### Final Question Distribution")

        mcq_dist = get_question_distribution(selected_topics, num_mcqs)
        fill_dist = get_question_distribution(selected_topics, num_fill_blank)
        tf_dist = get_question_distribution(selected_topics, num_true_false)

        for topic in selected_topics:
            text = fetch_textbook_content(class_selected, subject_selected, topic)
            if not text:
                st.warning(f"No textbook content found for topic: {topic}")
                continue

            if mcq_dist[topic] > 0:
                mcq = generate_ai_question_from_text(text, question_type="mcq", num_questions=mcq_dist[topic])
                st.session_state.ai_questions.append(f"[MCQ] {mcq}")

        for topic in selected_topics:
            text = fetch_textbook_content(class_selected, subject_selected, topic)
            if not text:
                continue
            if fill_dist[topic] > 0:
                fb = generate_ai_question_from_text(text, question_type="fill_blank", num_questions=fill_dist[topic])
                st.session_state.ai_questions.append(f"[FillBlank] {fb}")

        for topic in selected_topics:
            text = fetch_textbook_content(class_selected, subject_selected, topic)
            if not text:
                continue
            if tf_dist[topic] > 0:
                tf = generate_ai_question_from_text(text, question_type="true_false", num_questions=tf_dist[topic])
                st.session_state.ai_questions.append(f"[True/False] {tf}")

        total_questions = sum(d["count"] for d in st.session_state.descriptive_sets)
        st.session_state.distribution = get_question_distribution(selected_topics, total_questions)

        all_questions = []
        for desc_set in st.session_state.descriptive_sets:
            dist = get_question_distribution(selected_topics, desc_set["count"])
            qs = get_questions_from_db(class_selected, subject_selected, desc_set["marks"], dist)

            for i, q in enumerate(qs):
                if q.startswith("ai_"):
                    topic = list(dist.keys())[i % len(dist)]
                    text = fetch_textbook_content(class_selected, subject_selected, topic)
                    if not text:
                        continue
                    ai_q = generate_ai_question_from_text(text, question_type="descriptive", num_questions=1)
                    all_questions.append(f"[Descriptive AI] {ai_q}")
                else:
                    all_questions.append(f"[Descriptive DB] {q}")

        st.session_state.questions = all_questions

        st.write("### AI-Generated Questions")
        for q in st.session_state.ai_questions:
            st.write(q)

        st.write("### Descriptive Questions")
        for q in st.session_state.questions:
            st.write(q)
