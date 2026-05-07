import os
import requests
import re
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    input: str
    skill_type: str
    context: Optional[str] = None

def is_valid_url(text: str):
    # Regex per domini (es: magghyko.com, www.sito.it, https://...)
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
        print(f"🌐 TENTATIVO SCRAPING: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Errore: {str(e)}. Provo variante...")
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

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    print(f"📩 RICHIESTA RICEVUTA: Skill={request.skill_type}, Context={request.context or 'Generico'}")
    
    skill_map = {"copy": "skill.md", "structure": "skill-2.md", "aesthetic": "skill-3.md", "recap": "skill-4.md"}
    skill_file = skill_map.get(request.skill_type, "skill.md")
    
    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            skill_prompt = f.read()
        
        if request.context and request.context.strip():
            skill_prompt += f"\n\n--- ACTIVE CONTEXT LAYER ---\nTarget Context: {request.context}\n----------------------------"

        # LOGICA URL
        if is_valid_url(request.input):
            print(f"🔍 URL RILEVATO: {request.input}")
            scraped_data, error = scrape_site(request.input)
            if error:
                return {"status": "error", "message": f"Errore lettura sito. Copia-incolla il testo qui sotto.\n(Dettaglio: {error})"}
            content_to_analyze = f"ANALISI SITO: {request.input}\n\nCONTENUTO ESTRATTO:\n{scraped_data}"
        else:
            print("📝 TESTO SEMPLICE RILEVATO")
            content_to_analyze = f"CONTENUTO DA ANALIZZARE:\n\n{request.input}"

        if not GROQ_API_KEY:
            return {"status": "error", "message": "GROQ_API_KEY mancante nel .env"}

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": skill_prompt},
                {"role": "user", "content": content_to_analyze}
            ],
            "temperature": 0.6
        }
        
        print(f"⚡ ENGINE: GPT-OSS 120B (via Groq) in azione per Skill {request.skill_type}...")
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        res_json = res.json()
        
        if res.status_code != 200:
            return {"status": "error", "message": res_json.get("error", {}).get("message", "API Error")}
            
        analysis = res_json["choices"][0]["message"]["content"]
        return {"status": "success", "analysis": analysis}

    except Exception as e:
        print(f"❌ ERRORE CRITICO: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def read_index(): return FileResponse('index.html')
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
