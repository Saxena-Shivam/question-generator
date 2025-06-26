from pymongo import MongoClient
import os
from dotenv import load_dotenv
import random

# --- MongoDB Setup ---
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection_academic = client["Academic"]["chapters"]  # Changed collection name

# --- New Schema: academic ---
"""
Each document:
{
    "class": 6,
    "subject_name": "Mathematics",
    "subject_code": "ma",
    "chapters": [
        {
            "chapter_name": "Knowing Our Numbers",
            "weightage": 10,
            "difficulty": 0.4
        },
        ...
    ]
}
"""

# --- Source Data ---
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

# --- Example weightage/difficulty pools (customize as needed) ---
weightage_pool = [10, 12, 14, 15, 18, 20, 25]
difficulty_pool = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def insert_class_chapters():
    for subj in subjects:
        for class_num, chapters in subj["chapters_by_class"].items():
            chapter_list = []
            for chapter in chapters:
                # Assign random weightage and difficulty for demo; customize as needed
                weightage = random.choice(weightage_pool)
                difficulty = random.choice(difficulty_pool)
                chapter_list.append({
                    "chapter_name": chapter,
                    "weightage": weightage,
                    "difficulty": difficulty
                })
            doc = {
                "class": class_num,
                "subject_name": subj["subject_name"],
                "subject_code": subj["subject_code"],
                "chapters": chapter_list
            }
            collection_academic.update_one(
                {"class": class_num, "subject_code": subj["subject_code"]},
                {"$set": doc},
                upsert=True
            )
            print(f"Inserted/Updated: Class {class_num} {subj['subject_name']}")

if __name__ == "__main__":
    insert_class_chapters()
    print("All class-chapter data inserted successfully.")