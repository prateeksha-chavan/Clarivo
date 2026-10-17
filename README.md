# Clarivo
**From confusion to clear action.**

Clarivo turns confusing documents (notices, scholarship announcements, forms, PDFs) into a clear action plan: what to do, when it is due, which documents to prepare, and what to watch out for.

**Live demo:** _Add the Render URL after deployment._

## Hackathon entry
Hacktoberfest Hack Day Bengaluru 2026
- Track: **Best Use of Gemma 4**
- Problem statement: **G3 - Multimodal AI Intelligence**

## How Gemma 4 is used
Gemma 4 (`gemma-4-26b-a4b-it`, through the Gemini API) is the core of the app. It reads the uploaded document, including pages that are images or scans, together with a text instruction, and returns structured JSON with a summary, actions, deadlines, required documents and warnings. No other model is in the loop.

## How it works
1. Upload a PDF or an image.
2. The FastAPI backend prepares the file (PDF pages are read with PyMuPDF).
3. Gemma 4 analyses the content and returns structured JSON.
4. The page shows the result in clear sections.

## Tech stack
Python, FastAPI, Gemma 4 via the Gemini API (`google-genai`), PyMuPDF, plain HTML/CSS/JavaScript.

## Run it locally
Requires Python 3.11+ and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```powershell
git clone https://github.com/prateeksha-chavan/Clarivo.git
cd Clarivo
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```
(macOS/Linux: use `source venv/bin/activate` instead.)

Create a `.env` file:
```env
GEMINI_API_KEY=your_key_here
MODEL_NAME=gemma-4-26b-a4b-it
```

Start the app and open http://127.0.0.1:8000:
```powershell
uvicorn main:app --reload
```
A sample notice is included: `Clarivo_Test_Notice.pdf`.

## Privacy
Uploaded files are sent to Google's Gemini API so Gemma 4 can read them. Do not upload documents you are not allowed to share with a cloud API.

## Development notes
The repository was created on 6 October 2026. A first draft of the app was generated with AI coding assistants on 10-11 October 2026, before the 13-18 October development window opened. During the window (13-17 October) it was tested, fixed, documented and deployed. AI coding assistants were used throughout.
## License
MIT
