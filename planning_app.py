import streamlit as st
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fpdf import FPDF

# --- MongoDB Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_study_plans = client["Students"]["study_plans"]
collection_chapters = client["Academic"]["chapters"]
collection_exams = client["Academic"]["exams"]
collection_students = client["Students"]["students"]

st.set_page_config(page_title="Personalized Study Planner", layout="centered")
st.title("📚 Personalized Study Planner")

# --- Student selection ---
students = list(collection_students.find({}, {"_id": 0}))
student_names = [f"{s['name']} (Class {s['class']}, Roll {s['roll_number']})" for s in students]
student_idx = st.selectbox("Select Student", range(len(students)), format_func=lambda i: student_names[i])
student = students[student_idx]
class_num = student["class"]

# --- Exam selection (no subject selection) ---
exam_docs = list(collection_exams.find({"class": class_num}, {"_id": 0, "exam_type": 1, "subject_code": 1, "syllabus": 1}))
exam_type_to_subjects = {}
for e in exam_docs:
    etype = e["exam_type"]
    if etype not in exam_type_to_subjects:
        exam_type_to_subjects[etype] = []
    exam_type_to_subjects[etype].append({
        "subject_code": e["subject_code"],
        "syllabus": e.get("syllabus", [])
    })

exam_type_labels = [et.replace("_", " ").title() for et in exam_type_to_subjects.keys()]
exam_type_keys = list(exam_type_to_subjects.keys())
exam_type_label = st.selectbox("Select Exam", exam_type_labels)
selected_exam_type = exam_type_keys[exam_type_labels.index(exam_type_label)]
subjects_in_exam = exam_type_to_subjects[selected_exam_type]
days_left = st.number_input("Days Left Until Exam", min_value=1, max_value=60, value=10)
hours_per_day = st.number_input("Study Hours Per Day", min_value=1, max_value=12, value=2)

def get_chapter_info(class_num, subject_code):
    doc = collection_chapters.find_one({"class": class_num, "subject_code": subject_code})
    if not doc or "chapters" not in doc:
        return {}
    return {ch["chapter_name"]: {"weightage": ch.get("weightage", 1), "difficulty": ch.get("difficulty", 0.5)} for ch in doc["chapters"]}

def get_past_performance(student_id, subject, topic, selected_exam_type):
    student_doc = collection_students.find_one({"student_id": student_id})
    if not student_doc or "exams" not in student_doc:
        return 0.5

    # Define exam order
    exam_order = ["term1", "mid_term", "term2", "end_term"]
    if selected_exam_type not in exam_order:
        return 0.5
    selected_idx = exam_order.index(selected_exam_type)

    # Only consider exams before the selected exam
    past_exams = [
        exam for exam in student_doc["exams"]
        if exam.get("exam_type") in exam_order[:selected_idx]
        and exam.get("subject") == subject
    ]
    # Sort by exam order (oldest to newest)
    past_exams.sort(key=lambda x: exam_order.index(x.get("exam_type", "")))

    # Collect all scores for this topic from past exams (in order)
    topic_scores = []
    for exam in past_exams:
        for t in exam.get("topic_scores", []):
            if t["topic"] == topic and t.get("max_marks", 0) > 0:
                percent = t.get("marks_obtained", 0) / t["max_marks"]
                topic_scores.append(percent)

    # Use only the last two scores (if available)
    last_two = topic_scores[-2:]
    return round(sum(last_two) / len(last_two), 2) if last_two else 0.5

def create_study_plan_pdf(student, exam_type_label, days_left, hours_per_day, total_hours, all_subject_plans):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Personalized Study Plan", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 10, f"Student: {student['name']} (Class {student['class']}, Roll {student['roll_number']})", ln=True)
    pdf.cell(0, 10, f"Exam: {exam_type_label}", ln=True)
    pdf.cell(0, 10, f"Days Left: {days_left} | Hours/Day: {hours_per_day} | Total Hours: {total_hours}", ln=True)
    pdf.ln(5)
    for subj_plan in all_subject_plans:
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, f"Subject: {subj_plan['subject']}", ln=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 8, "Chapter", 1)
        pdf.cell(20, 8, "Weight", 1)
        pdf.cell(25, 8, "Difficulty", 1)
        pdf.cell(25, 8, "Past Perf.", 1)
        pdf.cell(30, 8, "Learning", 1)
        pdf.cell(25, 8, "Rev1", 1)
        pdf.cell(25, 8, "Rev2", 1)
        pdf.ln()
        pdf.set_font("Arial", "", 10)
        for p in subj_plan["plan"]:
            pdf.cell(40, 8, str(p["chapter"]), 1)
            pdf.cell(20, 8, str(p["weightage"]), 1)
            pdf.cell(25, 8, str(p["difficulty"]), 1)
            pdf.cell(25, 8, str(p["past_performance"]), 1)
            pdf.cell(30, 8, str(p["learning_hours"]), 1)
            pdf.cell(25, 8, str(p["revision1_hours"]), 1)
            pdf.cell(25, 8, str(p["revision2_hours"]), 1)
            pdf.ln()
        pdf.ln(2)
    return pdf.output(dest="S").encode("latin1")

