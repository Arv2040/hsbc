import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

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
    rule_column = "rule" if "rule" in df.columns else df.columns[0]
    return df[rule_column].dropna().tolist()

def extract_and_match_vs_excel(gpt_response_text: str):
    static_rules = get_excel_rules()

    prompt = f"""
You are a compliance expert.

From the following input (LLM-generated compliance response), perform the following:
1. Extract all policy/compliance rules that are implied or listed in the response.
2. Compare each of them with the static company rules below.
3. Return a list of **extracted rules** that do not closely match any static rule (less than 70% semantic similarity).

LLM Response:
\"\"\"{gpt_response_text}\"\"\"

Static Company Rules:
{chr(10).join([f"{i+1}. {rule}" for i, rule in enumerate(static_rules)])}

Instructions:
- Only return unmatched rules.
- Format:
[
  {{
    "extracted_rule": "...",
    "expected_match": "No close match found"
  }},
  ...
]
Show the output in a proper tabular format.
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

    return {
        "status": "✅ Completed extraction and comparison",
        "unmatched_rules": reply
    }
