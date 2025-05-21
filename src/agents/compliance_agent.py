import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

# Load .env variables
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

EXCEL_RULES_PATH = "data/presaved_rules.xlsx"

def get_excel_rules():
    df = pd.read_excel(EXCEL_RULES_PATH)
    rule_column = "Rules" if "Rules" in df.columns else df.columns[0]
    return df[rule_column].dropna().tolist()

def check_requirement_compliance(gpt_response_text: str):
    static_rules = get_excel_rules()

    prompt = f"""
You are a Compliance Validation Agent. You are given a set of SME-defined requirements  and a list of company policy rules from an Excel file.

Your task is to:

1. **Extract** all individual policy or compliance rules from the LLM-generated response.
2. **Compare** each extracted rule semantically (not by exact words) with the company’s static policy rules.
3. For each extracted rule, determine:
   - Whether it semantically matches any static rule
   - If matched, identify the closest matching static rule
   - If no match is found, return null for the matched rule

Return the result strictly as a **JSON list** of objects. Each object should have the following keys:
- `"AI GENRATED POLICIES"`: The individual rule extracted from the LLM output
- `"status"`: Either `"Matched"` or `"Mismatched"`
- `"COMPANY POLICIES"`: The static rule it matches with (if any); otherwise `null`
dont hallucinate on the llm response of the rules. just do the tasks instructed and dont add anything extra

⚠ **Return ONLY the JSON list**—do not include markdown, commentary, or extra explanation.

LLM Response:
\"\"\"{gpt_response_text}\"\"\"

Static Company Rules:
{chr(10).join([f"{i+1}. {Rules}" for i, Rules in enumerate(static_rules)])}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compliance expert trained to extract and match policy rules."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    reply = response.choices[0].message.content.strip()

    try:
        structured_data = json.loads(reply)

        if isinstance(structured_data, list):
            return structured_data  # ✅ Just return the list directly
        else:
            raise ValueError("LLM returned an unexpected format.")

    except json.JSONDecodeError:
        return [{
            "AI GENRATED POLICIES": "Error: Could not parse LLM response",
            "status": "Mismatched",
            "COMPANY POLICIES": None
        }]
