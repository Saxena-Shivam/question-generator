import random
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
groq_api_key = os.getenv("GROQ_API_KEY")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["Questions"]
subjects_collection = db["subjects"]
subjects_collection.delete_many({})  # Clear previous data if needed

# Groq client
groq_client = Groq(api_key=groq_api_key)

# Class-wise subject & chapter data
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
            7: ["Nutrition in Plants", "Heat", "Motion and Time", "Electricity"],
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
            7: ["Democracy and Equality", "India’s Neighbours", "State Government"],
            8: ["The Indian Constitution", "Judiciary", "Natural Resources"],
            9: ["Democratic Politics", "Climate", "Nazism and the Rise of Hitler"],
            10: ["Federalism", "Sectors of the Indian Economy", "Nationalism in India"]
        }
    }
]

# Marks categories
mark_weights = [1, 2, 5, 10]

# Function to generate question-answer pair from Groq
def generate_qna(subject, chapter, class_level, marks):
    prompt = (
        f"Generate a Class {class_level} level exam question in {subject} from the chapter '{chapter}' worth {marks} marks. "
        f"Also give an ideal answer. Format:\nQuestion: <...>\nAnswer: <...>"
    )
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # or use "llama3-70b-8192"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        question, answer = "", ""
        for line in lines:
            if line.lower().startswith("question:"):
                question = line.split(":", 1)[1].strip()
            elif line.lower().startswith("answer:"):
                answer = line.split(":", 1)[1].strip()
            elif answer:
                answer += " " + line.strip()
        return question, answer
    except Exception as e:
        print(f"❌ Error from Groq: {e}")
        return "[Placeholder Question]", "[Placeholder Answer]"

# Loop through each class and subject
for class_level in range(6, 11):
    for subject in subjects:
        chapters = subject["chapters_by_class"].get(class_level, [])
        if not chapters:
            continue  # Skip if class-level chapters not defined

        topic_docs = []
        for chapter_name in chapters:
            questions = []
            for marks in mark_weights:
                for _ in range(random.randint(1, 3)):
                    q, a = generate_qna(subject["subject_name"], chapter_name, class_level, marks)
                    questions.append({
                        "question": q,
                        "answer": a,
                        "marks": marks
                    })
            topic_docs.append({
                "topic_name": chapter_name,
                "questions": questions
            })

        subjects_collection.insert_one({
            "class": class_level,
            "subject_name": subject["subject_name"],
            "subject_code": subject["subject_code"],
            "topics": topic_docs
        })

print("✅ Successfully inserted real Q&A data for Classes 6 to 10.")
