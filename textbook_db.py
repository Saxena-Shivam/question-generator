from pymongo import MongoClient
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
# Get the MongoDB URI from the environment
mongo_uri = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(mongo_uri)

# Database and collection
collection_textbooks = client["Textbooks"]["content"]

def fetch_textbook_content(class_selected, subject_selected, topic):
    doc = collection_textbooks.find_one({
        "class": int(class_selected),
        "subject_name": subject_selected,
        "topic": topic
    })
    return doc["textbook"].strip() if doc and doc.get("textbook") else ""

result = fetch_textbook_content(7, "Social Studies", "k")
if result:
    print(result)
else:
    print("No textbook content found for the given class, subject, and topic.")
