# import every library
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util
from flask_sqlalchemy import SQLAlchemy

# The flask app is initialized here, plus the CORS is enabled on the initialized app
app = Flask(__name__)
CORS(app)

# Configure PostgreSQL database(i advise creating a .env file for security purpose in production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:242129@localhost/qat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load pretrained models
qa_model_name = "bert-base-uncased"
summarization_model_name = "t5-small"

#initialize the tokenizers on the models
qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_name)
qa_model = AutoModelForQuestionAnswering.from_pretrained(qa_model_name)

summarization_tokenizer = AutoTokenizer.from_pretrained(summarization_model_name)
summarization_model = AutoModelForSeq2SeqLM.from_pretrained(summarization_model_name)

#initialize the similarity checker
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')


# Database Models
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)


class TestQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)

    document = db.relationship('Document', backref=db.backref('test_questions', lazy=True))


# Create the database tables
with app.app_context():
    db.create_all()


def answer_question(context, question):
    inputs = qa_tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    outputs = qa_model(**inputs)
    start_index = torch.argmax(outputs.start_logits)
    end_index = torch.argmax(outputs.end_logits)

    answer_tokens = inputs['input_ids'][0][start_index:end_index + 1]
    answer = qa_tokenizer.decode(answer_tokens, skip_special_tokens=True)
    return answer


def summarize_text(text):
    inputs = summarization_tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = summarization_model.generate(inputs, max_length=100, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    bullet_points = summary.split('. ')
    bullet_points = [f"- {point.strip()}" for point in bullet_points if point.strip()]
    return bullet_points


def generate_test_question(answer):
    templates = [
        f"What does the document say about {answer.split()[0]}?",
        "Can you summarize the main idea in one sentence?",
        f"Can you explain more about {answer.split()[0]}?",
        f"Why is {answer.split()[0]} important in the context of the document?"
    ]
    return random.choice(templates)


def evaluate_answer(user_answer, correct_answer):
    user_embedding = similarity_model.encode(user_answer, convert_to_tensor=True)
    correct_embedding = similarity_model.encode(correct_answer, convert_to_tensor=True)

    similarity_score = util.pytorch_cos_sim(user_embedding, correct_embedding).item()
    knowledge_understood = similarity_score > 0.7
    return knowledge_understood, similarity_score * 100

# Root route 
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Question Answering API!"}), 200


@app.route('/upload/', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        document_content = file.read().decode('utf-8')
        document = Document(content=document_content)
        db.session.add(document)
        db.session.commit()
        return jsonify({"message": "Document uploaded successfully!", "document_id": document.id}), 201
    return jsonify({"message": "No file uploaded."}), 400


@app.route('/query/', methods=['POST'])
def query():
    data = request.json
    document_id = data.get("document_id")
    question = data.get("question")

    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found."}), 404

    context = document.content
    answer = answer_question(context, question)
    bullet_points = summarize_text(answer)
    test_question = generate_test_question(answer)

    # Store the test question and answer in the database
    test_question_record = TestQuestion(question=test_question, correct_answer=answer, document_id=document_id)
    db.session.add(test_question_record)
    db.session.commit()

    response = {
        "answer": answer,
        "bullet_points": bullet_points,
        "test_question": test_question,
        "test_question_id": test_question_record.id
    }
    return jsonify(response), 200


@app.route('/evaluate/', methods=['POST'])
def evaluate():
    data = request.json
    user_answer = data.get("user_answer")
    test_question_id = data.get("test_question_id")

    test_question = TestQuestion.query.get(test_question_id)
    if not test_question:
        return jsonify({"message": "Test question not found."}), 404

    correct_answer = test_question.correct_answer
    knowledge_understood, knowledge_confidence = evaluate_answer(user_answer, correct_answer)

    response = {
        "knowledge_understood": knowledge_understood,
        "knowledge_confidence": knowledge_confidence
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
