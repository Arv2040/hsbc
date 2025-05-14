import re
import spacy
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv(dotenv_path=".env")

nlp = spacy.load("en_core_web_sm")

def remove_noise(text: str) -> str:
    # Remove signatures and greetings heuristically
    text = re.sub(r"(Regards|Thanks|Sincerely|Best|Cheers)[\s\S]+", "", text, flags=re.I)
    text = re.sub(r"(Hi|Hello|Dear)[^,\n]*[,:\n]", "", text, flags=re.I)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def split_sentences(text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def detect_named_entities(text: str) -> List[Dict]:
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

def preprocess_text(raw_text: str) -> Dict:
    cleaned = remove_noise(raw_text)
    segments = split_sentences(cleaned)
    entities = detect_named_entities(cleaned)
    return {
        "clean_text": cleaned,
        "segments": segments,
        "entities": entities
    }
