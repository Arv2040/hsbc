from fastapi import FastAPI, UploadFile, File, HTTPException,Request
from agents.preprocessing import preprocess_text
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
from dotenv import load_dotenv
from agents.validation_agent import log_feedback, summarize_feedback, Feedback
from agents.summarization_agent import summarize_content
from agents.requirement_generation_agent import generate_requirements
from agents.compliance_agent import check_requirement_compliance
from agents.governance_agent import gov_agent


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContentInput(BaseModel):
    document_id: str
    reviewer: str
    content: str
    approved: bool

# Endpoint 1: Summarization Agent
@app.post("/summarize-content")
async def summarize_endpoint(input_data: ContentInput):
    try:
        summary = summarize_content(input_data.content)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 2: Requirement Generation Agent
@app.get("/generate-requirements")
async def requirement_endpoint():
    try:
        requirements = generate_requirements()
        return {"requirements": requirements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    

    

@app.post("/check-compliance")
async def check_compliance_api(feedback:Feedback):
    try:
        
        result = check_requirement_compliance(feedback)
        return JSONResponse(content={"result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/governance-audit")
async def governance_audit_api(request: Request):
    try:
        data = await request.json()
        agent_name = data.get("agent_name", "")
        input_text = data.get("input_text", "")
        output_text = data.get("output_text", "")
        result = gov_agent(agent_name, input_text, output_text)
        return JSONResponse(content={"result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
