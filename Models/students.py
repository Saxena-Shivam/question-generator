from pymongo import MongoClient
import os
from dotenv import load_dotenv
import random

# --- Subject Structure for Reference ---
subjects = [
    {
        "subject_name": "Mathematics",
        "subject_code": "ma",
        "chapters_by_class": {
            6: ["Knowing Our Numbers", "Whole Numbers", "Integers"],
            7: ["Integers", "Fractions and Decimals", "Data Handling", "Algebra", "Perimeter and Area"],
            8: ["Linear Equations", "Understanding Quadrilaterals", "Mensuration"],
            9: ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations in Two Variables"],
            10: ["Real Numbers", "Pair of Linear Equations", "Quadratic Equations", "Statistics"]
        }
    },
    {
        "subject_name": "Science",
        "subject_code": "sc",
        "chapters_by_class": {
            6: ["Food: Where Does It Come From?", "Components of Food", "Separation of Substances"],
            7: ["Nutrition in Plants", "Nutrition in Animals", "Heat", "Motion and Time", "Electricity"],
            8: ["Crop Production", "Microorganisms", "Force and Pressure"],
            9: ["Matter in Our Surroundings", "Atoms and Molecules", "The Fundamental Unit of Life"],
            10: ["Chemical Reactions", "Acids, Bases and Salts", "Life Processes"]
        }
    },
    {
        "subject_name": "Social Science",
        "subject_code": "ss",
        "chapters_by_class": {
            6: ["Understanding Diversity", "Local Government", "Maps"],
            7: ["Democracy and Equality", "India's Neighbours", "State Government"],
            8: ["The Indian Constitution", "Judiciary", "Natural Resources"],
            9: ["Democratic Politics", "Climate", "Nazism and the Rise of Hitler"],
            10: ["Federalism", "Sectors of the Indian Economy", "Nationalism in India"]
        }
    }
]

# --- MongoDB Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_students = client["Students"]["students"]

def insert_or_update_student(student_id, class_num, roll_number, name):
    try:
        collection_students.update_one(
            {"student_id": student_id},
            {"$set": {"class": class_num, "roll_number": roll_number, "name": name}},
            upsert=True
        )
    except Exception as e:
        print("Error inserting/updating student:", e)

def add_exam_to_student(student_id, exam_dict):
    try:
        collection_students.update_one(
            {"student_id": student_id},
            {"$push": {"exams": exam_dict}},
            upsert=True
        )
    except Exception as e:
        print("Error adding exam:", e)

def fetch_last_two_exam_scores(student_id, subject, topic, upto_date=None):
    """
    Returns the last two percentage scores for a topic in a subject for a student,
    considering only exams before upto_date (if provided).
    Percentage is calculated on the fly.
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
                if t.get("max_marks", 0) > 0:
                    percent = round((t.get("marks_obtained", 0) / t["max_marks"]) * 100, 1)
                else:
                    percent = 0.0
                scores.append(percent)
    return scores[:2]

if __name__ == "__main__":
    print("Deleting all previous students data...")
    collection_students.delete_many({})
    print("All previous students deleted.")

    student_list = [
        {"student_id": "S001", "name": "Alice", "class": 8, "roll": 12},
        {"student_id": "S002", "name": "Bob", "class": 7, "roll": 5},
        {"student_id": "S003", "name": "Charlie", "class": 9, "roll": 8},
        {"student_id": "S004", "name": "Diana", "class": 10, "roll": 3},
        {"student_id": "S005", "name": "Eve", "class": 6, "roll": 1},
    ]

    # Define exams and how much syllabus each covers (as number of topics)
    exam_types = [
        {"exam_id": "term1_2025", "exam_type": "term1", "date": "2025-05-01", "syllabus_topics": 1},
        {"exam_id": "midterm_2025", "exam_type": "mid_term", "date": "2025-07-01", "syllabus_topics": 2},
        {"exam_id": "term2_2025", "exam_type": "term2", "date": "2025-09-01", "syllabus_topics": 3},
        {"exam_id": "endterm_2025", "exam_type": "end_term", "date": "2025-12-01", "syllabus_topics": None},  # All topics
    ]

    for student in student_list:
        insert_or_update_student(student["student_id"], student["class"], student["roll"], student["name"])
        for subj in subjects:
            topics = subj["chapters_by_class"][student["class"]]
            total_topics = len(topics)
            for exam_info in exam_types:
                # Determine how many topics to include for this exam
                if exam_info["exam_type"] == "term1":
                    topics_for_exam = topics[:1]  # Only first chapter
                elif exam_info["exam_type"] == "mid_term":
                    topics_for_exam = topics[:2]  # First two chapters
                elif exam_info["exam_type"] == "term2":
                    topics_for_exam = topics[2:3] if total_topics >= 3 else []  # Only third chapter if exists
                elif exam_info["exam_type"] == "end_term":
                    topics_for_exam = topics      # All chapters
                else:
                    topics_for_exam = topics[:exam_info["syllabus_topics"]]

                # Set max_marks based on exam_type
                if exam_info["exam_type"] == "term1":
                    max_marks = 20
                elif exam_info["exam_type"] == "mid_term":
                    max_marks = 80
                elif exam_info["exam_type"] == "term2":
                    max_marks = 20
                elif exam_info["exam_type"] == "end_term":
                    max_marks = 80
                else:
                    max_marks = 20

                n = len(topics_for_exam)
                indices = list(range(n))
                random.shuffle(indices)
                split1 = n // 3
                split2 = 2 * n // 3

                topic_scores = []
                for idx, topic in enumerate(topics_for_exam):
                    if idx in indices[:split1]:
                        marks_obtained = random.randint(0, int(0.5 * max_marks))
                    elif idx in indices[split1:split2]:
                        marks_obtained = random.randint(int(0.5 * max_marks) + 1, int(0.75 * max_marks))
                    else:
                        marks_obtained = random.randint(int(0.75 * max_marks) + 1, max_marks)
                    topic_scores.append({
                        "topic": topic,
                        "marks_obtained": marks_obtained,
                        "max_marks": max_marks
                    })
                exam_dict = {
                    "exam_id": f"{exam_info['exam_id']}_{subj['subject_code']}",
                    "exam_type": exam_info["exam_type"],
                    "date": exam_info["date"],
                    "subject": subj["subject_name"],
                    "topic_scores": topic_scores
                }
                add_exam_to_student(student["student_id"], exam_dict)
    print("All students Data inserted successfully.")