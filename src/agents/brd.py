from pathlib import Path
import os
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv()
from typing import Dict, List
from agents.ingestion import parse_pdf
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_brd_from_text(raw_text: str) -> str:
    """Generate BRD document using the template from dev-data folder"""
   
    template_path = Path("agents/brd.pdf")
    if not template_path.exists():
        raise FileNotFoundError(f"BRD template not found at: {template_path.resolve()}")
   
    template_text = parse_pdf(str(template_path)) 
    
   
    prompt = f"""
    Create a comprehensive Business Requirements Document (BRD) based on the following content.
    Use this template structure from our existing BRD (shown below):
    
    --- TEMPLATE STRUCTURE ---
    {template_text}
    --- END TEMPLATE ---
    
    Content to analyze and incorporate:
    {raw_text}
    
    Important:
    - Maintain all sections from the template
    - Keep the same formatting style
    - Fill each section with relevant content from the provided text
    - Don't include placeholder text
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a business analyst expert at creating BRDs using existing templates."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2  
    )
    
    brd_content = response.choices[0].message.content.strip()
    """Generate compliance rules from extracted text"""
    prompt = f"""
    Based on the following business requirements, generate specific compliance rules:
    {brd_content}
    
    For each rule, provide:
    - Rule ID (auto-increment)
    - Description
    - Category (Data, Security, Operational, Legal)
    - Severity (High, Medium, Low)
    - Applicable Standards/Regulations
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compliance officer generating detailed rules."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3
    )
    
   
    rules_content = response.choices[0].message.content.strip()
    return rules_content


   
    
   

