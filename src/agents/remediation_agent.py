import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from agents.compliance_agent import check_requirement_compliance

# Load environment variables
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_remediation(gpt_response_text: str):
    compliance_results = check_requirement_compliance(gpt_response_text)
    
    mismatched_rules = [rule for rule in compliance_results if rule["status"] == "Mismatched"]

    if not mismatched_rules:
        return "✅ All LLM policies are compliant with company rules. No remediation needed."

    remediation_prompt = f"""
You are a Remediation Expert Agent. You will receive a list of non-compliant LLM-generated rules (mismatched against company policy).

Your job is to provide clear and practical **remediation steps** for each mismatched policy. 
Return the response as a JSON list of objects with these keys:
- `"MISMATCHED RULE"`: The non-compliant policy text
- `"REMEDIATION"`: A bullet-point list (array of strings) with actionable remediation steps

Only provide entries for mismatched policies.

Mismatched Rules:
{json.dumps([r["LLM POLICIES"] for r in mismatched_rules], indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a remediation advisor for compliance issues."},
            {"role": "user", "content": remediation_prompt}
        ],
        temperature=0.3
    )

    reply = response.choices[0].message.content.strip()

    try:
        structured_remediations = json.loads(reply)

        result_str = "🔧 **Remediation Plan for Mismatched Rules:**\n\n"
        for item in structured_remediations:
            result_str += f"- **MISMATCHED RULE:** {item['MISMATCHED RULE']}\n"
            for bullet in item.get("REMEDIATION", []):
                result_str += f"  - {bullet}\n"
            result_str += "\n"

        return result_str.strip()

    except json.JSONDecodeError:
        return "❌ Failed to parse remediation response. Please check LLM formatting."

# Example usage:
if __name__ == "__main__":
    llm_response_text = """
    1. All employees must change their passwords every 180 days.
    2. Personal devices are allowed for internal communication.
    3. Customer data can be stored indefinitely.
    """

    print(generate_remediation(llm_response_text))
