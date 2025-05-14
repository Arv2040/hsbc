from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from summarization_agent import summarize_content
from requirement_generation_agent import generate_requirements

app = FastAPI(title="SME Feedback Agent System")

# Enable CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model for summarization
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
