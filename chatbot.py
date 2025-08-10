from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import sqlite3
import datetime

# Initialize FastAPI app
app = FastAPI()

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define sample FAQ questions and answers
FAQ_QUESTIONS = [
    "What is your return policy?",
    "How can I track my order?",
    "Do you offer customer support?",
    "What payment methods do you accept?"
]

FAQ_ANSWERS = [
    "Our return policy lasts 30 days.",
    "You can track your order using the tracking link sent to your email.",
    "Yes, we offer 24/7 customer support.",
    "We accept credit cards, debit cards, and PayPal."
]

# Precompute the embeddings of FAQ questions
faq_embeddings = model.encode(FAQ_QUESTIONS, convert_to_tensor=True)

# Initialize SQLite database connection
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Request body schema
class ChatRequest(BaseModel):
    message: str

# Root route for testing
@app.get("/")
async def root():
    return {"message": "🤖 Chatbot API is running. Send POST requests to /chat."}

# Chat route
@app.post("/chat")
async def chat(request: ChatRequest):
    user_msg = request.message

    # Generate embedding for user message
    user_embedding = model.encode(user_msg, convert_to_tensor=True)

    # Perform semantic search
    hits = util.semantic_search(user_embedding, faq_embeddings, top_k=1)
    best_match_idx = hits[0][0]['corpus_id']
    response = FAQ_ANSWERS[best_match_idx]

    # Log the conversation
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO chat_logs (user_message, bot_response, timestamp) VALUES (?, ?, ?)",
        (user_msg, response, timestamp)
    )
    conn.commit()

    # Return the chatbot response
    return {"response": response}
