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
#----Reuires dependencies ---------------------------------------------------
# from integration import (
#     create_jira_ticket,
#     push_to_sharepoint,
#     notify_slack,
#     generate_summary_from_openai
# )
# from pydantic import BaseModel
# import logging
# from ingestion import fetch_emails, transcribe_audio, parse_pdf, ocr_image, extract_metadata
# import shutil

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------- Reuires Azure dependencies -----------------------
# @app.get("/emails")
# async def get_emails():
#     try:
#         emails = fetch_emails()
#         return {"emails": emails}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.post("/transcribe-audio")
# async def transcribe(file: UploadFile = File(...)):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename[-4:]) as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             tmp_path = tmp.name
#         transcript = transcribe_audio(tmp_path)
#         os.remove(tmp_path)
#         return {"transcript": transcript, "metadata": extract_metadata("audio")}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.post("/parse-pdf")
# async def parse(file: UploadFile = File(...)):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             tmp_path = tmp.name
#         text = parse_pdf(tmp_path)
#         os.remove(tmp_path)
#         return {"text": text, "metadata": extract_metadata("pdf")}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.post("/ocr-image")
# async def ocr(file: UploadFile = File(...)):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename[-4:]) as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             tmp_path = tmp.name
#         text = ocr_image(tmp_path)
#         os.remove(tmp_path)
#         return {"text": text, "metadata": extract_metadata("image")}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)
# ------------------------------------------------------------------------------------------------------

# --------------------------------Requires Several external APIS like Jira, Sharepoint , Slack -------------------------------
# class IntegrationPayload(BaseModel):
#     title: str
#     description: str
#     summary: str

# @app.post("/sync/jira")
# async def sync_jira(payload: IntegrationPayload):
#     try:
#         response = create_jira_ticket(payload.title, payload.description)
#         return {"status": "success", "ticket": response}
#     except Exception as e:
#         logging.error(f"Jira sync failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/sync/sharepoint")
# async def sync_sharepoint(payload: IntegrationPayload):
#     try:
#         result = push_to_sharepoint(payload.title, payload.description)
#         return {"status": "success", "result": result}
#     except Exception as e:
#         logging.error(f"SharePoint sync failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/notify/slack")
# async def notify(payload: IntegrationPayload):
#     try:
#         result = notify_slack(payload.summary)
#         return {"status": "notified", "result": result}
#     except Exception as e:
#         logging.error(f"Slack notification failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/generate/summary")
# async def generate_summary(payload: IntegrationPayload):
#     try:
#         result = generate_summary_from_openai(payload.description)
#         return {"summary": result}
#     except Exception as e:
#         logging.error(f"OpenAI summary generation failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


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
