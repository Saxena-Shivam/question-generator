# Question Paper Generator

This project is a **Question Paper Generator** web application built with [Streamlit](https://streamlit.io/) and Python. It allows users (teachers, educators, or students) to generate question papers for different classes, subjects, and topics, using both a database of real questions and AI-generated questions.

---

## Features

- **Select Class, Subject, and Topics**  
  Choose from available classes, subjects, and topics to generate a custom question paper.

- **Fetch Real Questions from Database**  
  Pulls descriptive, MCQ, fill-in-the-blank, and true/false questions from a MongoDB database.

- **AI-Generated Questions**  
  Uses the Groq API (LLM) to generate new questions based on textbook content if not enough real questions are available.

- **Textbook Content Integration**  
  Fetches topic-wise textbook content from the database to provide context for AI question generation.

- **Customizable Distribution**  
  Distributes questions across selected topics as per user input.

---

## Technologies Used

- **Python**
- **Streamlit** (for the web UI)
- **MongoDB** (for storing questions and textbook content)
- **Groq API** (for AI question generation)
- **python-dotenv** (for environment variable management)

---

## Setup Instructions

1. **Clone the repository**

   ```sh
   git clone https://github.com/Saxena-Shivam/question-generator.git
   cd question-generator
   ```

2. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

   _(Or manually: `pip install streamlit pymongo groq python-dotenv`)_

3. **Set up your `.env` file**  
   Create a `.env` file (or edit the provided one) with your API keys:

   ```
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Configure MongoDB**  
   Make sure your MongoDB URI and database/collection names in the code match your setup.

5. **Run the app**
   ```sh
   streamlit run app.py
   ```

---

## Folder Structure

```
.
├── app.py                # Main Streamlit app
├── add_textbook.py       # Script to add textbook content to MongoDB
├── textbook.json         # Source data for textbook content
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
└── ...                   # Other scripts and data files
```

---

## Usage

1. Open the app in your browser.
2. Select the class, subject, and topics.
3. Choose the number and type of questions.
4. Generate the question paper with a mix of real and AI-generated questions.

---

## License

This project is for educational and demonstration purposes.

---

\*\*Contributions and suggestions
