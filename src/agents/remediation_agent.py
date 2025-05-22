import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import pandas as pd
from datetime import datetime

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def analyze_compliance_issues(raw_text: str, output_path: str = "compliance_remedies.xlsx") -> str:
    prompt = f"""
Act as a Compliance Expert. Based on the following text, identify each mismatched or violated policy clearly and provide a corresponding remediation.

Format your response like this:

- [AI GENRATED POLICIES] → [REMEDY]

Keep it clear and to the point.

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

    # Split response into lines, extract rule → remedy pairs
    rows = []
    for line in remedies_text.splitlines():
        if "→" in line:
            rule, remedy = line.split("→", 1)
        elif ":" in line:
            rule, remedy = line.split(":", 1)
        else:
            continue
        rows.append({
            "AI GENERATED POLICIES": rule.strip("-• ").strip(),
            "REMEDIATIONS": remedy.strip()
        })

    # Save to Excel
    df = pd.DataFrame(rows)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = output_path.replace(".xlsx", f"_{timestamp}.xlsx")
    df.to_excel(excel_path, index=False)

    return excel_path  # Return path to the generated Excel file
