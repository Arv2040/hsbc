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
Act as Compliance Expert whose primary job is to generate remedies based on the identified mismatched or violated compliances. Generate the remedies in brief and to the point.
Return the remedies in a list in bullet points.

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

