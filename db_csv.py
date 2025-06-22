import csv
from pymongo import MongoClient

client = MongoClient("mongodb+srv://shivamsaxena562006:LZPRnz4ePeG7utqv@cluster0.7nvtxfb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
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