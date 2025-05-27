import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException,Request
from agents.preprocessing import preprocess_text
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agents.brd import generate_brd_from_text
import os
import json
import shutil
import tempfile
import pandas as pd
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
from agents.remediation_agent import analyze_compliance_issues 
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.comp_gen_agent import generate_compliance_rules_llm
from pathlib import Path
import shutil
import tempfile
from agents.brd import generate_brd  
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


# Endpoint 1: Ingestion Agent
p = ""
@app.post("/ingestion")
async def parse(file: UploadFile = File(...)):
    try:
        global p
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        text = parse_pdf(tmp_path)
        p = text
        os.remove(tmp_path)
        return {"text":text}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
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
        global p
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse the PDF to extract text
        text = parse_pdf(tmp_path)
        
        # Preprocess the extracted text
        processed_output = preprocess_text(p)
        p = processed_output
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
        global p
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Parse the PDF to extract text
        text = parse_pdf(tmp_path)
        
        # Summarize the extracted text
        summary = summarize_content(p)
        p = summary
        
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
    

rules = ""




@app.post("/generate-compliance-rules")
async def generate_compliance_rules_endpoint(file: UploadFile = File(...)):
    try:
        global rules
        # Save uploaded BRD PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text from PDF
        brd_text = parse_pdf(tmp_path)

        # Generate compliance rules using LLM
        rules = generate_compliance_rules_llm(p)

        # Convert rules_text to list
        rules_list = [line.strip() for line in rules.split('\n') if line.strip()]

        # Save to Excel
        df = pd.DataFrame({'Compliance Rules': rules_list})
        excel_path = Path("outputs/compliance_rules.xlsx")
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(excel_path, index=False)

        return JSONResponse({
            "rules_text": rules,
            "download_url": "/download/compliance-rules"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Download endpoint
@app.get("/download/compliance-rules")
async def download_compliance_rules():
    file_path = "outputs/compliance_rules.xlsx"
    return FileResponse(path=file_path, filename="compliance_rules.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

remedies = " "
@app.post("/check-compliance")
async def check_compliance_api():
    try:
        global remedies
        requirement_text =rules  # Pass file path to parse_pdf
        response = check_requirement_compliance(requirement_text)
        remedies  = response
        return JSONResponse(content={"result": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate-remediation")
async def generate_remediation_endpoint():
    try:
        global remedies
        remedies = analyze_compliance_issues(remedies)
        rules_list = [line.strip() for line in remedies.split('\n') if line.strip()]
        df = pd.DataFrame({'Remedies': rules_list})

        # Save to Excel
        excel_path = Path("outputs/remediation.xlsx")
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(excel_path, index=False)

        return JSONResponse({
            "remedies": remedies,
            "download_url": "/download/remediation"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


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
