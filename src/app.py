from fastapi import FastAPI, UploadFile, File
from preprocessing import preprocess_text
from typing import Dict

app = FastAPI()

@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)) -> Dict:
    text = await file.read()
    processed_output = preprocess_text(text.decode("utf-8"))
    return processed_output
