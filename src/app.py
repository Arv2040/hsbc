from fastapi import FastAPI, UploadFile, File, HTTPException,Request
from agents.preprocessing import preprocess_text
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
import streamlit as st
from dotenv import load_dotenv
from agents.validation_agent import log_feedback, summarize_feedback, Feedback
from agents.summarization_agent import summarize_content
from agents.requirement_generation_agent import generate_requirements
from agents.compliance_agent import check_requirement_compliance
from agents.governance_agent import gov_agent

#--------- after dependencies ------
#import speech_recognition as sr
# from dotenv import load_dotenv
# from pydub import AudioSegment
# from ingestion import fetch_emails, parse_pdf, ocr_image, extract_metadata
# from faq_chatbot import main_chat
# from ingestion import fetch_emails, transcribe_audio, parse_pdf, ocr_image, extract_metadata
# from integration import (
#     create_jira_ticket,
#     push_to_sharepoint,
#     notify_slack,
#     generate_summary_from_openai
# )
# from pydantic import BaseModel
# import logging

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#streamlit
st.title("HSBC DATA PROCESSING")
uploaded_file = st.file_uploader("Upload a file", type=["txt", "csv", "pdf", "png", "jpg"])

    
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# class IntegrationPayload(BaseModel):
#     title: str
#     description: str
#     summary: str
# app = FastAPI(
#     title="Unified Document & Audio Processing API",
#     description="Handles emails, OCR, PDFs, audio transcription, and chatbot interaction",
#     version="1.0.0"
# )

# Endpoint 1: Ingestion Agent
# @app.get("/emails")
# async def get_emails():
#     try:
#         emails = fetch_emails()
#         return {"emails": emails}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


# @app.post("/transcript/", response_model=Dict[str, str])
# async def transcript(audio: UploadFile = File(...)) -> Dict[str, str]:
#     if audio.content_type not in ["audio/wav", "audio/x-wav", "audio/mpeg"]:
#         raise HTTPException(status_code=400, detail="Only .wav or .mp3 audio files are supported.")

#     temp_input_path = "temp_input_audio"
#     audio_ext = ".wav" if "wav" in audio.content_type else ".mp3"
#     input_file_path = temp_input_path + audio_ext
#     output_wav_path = "converted_audio.wav"

#     try:
#         # Save uploaded file
#         with open(input_file_path, "wb") as buffer:
#             shutil.copyfileobj(audio.file, buffer)

#         # ⚠️ Explicitly close the uploaded file before processing
#         audio.file.close()

#         # Convert mp3 to wav if needed
#         if audio_ext == ".mp3":
#             sound = AudioSegment.from_file(input_file_path, format="mp3")
#             sound.export(output_wav_path, format="wav")
#             audio_path = output_wav_path
#         else:
#             audio_path = input_file_path

#         # Transcribe
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(audio_path) as source:
#             recognizer.adjust_for_ambient_noise(source, duration=0.5)
#             audio_data = recognizer.record(source, duration=10)

#         transcript_text = recognizer.recognize_google(audio_data, language='en-IN')
#         full_question = "bank " + transcript_text

#         solution = main_chat(full_question, False)

#         return {
#             "Question": transcript_text,
#             "Solution": solution,
#             "Name": "Rohit Kumar",
#             "Email": "Rohit.Kumar3435@in.ey.com",
#             "Rating": "5"
#         }

#     except sr.UnknownValueError:
#         raise HTTPException(status_code=400, detail="Could not understand the audio.")
#     except sr.RequestError as e:
#         raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
#     finally:
#         # Clean up files
#         for path in [input_file_path, output_wav_path]:
#             if os.path.exists(path):
#                 try:
#                     os.remove(path)
#                 except PermissionError:
#                     pass  # Silently ignore if still locked

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
#         with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             tmp_path = tmp.name
#         text = ocr_image(tmp_path)
#         os.remove(tmp_path)
#         return {"text": text, "metadata": extract_metadata("image")}
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)



# Endpoint 2: Preprocessing Agent
@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)) -> Dict:
    text = await file.read()
    processed_output = preprocess_text(text.decode("utf-8"))
    gov_agent("preprocess",text,processed_output)
    return processed_output

# Endpoint 3: summarization Agent
@app.post("/summarize-content")
async def summarize_endpoint(input_data):
    try:
        summary = summarize_content(input_data)
        gov_agent("summarize",input_data,summary)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 4: Requirement Generation Agent
@app.get("/generate-requirements")
async def requirement_endpoint():
    try:
        requirements = generate_requirements()
        gov_agent("requirement","N/A",requirements)
        return {"requirements": requirements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 5: Compliance Mapping Agent
@app.post("/check-compliance")
async def check_compliance_api(feedback:Feedback):
    try:
        
        result = check_requirement_compliance(feedback)
        input_str = json.dumps(feedback.model_dump(), indent=2)
        gov_agent("compliance",input_str,result)
        return JSONResponse(content={"result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Endpoint 6: Validation Agent
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
            d = json.dumps(data)
            gov_agent("feedback","N/A",d)
        except json.JSONDecodeError:
            data = []
        
    return JSONResponse(content={"log": data})

# Get AI summary of SME feedback
@app.post("/ai-summarize")
async def ai_summarize_feedback(feedback: Feedback):
    try:
        summary = summarize_feedback(feedback)
        input_str = json.dumps(feedback.model_dump(), indent=2)
        gov_agent("summarize",input_str,summary)
        return JSONResponse(content={"summary": summary})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
# Endpoint 7: Integration Agent

#requires api keys
# '''
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
# '''



