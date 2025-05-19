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
    rule_column = "Rules" if "Rules" in df.columns else df.columns[0]
    return df[rule_column].dropna().tolist()

def extract_and_match_vs_excel(gpt_response_text: str):
    static_rules = get_excel_rules()

    prompt = f"""
You are an AI assistant designed to evaluate the alignment of an LLM-generated response with a set of predefined rules listed in an Excel sheet. Your tasks are as follows:

Semantic Matching:
Compare the LLM-generated output with the rules present in the provided Excel file using semantic similarity—not keyword or string matching. You must understand and interpret the meaning of the rules.

Highlighting Unmatched Data:
Any content in the LLM output that does not semantically match any rule in the Excel must be highlighted in red to indicate non-compliance or deviation.

Rule Extraction:
Extract all policy or compliance rules that are either explicitly stated or implied in the LLM-generated response. These should be listed clearly and concisely.

Mismatch Identification:
From the extracted rules, identify and return a list of those that do not closely match any rule from the Excel sheet (again, based on semantic meaning).

Return the final output in the following format:

Original LLM Output (with unmatched sections highlighted in red)

Extracted Rules from LLM Output

List of Extracted Rules that Do Not Match Any Static Rule

Ensure that your evaluation focuses on the intent and meaning behind each rule rather than exact wording.

The displayed result should only consist of the unmatched values and not the llm output.

LLM Response:
\"\"\"{gpt_response_text}\"\"\"

Static Company Rules:
{chr(10).join([f"{i+1}. {Rules}" for i, Rules in enumerate(static_rules)])}

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
        #"unmatched_rules": reply
    }
