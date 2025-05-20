from pathlib import Path
import os
import json
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

def generate_brd(input_data: str | Path, template_file: Path = None, compliance_data: dict = None) -> dict:
    """
    Accepts either a raw string (prompt) or a PDF file path.
    Optionally accepts a custom BRD template and compliance data.
    """
    if isinstance(input_data, Path) or (isinstance(input_data, str) and os.path.isfile(input_data)):
        input_path = Path(input_data)
        if input_path.suffix.lower() != ".pdf":
            raise ValueError("Unsupported file type. Only .pdf is allowed.")
        raw_text = parse_pdf(str(input_path))
    elif isinstance(input_data, str):
        raw_text = input_data
    else:
        raise TypeError("Invalid input. Provide a PDF file path or a text prompt.")

    return generate_brd_from_text(raw_text, template_file=template_file, compliance_data=compliance_data)


def generate_brd_from_text(raw_text: str, template_file: Path = None, compliance_data: dict = None) -> dict:
    """
    Generates BRD content and compliance rules using either a provided template or a default one.
    Injects given compliance_data and enforces only those rules to be used (no hallucination).
    """
    # Use uploaded template if provided, else fallback to default
    if template_file and template_file.exists():
        template_text = parse_pdf(str(template_file))
    else:
        default_template = Path("agents/brd.pdf")
        if not default_template.exists():
            raise FileNotFoundError(f"BRD template not found at: {default_template.resolve()}")
        template_text = parse_pdf(str(default_template))

    # Build compliance context if provided
    compliance_instructions = ""
    if compliance_data:
        compliance_instructions = "\n--- COMPLIANCE CONTEXT ---\n"
        for key, value in compliance_data.items():
            compliance_instructions += f"- **{key}**: {value}\n"
        compliance_instructions += "--- END COMPLIANCE CONTEXT ---\n"

    # Construct prompt for BRD generation
    prompt = f"""
Act as a Professional Business Analyst Expert who is specialized in creating consistent BRDs for similar use-cases.
Generate a complete Business Requirements Document (BRD) using the input and the BRD template structure.

--- BRD TEMPLATE STRUCTURE ---
{template_text}
--- END TEMPLATE ---

{compliance_instructions}

--- USE CASE INPUT ---
{raw_text}
--- END INPUT ---

*Instructions:*
- Strictly follow the template structure.
- Format each section using Markdown-style headers (e.g., ## Section Title).
- Use bullet points, numbered lists, and bolded field labels.
- For any missing information, insert “To be defined”.
- **Use only the compliance rules provided in the compliance context. Do not hallucinate or invent any additional rules.**
- Do NOT add anything outside the provided input.
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

    # Generate compliance rules table (from given compliance_data only)
    if compliance_data:
        # Format rules manually based on provided data
        rules_markdown = "| Rule ID | Description | Category | Severity | Applicable Standards |\n"
        rules_markdown += "|---------|-------------|----------|----------|----------------------|\n"
        for idx, (key, rule) in enumerate(compliance_data.items(), start=1):
            rule_id = f"R{idx}"
            rules_markdown += f"| {rule_id} | {rule.get('description', '')} | {rule.get('category', '')} | {rule.get('severity', '')} | {rule.get('standards', '')} |\n"
        rules_content = rules_markdown
    else:
        # Fallback: LLM generates compliance rules from BRD content
        rules_prompt = f"""
Based on the following BRD, generate a structured list of compliance rules.

--- BRD CONTENT START ---
{brd_content}
--- BRD CONTENT END ---

**Instructions:**
- For each rule, include:
  - **Rule ID** (e.g., R1, R2, R3…)
  - **Rule Description**
  - **Category** (Data, Security, Operational, Legal)
  - **Severity** (High, Medium, Low)
  - **Applicable Standards** (e.g., GDPR, ISO 27001)

Format as a Markdown table:
| Rule ID | Description | Category | Severity | Applicable Standards |
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

    # Combine BRD + Rules
    combined_text = f"{brd_content}\n\n## Compliance Rules\n\n{rules_content}"

    # Save as PDF
    pdf_path = Path("generated_pdf/generated_brd.pdf")
    create_pdf_from_text(combined_text, pdf_path)

    return {
        "brd_text": combined_text,
        "pdf_path": str(pdf_path)
}
def sanitize_text(text: str) -> str:
    """
    Replaces common Unicode characters with ASCII equivalents.
    Removes other characters that cannot be encoded in Latin-1.
    """
    replacements = {
        '\u2013': '-',   # en dash
        '\u2014': '-',   # em dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2022': '-',   # bullet
        '\u00a0': ' ',   # non-breaking space
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text.encode('latin-1', errors='ignore').decode('latin-1')

def create_pdf_from_text(text: str, pdf_path: Path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Times", size=12)

    for line in text.split("\n"):
        clean_line = sanitize_text(line)
        if clean_line.startswith("## "):
            pdf.set_font("Times", style='B', size=14)
            pdf.cell(0, 10, clean_line[3:], ln=True)
            pdf.set_font("Times", size=12)
        elif clean_line.strip() == "":
            pdf.ln(4)
        else:
            wrapped = textwrap.wrap(clean_line, 100)
            for subline in wrapped:
                pdf.cell(0, 10, subline, ln=True)

    pdf.output(str(pdf_path))

