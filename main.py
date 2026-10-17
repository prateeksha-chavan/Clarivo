import json
import os
import re

import fitz  # PyMuPDF, used to turn PDF pages into images
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("MODEL_NAME")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI(title="Clarivo")

MAX_BYTES = 10 * 1024 * 1024

PROMPT = """You are Clarivo, an assistant that turns confusing documents into clear action.
Read the attached document (a syllabus, form, notice, scholarship letter, etc.).
Return ONLY valid JSON, with no markdown and no extra text, in exactly this shape:
{
  "title": "short name of the document",
  "summary": "2 sentence plain-language summary",
  "actions": [{"task": "what to do", "priority": "high|medium|low"}],
  "deadlines": [{"date": "date as written", "what": "what is due"}],
  "required_documents": ["document to prepare"],
  "warnings": ["risk, penalty or easy-to-miss detail"]
}
Rules: use only information visible in the document. If something is missing, use an
empty list. Never invent dates. Keep each item under 20 words."""


def parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found in model output")
    return json.loads(text[start : end + 1])


def pdf_to_images(data: bytes, max_pages: int = 3) -> list[bytes]:
    doc = fitz.open(stream=data, filetype="pdf")
    last = min(max_pages, len(doc))
    return [
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).tobytes("png")
        for page in doc.pages(0, last)
    ]


@app.get("/")
def home():
    return FileResponse("index.html")


@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    data = file.file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 10 MB)")

    mime = file.content_type or ""
    if mime == "application/pdf":
        parts = [
            types.Part.from_bytes(data=img, mime_type="image/png")
            for img in pdf_to_images(data)
        ]
    elif mime.startswith("image/"):
        parts = [types.Part.from_bytes(data=data, mime_type=mime)]
    else:
        raise HTTPException(415, "Upload an image (jpg/png) or a PDF")

    raw = ""
    for _ in range(2):  # one retry if the model returns broken JSON
        try:
            resp = client.models.generate_content(model=MODEL, contents=parts + [PROMPT])
            raw = resp.text or ""
            return parse_json(raw)
        except (ValueError, json.JSONDecodeError):
            continue
        except Exception as e:
            raise HTTPException(502, f"Model call failed: {e}")
    return {"error": "Could not read a structured result. Try a clearer image.", "raw": raw}
