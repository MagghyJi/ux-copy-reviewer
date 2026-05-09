import os
import requests
import re
import base64
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

# Configurazione CORS (Fondamentale per Hugging Face)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    input: str
    skill_type: str
    context: Optional[str] = None
    images: Optional[List[str]] = None # Base64 data strings

def is_valid_url(text: str):
    pattern = re.compile(
        r'^(https?:\/\/)?' 
        r'(([a-z0-9-]+\.)+[a-z]{2,})' 
        r'(\/.*)?$', re.IGNORECASE
    )
    return re.match(pattern, text.strip()) and ' ' not in text.strip()

def scrape_site(url_input: str):
    url = url_input.strip().lower()
    if not url.startswith('http'):
        url = 'https://' + url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        if 'www.' not in url:
            url = url.replace('https://', 'https://www.')
        else:
            url = url.replace('www.', '')
        
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
        except Exception as e2:
            return None, str(e2)

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:15000], None
    except Exception as e:
        return None, str(e)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Server is up"}

@app.get("/analyze")
async def analyze_get():
    return {"status": "error", "message": "Please use POST method"}

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    print(f"--- ANALYZE REQUEST RECEIVED: {request.skill_type} ---")
    skill_map = {"copy": "skill.md", "structure": "skill-2.md", "aesthetic": "skill-3.md", "recap": "skill-4.md"}
    skill_file = skill_map.get(request.skill_type, "skill.md")
    
    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            base_skill_prompt = f.read()
        
        # Determine language for enforcement
        italian_markers = [" il ", " la ", " di ", " per ", " un ", " che ", " è ", " sono ", " del ", " della "]
        is_it = any(word in request.input.lower() for word in italian_markers)
        lang_name = "ITALIAN" if is_it else "ENGLISH"

        # PREPEND CRITICAL RULES
        critical_rules = (
            "### CRITICAL OPERATING RULES ###\n"
            f"1. RESPONSE LANGUAGE: You MUST respond EXCLUSIVELY in {lang_name}. "
            "Never mix languages. If the content is in English, reply in English. "
            "If the content is in Italian, reply in Italian.\n"
        )
        if request.images and len(request.images) > 0:
            critical_rules += f"2. VISION ENABLED: Visual descriptions of {len(request.images)} screenshot(s) ARE PROVIDED. Use them for absolute precision.\n"
        
        skill_prompt = f"[LANGUAGE: {lang_name}]\n\n" + critical_rules + "\n" + base_skill_prompt

        if request.context and request.context.strip():
            skill_prompt += f"\n\n--- ACTIVE CONTEXT LAYER ---\nTarget Context: {request.context}\n----------------------------"

        content_to_analyze = ""
        if request.input:
            if is_valid_url(request.input):
                scraped_data, error = scrape_site(request.input)
                if not error:
                    content_to_analyze = f"SOURCE MATERIAL (WEBSITE SCRAPE):\nURL: {request.input}\n\nCONTENT:\n{scraped_data}"
                else:
                    content_to_analyze = f"SOURCE MATERIAL: URL {request.input} (Scraping failed, use visual cues)."
            else:
                content_to_analyze = f"SOURCE MATERIAL (TEXT):\n\n{request.input}"

        if not GROQ_API_KEY:
            return {"status": "error", "message": "GROQ_API_KEY missing"}

        # Vision Cues placeholder for Cloud
        visual_cues_text = ""
        if request.images and len(request.images) > 0:
            visual_cues_text = "Visual cues analysis is currently being processed via text reasoning as vision models are local."

        # FINAL ANALYSIS
        combined_content = content_to_analyze
        if visual_cues_text:
            combined_content = (
                "### MANDATORY VISUAL CONTEXT ###\n"
                "The following is a DIRECT SENSORY DESCRIPTION of the website screenshots. "
                "You MUST treat this as if you are seeing the images yourself. "
                "Do NOT say you lack visual access. Use these details for your scores.\n\n"
                f"{visual_cues_text}\n\n"
                "### SOURCE CONTENT ###\n"
                f"{content_to_analyze}"
            )
            
        headers_groq = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload_groq = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": skill_prompt},
                {"role": "user", "content": combined_content or "Perform analysis based on provided context."}
            ],
            "temperature": 0.2
        }
        
        res_g = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload_groq, headers=headers_groq)
        res_json = res_g.json()
        
        if res_g.status_code != 200:
            return {"status": "error", "message": res_json.get("error", {}).get("message", "Groq API Error")}
            
        analysis = res_json["choices"][0]["message"]["content"]
        return {"status": "success", "analysis": analysis}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def read_index():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
