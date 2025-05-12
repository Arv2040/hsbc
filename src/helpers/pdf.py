import PyPDF2
def extract_text_from_pdf(file_path):
    all_text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    return all_text

