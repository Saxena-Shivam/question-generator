from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://shivamsaxena562006:LZPRnz4ePeG7utqv@cluster0.7nvtxfb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

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
