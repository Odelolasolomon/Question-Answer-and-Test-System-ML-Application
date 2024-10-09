# Question Answering and Evaluation System

This project is a **Question Answering System** built with **Flask** and utilizes **transformer models** for **question answering**, **text summarization**, and **answer evaluation**. The project also includes a **PostgreSQL** database to store documents and corresponding test questions and answers.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [API Endpoints](#api-endpoints)
- [Models and Techniques](#models-and-techniques)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Flask application uses pre-trained models for question answering and summarization, and a sentence similarity model for evaluating the correctness of user responses. The system enables users to upload documents, query questions, and evaluate their answers based on similarity with model-generated answers.

The following models are used in the project:
- **BERT** for Question Answering
- **T5** for Summarization
- **Sentence Transformer** for Sentence Similarity

Additionally, we employ a PostgreSQL database to store documents and test questions.

## Installation

To run this project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/qa-system.git
   cd <put project directory here>
   ```
2. **Set up a virtual environment(you can also do this in your VScode or via your command prompt**
   ```cmd
   - python -m venv venv
   - source venv/bin/activate  # For Linux/Mac
   - venv\Scripts\activate  # For Windows
   ```
  
4. **Install dependencies**
   ``` cmd
   pip install -r requirements.txt
   - Flask
   - Flask-CORS
   - transformers
   - torch
   - sentence-transformers
   - Flask-SQLAlchemy
   - psycopg2-binary
   ```
  
  Configure PostgreSQL:

4. **Ensure PostgreSQL or any preferred database of your choice and is installed and running, and create a database called qat(could use any other name too)**
- CREATE DATABASE qat;

5. Set up the envioronment variables(for security purpose you can set it up in a .env file)
   ```python
   - DATABASE_URL=postgresql://<username>:<password>@localhost/qat
   ---
   

7. Create sql tables for the system(Document and TestQuestion are the tables created)
  

- **Document and Question Table**

```SQL
CREATE TABLE Document (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL
);


CREATE TABLE TestQuestion (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    correct_answer TEXT NOT NULL,
    document_id INT REFERENCES Document(id) ON DELETE CASCADE
);
```

## API Endpoints
``` python
  **Root (/)**
- Description: Returns a welcome message.
- Method: GET

{
  "message": "Welcome to the Question Answering API!"
}

 **Upload a Document (/upload/)**
- Description: Uploads a document and stores it in the database.
- Method: POST
- file: <Your file>

- Response will be :
{
  "message": "Document uploaded successfully!",
  "document_id": <document_id>
} 

 **Query a Question (/query/)**
- Description: Queries a question and generates an answer, a summary, and a test question.
- Method: POST

- Payload (JSON):
-  {
  "document_id": <document_id>,
  "question": "What is the main idea of the document?"
}

- Response
  {
  "answer": "<Generated Answer>",
  "bullet_points": "- Summary point 1", "- Summary point 2",
  "test_question": "<Generated Test Question>",
  "test_question_id": <test_question_id>
}

 **Evaluate an Answer (/evaluate/)**
- Description: Evaluates a user-provided answer by comparing it to the correct answer.
- Method: POST

- Payload (JSON):
  {
  "user_answer": "The main idea is...",
  "test_question_id": <test_question_id>
}
- Response
  {
  "knowledge_understood": true,
  "knowledge_confidence": 85.6
}
```

## Models and Techniques
 **Question Answering (BERT)**
- For question answering, I used a pre-trained BERT model, specifically bert-base-uncased. The model takes in the document context and the user's question to predict the answer. Here's the basic logic:
  ```python
 inputs = qa_tokenizer.encode_plus(question, context, return_tensors="pt")
 outputs = qa_model(**inputs)
 start_index = torch.argmax(outputs.start_logits)
 end_index = torch.argmax(outputs.end_logits)
 
 


 ## Summarization (T5)
- I used T5-small for summarization. Given a text, it generates a concise summary that we format as bullet points:
  ```python
 inputs = summarization_tokenizer.encode("summarize: " + text, return_tensors="pt")
 summary_ids = summarization_model.generate(inputs, max_length=100, num_beams=4)
 summary = summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
 

## Answer Evaluation (Sentence Transformer)
- To evaluate the user's answer, I calculated the cosine similarity between the user-provided answer and the correct answer using SentenceTransformer (all-MiniLM-L6-v2):
  
  ```python
 user_embedding = similarity_model.encode(user_answer, convert_to_tensor=True)
 correct_embedding = similarity_model.encode(correct_answer, convert_to_tensor=True)
 similarity_score = util.pytorch_cos_sim(user_embedding, correct_embedding).item()


**Note: If the similarity score exceeds 0.7, the answer is considered correct.**

**Usage**
- Once the project is up and running, you can interact with the API using tools like Postman or cURL. Follow the steps outlined in the API section to upload documents, query questions, and evaluate answers.


### Notes:

1. This README includes instructions on installation, database setup, API endpoints, and the models used.
2. LaTeX-like syntax (`$...$`) is not used here because GitHub's Markdown renderer does not support true LaTeX. Instead, I avoided complex math equations and used regular text formatting to keep everything GitHub-compatible.
3. The README is developer-friendly and offers enough detail for collaborators to quickly get started.



