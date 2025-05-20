import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException,Request
from agents.preprocessing import preprocess_text
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agents.brd import generate_brd_from_text
import os
import json
import shutil
import tempfile
from dotenv import load_dotenv
from agents.ingestion import parse_pdf
from agents.validation_agent import log_feedback, summarize_feedback, Feedback
from agents.summarization_agent import summarize_content
from agents.requirement_generation_agent import generate_requirements
from agents.compliance_agent import check_requirement_compliance
from agents.governance_agent import gov_agent
from agents.ingestion import parse_pdf
from agents.compliance_agent import check_requirement_compliance
from agents.match_compliance_rules import extract_and_match_vs_excel
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import tempfile
from agents.brd import generate_brd  
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
def run_compliance(text: str):
    try:
        result = check_requirement_compliance(text)
        return result, None
    except Exception as e:
        return None, str(e)
def run_compliance_check(requirements_file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(requirements_file.file, tmp)
            tmp_path = tmp.name

        extracted_text = parse_pdf(tmp_path)
        os.remove(tmp_path)

        result = check_requirement_compliance(extracted_text)
        return result, None

    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return None, str(e)
class MatchRequest(BaseModel):
    gpt_response_text: str
    
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

@app.post("/ingestion")
async def parse(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        text = parse_pdf(tmp_path)
        os.remove(tmp_path)
        return {"text":text}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
 



# @app.post("/generate-brd-and-rules")
# async def generate_brd_and_rules(file: UploadFile = File(...)):
#     try:
       
#         temp_dir = tempfile.mkdtemp()
        
        
#         input_pdf_path = os.path.join(temp_dir, "input.pdf")
#         with open(input_pdf_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)
        
#         extracted_text = parse_pdf(input_pdf_path)
        
      
#         rules_content = generate_brd_from_text(extracted_text)
        
       
        
#         rules_filename = f"compliance_rules.json"
#         rules_path = os.path.join("compliance_rules", rules_filename)
        
        
#         os.makedirs("compliance_rules", exist_ok=True)
        
       
#         with open(rules_path, "w") as f:
#             json.dump({"rules": rules_content}, f, indent=2)
        
       
#         return {
#             "status": "success",
#             "rules": rules_content,
#             "rules_file": rules_filename,
#             "rules_path": rules_path,
#             "message": "BRD processing complete and compliance rules generated"
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
       
#         if 'temp_dir' in locals():
#             shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/generate-brd/")
async def generate_brd_endpoint(
    prompt: str = Form(None),
    compliance_result: str = Form(None),
    file: UploadFile = File(None),
    template_file: UploadFile = File(None)
    ):
    try:
        if not prompt and not file:
            return JSONResponse(status_code=400, content={"error": "Provide either a prompt or a PDF file."})

        # Parse compliance_result from JSON string to dict
        compliance_data = None
        if compliance_result:
            compliance_data = json.loads(compliance_result)

        # Save optional template
        template_path = None
        if template_file:
            if not template_file.filename.endswith(".pdf"):
                return JSONResponse(status_code=400, content={"error": "Only PDF templates are allowed."})
            temp_template_path = Path(f"uploads/templates/{template_file.filename}")
            temp_template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_template_path, "wb") as buffer:
                shutil.copyfileobj(template_file.file, buffer)
            template_path = temp_template_path

        # Save uploaded file if present
        if file:
            upload_path = Path(f"uploads/{file.filename}")
            upload_path.parent.mkdir(parents=True, exist_ok=True)
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            result = generate_brd(upload_path, template_file=template_path, compliance_data=compliance_data)
        else:
            result = generate_brd(prompt, template_file=template_path, compliance_data=compliance_data)

        return JSONResponse({
            "brd_text": result["brd_text"],
            "pdf_download_url": "/download-brd/"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download-brd/")
def download_brd_pdf():
    pdf_path = Path("generated_pdf/generated_brd.pdf")
    if not pdf_path.exists():
        return JSONResponse(status_code=404, content={"error": "Generated BRD PDF not found."})

    return FileResponse(
        path=str(pdf_path),
        filename="generated_brd.pdf",
        media_type="application/pdf"
    )




@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)) -> Dict:
    try:
        # Save the uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse the PDF to extract text
        text = parse_pdf(tmp_path)
        
        # Preprocess the extracted text
        processed_output = preprocess_text(text)
        
        # Clean up the temporary file
        os.remove(tmp_path)
        
        # Log with governance agent
        gov_agent("preprocess", text, processed_output)
        
        return processed_output
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/summarize-content")
async def summarize_endpoint(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse the PDF to extract text
        text = parse_pdf(tmp_path)
        
        # Summarize the extracted text
        summary = summarize_content(text)
        
        # Clean up the temporary file
        os.remove(tmp_path)
        
        # Log with governance agent
        gov_agent("summarize", text, summary)
        
        return {"summary": summary}
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/generate-requirements")
async def requirement_endpoint():
    try:
        requirements = generate_requirements()
        gov_agent("requirement","N/A",requirements)
        return {"requirements": requirements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-compliance")
async def check_compliance_api(requirements_file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await requirements_file.read())
            tmp_path = tmp.name

        requirement_text = parse_pdf(tmp_path)  # Pass file path to parse_pdf
        response = check_requirement_compliance(requirement_text)
        return JSONResponse(content={"result": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/compliance-gap-analysis")
async def compliance_gap_analysis(requirements_file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await requirements_file.read())
            tmp_path = tmp.name

        # Step 2: Extract raw text from PDF
        requirement_text = parse_pdf(tmp_path)

        # Step 3: Use GPT to generate compliance response
        gpt_compliance_output = check_requirement_compliance(requirement_text)

        # Step 4: Extract and match rules using GPT semantic comparison
        comparison_result = extract_and_match_vs_excel(gpt_compliance_output)

        # Return results
        return JSONResponse(content={
            "compliance_analysis": gpt_compliance_output,
            "semantic_gap_analysis": comparison_result
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


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



# '''


@app.post("/run-full-pipeline")
async def run_full_pipeline(
    file: UploadFile = File(...),
    prompt: str = Form(None),
    template_file: UploadFile = File(None)
):
    try:
        # Step 1: Save uploaded file to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Step 2: Ingestion
        extracted_text = parse_pdf(tmp_path)
        os.remove(tmp_path)
        data = {"text": extracted_text}
        gov_agent("ingestion", "raw-pdf", extracted_text)

        # Step 3: Preprocessing
        processed = preprocess_text(extracted_text)
        data["preprocessed"] = processed
        gov_agent("preprocess", extracted_text, processed)

        # Step 4: Summarization
        summary = summarize_content(processed)
        data["summary"] = summary
        gov_agent("summarize", processed, summary)

        # Step 5: Requirement Generation
        requirements = generate_requirements()
        data["requirements"] = requirements
        gov_agent("requirement", "N/A", requirements)

        # Step 6: Compliance Checking
        compliance = check_requirement_compliance(requirements)
        data["compliance_result"] = compliance
        gov_agent("compliance", requirements, compliance)

        # Step 7: BRD & PDF Generation
        template_path = None
        if template_file:
            if not template_file.filename.endswith(".pdf"):
                return JSONResponse(status_code=400, content={"error": "Only PDF templates are allowed."})
            template_path = Path(f"uploads/templates/{template_file.filename}")
            template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(template_path, "wb") as f:
                shutil.copyfileobj(template_file.file, f)

        # Use prompt if available, else extracted PDF text
        brd_input = prompt if prompt else extracted_text
        result = generate_brd(brd_input, template_file=template_path)

        data["brd_text"] = result["brd_text"]
        data["pdf_download_url"] = "/download-brd/"
        data["message"] = "Full pipeline and BRD PDF generation complete"

        os.makedirs("src", exist_ok=True)
        with open("src/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

#---------second part of the code --------
@app.post("/full-compliance-pipeline")
async def full_compliance_pipeline(file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        input_pdf_path = os.path.join(temp_dir, "input.pdf")
        with open(input_pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Step 2: Extract text from PDF
        extracted_text = parse_pdf(input_pdf_path)

        # Step 3: Generate BRD (text + PDF)
        brd_result = generate_brd(extracted_text)  # returns dict with 'brd_text'
        brd_text = brd_result.get("brd_text", "")
        pdf_path = "generated_pdf/generated_brd.pdf"

        # Step 4: Run Compliance Check using GPT
        compliance_result = check_requirement_compliance(extracted_text)

        # Step 5: LLM-Based Semantic Rule Extraction + Matching Against Excel
        match_result = extract_and_match_vs_excel(compliance_result)

        # Final JSON Response
        return JSONResponse(content={
            "status": "✅ Full pipeline completed",
            "extracted_text": extracted_text,
            "brd_text": brd_text,
            "pdf_download_url": "/download-brd/",
            "compliance_result": compliance_result,
            "semantic_gap_analysis": match_result
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
