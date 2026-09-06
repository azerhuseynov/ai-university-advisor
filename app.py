# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import Advisor

app = FastAPI()

# one Advisor instance per visitor, kept in memory while the server runs
sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    question: str

@app.post("/chat")
def chat(req: ChatRequest):
    if req.session_id not in sessions:
        sessions[req.session_id] = Advisor()

    advisor = sessions[req.session_id]
    answer = advisor.ask(req.question)
    return {"answer": answer}

from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="static", html=True), name="static")