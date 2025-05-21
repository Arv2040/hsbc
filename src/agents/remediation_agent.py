import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from agents.compliance_agent import check_requirement_compliance  # Import the function

# Load environment variables
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_remediation(gpt_response_text: str):
    # Step 1: Get compliance results
    compliance_results = check_requirement_compliance(gpt_response_text)

    # Step 2: Filter only mismatched rules
    mismatched_rules = [
        rule["llm_rule"]
        for rule in compliance_results
        if rule.get("status") == "Mismatched"
    ]

    if not mismatched_rules:
        return {"message": "All rules matched. No remediation needed."}

    # Step 3: Construct LLM prompt for remediation
    remediation_prompt = f"""
You are a Remediation Agent. The following rules were flagged as **non-compliant** by the compliance checker.

For each of the following rules, generate a clear remediation suggestion that would bring it in line with standard compliance expectations.

⚠ Output strictly as a **JSON list** of objects, each with:
- `"original_rule"`: The rule that was mismatched.
- `"remediation_advice"`: A concise and actionable remediation.

Mismatched Rules:
{json.dumps(mismatched_rules, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compliance remediation advisor."},
            {"role": "user", "content": remediation_prompt}
        ],
        temperature=0.3
    )

    try:
        result = response.choices[0].message.content.strip()
        return json.loads(result)

    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM output."}
