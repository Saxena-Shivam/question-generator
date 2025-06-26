from pymongo import MongoClient
import os
from dotenv import load_dotenv

# --- MongoDB Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_exams = client["Academic"]["exams"]  # One document per exam

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

exam_types = [
    {"exam_type": "term1", "marks": 20, "syllabus_count": 1},
    {"exam_type": "mid_term", "marks": 80, "syllabus_count": 2},
    {"exam_type": "term2", "marks": 20, "syllabus_count": None},  # Only 3rd chapter
    {"exam_type": "end_term", "marks": 80, "syllabus_count": None},  # All chapters
]

def insert_exams_academic():
    for subj in subjects:
        for class_num, chapters in subj["chapters_by_class"].items():
            total_chapters = len(chapters)
            for exam in exam_types:
                if exam["exam_type"] == "term2":
                    syllabus = [chapters[2]] if total_chapters >= 3 else []
                elif exam["syllabus_count"] is None or exam["syllabus_count"] > total_chapters:
                    syllabus = chapters
                else:
                    syllabus = chapters[:exam["syllabus_count"]]
                doc = {
                    "exam_id": f"{exam['exam_type']}_{class_num}_{subj['subject_code']}",
                    "class": class_num,
                    "subject_name": subj["subject_name"],
                    "subject_code": subj["subject_code"],
                    "exam_type": exam["exam_type"],
                    "marks": exam["marks"],
                    "syllabus": syllabus
                }
                collection_exams.update_one(
                    {
                        "class": class_num,
                        "subject_code": subj["subject_code"],
                        "exam_type": exam["exam_type"]
                    },
                    {"$set": doc},
                    upsert=True
                )
                print(f"Inserted/Updated: Class {class_num} {subj['subject_name']} {exam['exam_type']}")

if __name__ == "__main__":
    insert_exams_academic()
    print("All exam data inserted successfully.")