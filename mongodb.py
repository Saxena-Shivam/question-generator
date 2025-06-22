import random
from pymongo import MongoClient

client = MongoClient("mongodb+srv://shivamsaxena562006:LZPRnz4ePeG7utqv@cluster0.7nvtxfb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Questions"]
subjects_collection = db["subjects"]

# Clear previous data (optional)
subjects_collection.delete_many({})

# Subject structure
subjects = [
    {"subject_name": "Mathematics", "subject_code": "ma", "topics": ["a", "b", "c", "d", "e"]},
    {"subject_name": "Biology", "subject_code": "bs", "topics": ["f", "g", "h", "i", "j"]},
    {"subject_name": "Social Studies", "subject_code": "ss", "topics": ["k", "l", "m", "n", "o"]}
]

# Marks pattern
mark_weights = [1, 2, 4, 5, 10, 20]

# Insert data for classes 6 to 10
for class_level in range(6, 11):
    for subject in subjects:
        topic_docs = []

        for topic_letter in subject["topics"]:
            questions = []
            for mark in mark_weights:
                num_questions = random.randint(1, 10)
                for q_num in range(1, num_questions + 1):
                    question_id = f"{subject['subject_code']}{topic_letter}{str(q_num).zfill(2)}{str(mark).zfill(2)}"
                    questions.append({"question": question_id, "marks": mark})

            topic_docs.append({
                "topic_name": topic_letter,
                "questions": questions
            })

        document = {
            "class": class_level,
            "subject_code": subject["subject_code"],
            "subject_name": subject["subject_name"],
            "topics": topic_docs
        }

        subjects_collection.insert_one(document)

print("✅ Data inserted for classes 6 to 10.")
