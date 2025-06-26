import csv
from pymongo import MongoClient
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
# Get the MongoDB URI from the environment
mongo_uri = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["Questions"]
subjects_collection = db["subjects"]

output_file = "classwise_questions.csv"
all_rows = []

for subject in subjects_collection.find():
    class_level = subject["class"]
    subject_name = subject["subject_name"]
    subject_code = subject["subject_code"]

    for topic in subject["topics"]:
        topic_name = topic["topic_name"]
        for q in topic["questions"]:
            all_rows.append({
                "Class": class_level,
                "Subject Name": subject_name,
                "Subject Code": subject_code,
                "Topic": topic_name,
                "Question": q["question"],
                "Marks": q["marks"]
            })

# Write to CSV
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Class", "Subject Name", "Subject Code", "Topic", "Question", "Marks"])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"✅ Data exported to {output_file}")