def generate_study_plan_all_subjects(subjects_in_exam, student, class_num, total_hours):
    # Gather all chapters across all subjects for scoring
    chapter_items = []
    for subj_exam in subjects_in_exam:
        subject_code = subj_exam["subject_code"]
        subj_doc = collection_chapters.find_one({"class": class_num, "subject_code": subject_code}, {"subject_name": 1})
        subject_name = subj_doc["subject_name"] if subj_doc else subject_code
        syllabus = subj_exam.get("syllabus", [])
        chapter_info = get_chapter_info(class_num, subject_code)
        for ch in syllabus:
            info = chapter_info.get(ch, {"weightage": 1, "difficulty": 0.5})
            weightage = info["weightage"]
            difficulty = info["difficulty"]
            past_perf = get_past_performance(student["student_id"], subject_name, ch, selected_exam_type)
            if past_perf is None:
                past_perf = 0.5
            score = 0.5 * weightage + 0.3 * difficulty + 0.2 * (1 - past_perf)
            chapter_items.append({
                "subject": subject_name,
                "subject_code": subject_code,
                "chapter": ch,
                "weightage": weightage,
                "difficulty": difficulty,
                "past_performance": past_perf,
                "score": score
            })
    total_score = sum([c["score"] for c in chapter_items]) or 1
    # Distribute hours
    learning_hours = total_hours * 0.7
    revision1_hours = total_hours * 0.2
    revision2_hours = total_hours * 0.1
    for c in chapter_items:
        c["learning_hours"] = round(learning_hours * (c["score"] / total_score), 1)
        c["revision1_hours"] = round(revision1_hours * (c["score"] / total_score), 1)
        c["revision2_hours"] = round(revision2_hours * (c["score"] / total_score), 1)
    # Group back by subject for display and saving
    subject_plan_map = {}
    for c in chapter_items:
        if c["subject"] not in subject_plan_map:
            subject_plan_map[c["subject"]] = []
        subject_plan_map[c["subject"]].append(c)
    all_subject_plans = [{"subject": k, "plan": v} for k, v in subject_plan_map.items()]
    return all_subject_plans

if st.button("Generate Study Plan"):
    total_hours = days_left * hours_per_day
    all_subject_plans = generate_study_plan_all_subjects(subjects_in_exam, student, class_num, total_hours)
    # Save to DB for each subject
    for subj_plan in all_subject_plans:
        collection_study_plans.update_one(
            {
                "student_id": student["student_id"],
                "class": class_num,
                "subject": subj_plan["subject"],
                "exam_type": selected_exam_type
            },
            {
                "$set": {
                    "student_id": student["student_id"],
                    "name": student["name"],
                    "class": class_num,
                    "roll_number": student["roll_number"],
                    "subject": subj_plan["subject"],
                    "exam_type": selected_exam_type,
                    "days_left": days_left,
                    "hours_per_day": hours_per_day,
                    "plan": subj_plan["plan"]
                }
            },
            upsert=True
        )

    st.success("Study plan generated and saved for all subjects in this exam!")
    st.markdown("### Study Plan Breakdown")
    st.write(f"**Total Study Hours:** {total_hours}")
    for subj_plan in all_subject_plans:
        st.markdown(f"#### {subj_plan['subject']}")
        st.table([
            {
                "Chapter": p["chapter"],
                "Weightage": p["weightage"],
                "Difficulty": p["difficulty"],
                "Past Perf.": p["past_performance"],
                "Learning (hrs)": p["learning_hours"],
                "Revision 1 (hrs)": p["revision1_hours"],
                "Revision 2 (hrs)": p["revision2_hours"]
            }
            for p in subj_plan["plan"]
        ])
    # One PDF for all subjects
    pdf_bytes = create_study_plan_pdf(
        student, exam_type_label, days_left, hours_per_day, total_hours, all_subject_plans
    )
    st.download_button(
        label="Download Full Study Plan as PDF",
        data=pdf_bytes,
        file_name=f"study_plan_{student['name']}_{exam_type_label}.pdf",
        mime="application/pdf"
    )