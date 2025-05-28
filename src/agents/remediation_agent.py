import os
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

latest_summary = {"content": ""}

def analyze_compliance_issues(raw_text: str) -> list:
    prompt = f"""
Act as a Compliance Expert whose main job is to generate clear and actionable remedies for each mismatched or violated compliance rule.

Instructions:

Provide a separate remedy for each mismatched rule.

Remedies must be in simple, non-technical language that anyone can understand.

Keep each remedy brief, clear, and to the point.

Do not repeat or rephrase the mismatched rule. Focus only on how to fix it.

Output should be a bullet point list like this:

Remedy 1

Remedy 2

Remedy 3

Remedy 4

Important:

Do not add any extra explanation or text before or after the list.

Do not group remedies together. Each rule gets its own remedy.each remedy should be detailed and shouldnt just repeat the rule in a different order.dont repeat the words give a detailed solution.each mismtched rule should have an appropriate remedy.
Text:
{raw_text}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compliance assistant that identifies issues and suggests remedies."},
            {"role": "user", "content": prompt},
        ]
    )

    remedies_text = response.choices[0].message.content.strip()
   
    return remedies_text

