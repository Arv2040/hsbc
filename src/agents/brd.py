from pathlib import Path
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from agents.ingestion import parse_pdf
from fpdf import FPDF
import textwrap

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_LOCAL"),
    api_version=os.getenv("OPENAI_API_VERSION_LOCAL"),
    azure_endpoint=os.getenv("OPENAI_API_BASE_LOCAL")
)

def generate_brd_from_text(raw_text: str) -> dict:
    """Generate BRD + Compliance Rules, return both text and downloadable PDF path."""

    template_path = Path("agents/brd.pdf")
    if not template_path.exists():
        raise FileNotFoundError(f"BRD template not found at: {template_path.resolve()}")

    template_text = parse_pdf(str(template_path))

    # Step 1: Generate the BRD content
    prompt = f"""
You are a Business Analyst AI assistant. Generate a well-formatted, complete Business Requirements Document (BRD) based on the provided use case input and the BRD template structure below.

--- BRD TEMPLATE STRUCTURE ---
{template_text}
--- END TEMPLATE ---

--- USE CASE INPUT ---
{raw_text}
--- END INPUT ---

**Instructions:**
- Strictly follow the section structure and order from the template.
- Format each section using Markdown-style headers (e.g., `## Section Title`).
- Use bullet points, numbered lists, and bolded field labels where appropriate.
- For any missing information, insert “To be defined”.
- Do NOT invent data not suggested by the input.
- Return only the final BRD content. No explanation or extra comments.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a business analyst expert at creating BRDs using templates."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2
    )

    brd_content = response.choices[0].message.content.strip()

    # Step 2: Generate Compliance Rules
    rules_prompt = f"""
Based on the following Business Requirements Document (BRD), generate a structured list of compliance rules.

--- BRD CONTENT START ---
{brd_content}
--- BRD CONTENT END ---

**Instructions:**
- For each rule, include:
  - **Rule ID** (e.g., R1, R2, R3…)
  - **Rule Description**
  - **Category** (choose one: Data, Security, Operational, Legal)
  - **Severity** (High, Medium, Low)
  - **Applicable Standards** (e.g., GDPR, ISO 27001)

- Format output as a Markdown table:
| Rule ID | Description | Category | Severity | Applicable Standards |
|---------|-------------|----------|----------|-----------------------|
| R1      | ...         | Data     | High     | GDPR                 |
"""

    rules_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compliance officer generating rules based on BRD content."},
            {"role": "user", "content": rules_prompt},
        ],
        temperature=0.3
    )

    rules_content = rules_response.choices[0].message.content.strip()

    # Combine BRD content and compliance rules
    combined_text = f"{brd_content}\n\n## Compliance Rules\n\n{rules_content}"

    # Step 3: Create PDF
    pdf_path = Path("generated_pdf/generated_brd.pdf")
    create_pdf_from_text(combined_text, pdf_path)

    # Return both the text and path to the PDF
    return {
        "brd_text": combined_text,
        "pdf_path": str(pdf_path)
    }

def create_pdf_from_text(text: str, pdf_path: Path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        if line.startswith("## "):
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, line[3:], ln=True)
            pdf.set_font("Arial", size=12)
        elif line.strip() == "":
            pdf.ln(4)
        else:
            wrapped = textwrap.wrap(line, 100)
            for subline in wrapped:
                pdf.cell(0, 10, subline, ln=True)

    pdf.output(str(pdf_path))
