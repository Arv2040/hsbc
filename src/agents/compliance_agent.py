import openai 
import os
from dotenv import load_dotenv
from agents.ingestion import parse_pdf
import json
from pathlib import Path

load_dotenv()
client = openai.AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def check_requirement_compliance(requirement_text):
       
    json_path = Path("compliance_rules/compliance_rules.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract the "rules" key
    compliance_rules_text = data.get("rules", [])
        
    prompt = f"""
    You are a compliance assistant.
    Given the following business requirement, check if it aligns with these policies:
    {compliance_rules_text}

    If not compliant, list what's missing and suggest clauses to add.

    Requirement:
    \"\"\"
    {requirement_text}
    \"\"\"

    Respond in this format:
    - Compliance Status: [Compliant/Non-Compliant] 
    - Matched Policies: [List]
    - Missing Elements: [List]
    - Suggested Clauses: [List]
    """

    response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

    return response.choices[0].message.content