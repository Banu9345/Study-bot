# Study-bot
AI Study Bot using FastAPI and MongoDB
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import os

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# Initialize FastAPI
app = FastAPI(title="Study Bot API")

# MongoDB Setup
client = MongoClient(MONGODB_URI)
db = client["studybot_db"]
collection = db["chat_history"]

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# Request Model
class ChatRequest(BaseModel):
    user_id: str
    message: str

# Home Route
@app.get("/")
def home():
    return {"message": "Study Bot is Running 🚀"}

# Chat Endpoint
@app.post("/chat")
def chat(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message

    # Retrieve previous messages
    previous_chats = list(collection.find({"user_id": user_id}))

    messages = [
        SystemMessage(content="You are a helpful AI Study Assistant. Answer clearly and academically.")
    ]

    # Add previous messages
    for chat in previous_chats:
        messages.append(HumanMessage(content=chat["user_message"]))
        messages.append(AIMessage(content=chat["bot_response"]))

    # Add current message
    messages.append(HumanMessage(content=user_message))

    # Get AI response
    response = llm.invoke(messages)
    bot_reply = response.content

    # Store in MongoDB
    collection.insert_one({
        "user_id": user_id,
        "user_message": user_message,
        "bot_response": bot_reply
    })

    return {"response": bot_reply}

# Get Chat History
@app.get("/history/{user_id}")
def get_history(user_id: str):
    chats = list(collection.find({"user_id": user_id}, {"_id": 0}))
    return {"history": chats}
