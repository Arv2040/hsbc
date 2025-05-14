from fastapi import FastAPI, UploadFile, File
from preprocessing import preprocess_text
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
from dotenv import load_dotenv
from validation_agent import log_feedback, summarize_feedback, Feedback

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)) -> Dict:
    text = await file.read()
    processed_output = preprocess_text(text.decode("utf-8"))
    return processed_output

# Submit SME feedback
@app.post("/submit-feedback")
async def submit_feedback(feedback: Feedback):
    try:
        log_feedback(feedback)
        return JSONResponse(content={"message": "Feedback submitted successfully."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Get full feedback log
@app.get("/feedback-log")
async def get_feedback_log():
    feedback_log_path = os.getenv("FEEDBACK_LOG", "feedback_logs.json")
    if not os.path.exists(feedback_log_path):
        return JSONResponse(content={"log": []})
    with open(feedback_log_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    return JSONResponse(content={"log": data})

# Get AI summary of SME feedback
@app.post("/ai-summarize")
async def ai_summarize_feedback(feedback: Feedback):
    try:
        summary = summarize_feedback(feedback)
        return JSONResponse(content={"summary": summary})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
