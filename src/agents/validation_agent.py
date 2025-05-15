import json
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Feedback data model
class Feedback(BaseModel):
    document_id: str
    reviewer: str
    comments: str
    edits: str
    approved: bool

# Load log file path from environment
FEEDBACK_LOG_PATH = os.getenv("FEEDBACK_LOG", "feedback_logs.json")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def log_feedback(feedback: Feedback):
    if not os.path.exists(FEEDBACK_LOG_PATH):
        with open(FEEDBACK_LOG_PATH, "w") as f:
            json.dump([], f)
    with open(FEEDBACK_LOG_PATH, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    data.append(feedback.dict())
    with open(FEEDBACK_LOG_PATH, "w") as f:
        json.dump(data, f, indent=4)

def summarize_feedback(feedback: Feedback) -> str:
    prompt = (
        f"Summarize this SME feedback: Document ID: {feedback.document_id}, "
        f"Reviewer: {feedback.reviewer}, Comments: {feedback.comments}, "
        f"Edits: {feedback.edits}, Approved: {feedback.approved}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a summarization assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content.strip()
