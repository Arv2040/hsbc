from fastapi import Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from pathlib import Path
import openai
import shutil
import json
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


client = openai.AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_compliance_rules_llm(brd_text: str) -> str:
    prompt = f"""
You are an expert compliance analyst specializing in deriving Non-Functional Requirement (NFR) compliance rules from business requirement documents (BRDs).

**Your task:**  
Thoroughly analyze the provided BRD content and extract **clear, specific, and measurable NFR compliance rules**. The rules must be:

- **Actionable**: Capable of being implemented and enforced.
- **Testable**: Where applicable, include metrics, thresholds, or criteria (e.g., "response time must be < 2 seconds").
- **Categorized**: Tag each rule under a category such as **Performance**, **Scalability**, **Security**, **Usability**, **Maintainability**, **Availability**, **Compliance**, etc.

**Format the output** as a numbered list like:
1. [Category] - [Rule]
   - Justification (optional): [Explain why this rule is important or how it connects to the BRD]

BRD Content:
\"\"\"
{brd_text}
\"\"\"
"""


    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert compliance analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=700
    )
    return response.choices[0].message.content




