import openai 
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def check_requirement_compliance(requirement_text):
    prompt = f"""
You are a compliance assistant.
Given the following business requirement, check if it aligns with GDPR and MiFID policies.
If not, list what is missing and suggest clauses to add.
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

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response['choices'][0]['message']['content']



