import os 
import email
import imaplib
import pytesseract
import tempfile
from dotenv import load_dotenv
import httpx
import speech_recognition as sr
from pydub import AudioSegment
import uuid
import PyPDF2  # ✅ Use PyPDF2 instead of fitz


load_dotenv(dotenv_path=".env")

# Azure OpenAI API (loaded for future extension if needed)
OPENAI_API_TYPE_LOCAL = os.getenv("OPENAI_API_TYPE_LOCAL")
OPENAI_API_BASE_LOCAL = os.getenv("OPENAI_API_BASE_LOCAL")
OPENAI_API_VERSION_LOCAL = os.getenv("OPENAI_API_VERSION_LOCAL")
OPENAI_API_KEY_LOCAL = os.getenv("OPENAI_API_KEY_LOCAL")


def fetch_emails():
    imap_host = os.getenv("IMAP_HOST")
    imap_user = os.getenv("IMAP_USER")
    imap_pass = os.getenv("IMAP_PASS")

    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(imap_user, imap_pass)
    mail.select('inbox')

    result, data = mail.search(None, 'ALL')
    emails = []
    for num in data[0].split():
        result, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        emails.append({
            "subject": msg.get("subject"),
            "from": msg.get("from"),
            "date": msg.get("date"),
            "body": msg.get_payload()
        })
    mail.close()
    mail.logout()
    return emails


# ✅ Updated parse_pdf function using PyPDF2
def parse_pdf(file_path):
    full_text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            full_text += page.extract_text() or ""
    return full_text


def ocr_image(file_path):
    return pytesseract.image_to_string(file_path)


def extract_metadata(source, topic=None):
    return {
        "source": source,
        "topic": topic or "Unknown",
        "timestamp": str(tempfile.mktemp())
    }
