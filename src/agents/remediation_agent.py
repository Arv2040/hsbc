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
You are a senior compliance expert responsible for identifying and resolving mismatched or violated compliance rules in business requirement documents (BRDs).

Your task is to provide a clear, practical, and effective **remedy** for **each** mismatched compliance rule listed below.

Instructions:

- Each compliance mismatch **must have a unique remedy**. **Do not skip any**. Do not write "No specific recommendation provided".
- Each remedy must be **detailed**, **realistic**, and **immediately implementable**.
- Use **simple, non-technical language** that any business stakeholder can understand.
- Focus only on **how to fix** the compliance issue — **do not repeat or rephrase** the rule itself.
- Each remedy should be written as a **separate bullet point**.
- **Do not include any numbering (e.g., Remedy 1, Remedy 2)** — just bullet points.
- Do not include any introductory or concluding text in the output.

Text:
\"\"\"
{raw_text}
\"\"\"
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

