# --------------------------------- Requires Azure Speech Dependencies ------------------------------------------------

# import os
# import email
# import imaplib
# import pytesseract
# import fitz  # PyMuPDF
# import tempfile
# from pydub import AudioSegment
# from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
# from dotenv import load_dotenv

# load_dotenv(dotenv_path=".env")

# # Azure OpenAI API (loaded for future extension if needed)
# OPENAI_API_TYPE_LOCAL = os.getenv("OPENAI_API_TYPE_LOCAL")
# OPENAI_API_BASE_LOCAL = os.getenv("OPENAI_API_BASE_LOCAL")
# OPENAI_API_VERSION_LOCAL = os.getenv("OPENAI_API_VERSION_LOCAL")
# OPENAI_API_KEY_LOCAL = os.getenv("OPENAI_API_KEY_LOCAL")

# # Azure Speech config
# speech_config = SpeechConfig(
#     subscription=os.getenv("AZURE_SPEECH_KEY"),
#     region=os.getenv("AZURE_SPEECH_REGION")
# )


# def fetch_emails():
#     imap_host = os.getenv("IMAP_HOST")
#     imap_user = os.getenv("IMAP_USER")
#     imap_pass = os.getenv("IMAP_PASS")

#     mail = imaplib.IMAP4_SSL(imap_host)
#     mail.login(imap_user, imap_pass)
#     mail.select('inbox')

#     result, data = mail.search(None, 'ALL')
#     emails = []
#     for num in data[0].split():
#         result, data = mail.fetch(num, '(RFC822)')
#         msg = email.message_from_bytes(data[0][1])
#         emails.append({
#             "subject": msg.get("subject"),
#             "from": msg.get("from"),
#             "date": msg.get("date"),
#             "body": msg.get_payload()
#         })
#     mail.close()
#     mail.logout()
#     return emails


# def transcribe_audio(file_path):
#     audio_config = AudioConfig(filename=file_path)
#     recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
#     result = recognizer.recognize_once()
#     return result.text if result.reason.name == "RecognizedSpeech" else None


# def parse_pdf(file_path):
#     doc = fitz.open(file_path)
#     full_text = ""
#     for page in doc:
#         full_text += page.get_text()
#     return full_text


# def ocr_image(file_path):
#     return pytesseract.image_to_string(file_path)


# def extract_metadata(source, topic=None):
#     return {
#         "source": source,
#         "topic": topic or "Unknown",
#         "timestamp": str(tempfile.mktemp())
#     }
