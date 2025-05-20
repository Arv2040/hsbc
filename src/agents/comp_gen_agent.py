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
You are a compliance analyst. Based on the following BRD content, extract relevant compliance rules or requirements that the business must adhere to. Format each rule as a numbered list.

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




