import os
import requests
import re
import base64
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    image: Optional[str] = None # Base64 data string

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

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    skill_map = {"copy": "skill.md", "structure": "skill-2.md", "aesthetic": "skill-3.md", "recap": "skill-4.md"}
    skill_file = skill_map.get(request.skill_type, "skill.md")
    
    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            base_skill_prompt = f.read()
        
        # PREPEND CRITICAL RULES TO SYSTEM PROMPT
        critical_rules = (
            "### CRITICAL OPERATING RULES ###\n"
            "1. RESPONSE LANGUAGE: You MUST respond in the SAME LANGUAGE as the source material provided. "
            "If the website or text is in ENGLISH, you MUST output your entire analysis in ENGLISH. "
            "If it is in ITALIAN, you MUST output in ITALIAN.\n"
        )
        if request.image:
            critical_rules += "2. VISION ENABLED: A screenshot IS PROVIDED. You MUST use it to perform the analysis. Do NOT say visual access is limited. You have full visibility.\n"
        
        skill_prompt = critical_rules + "\n" + base_skill_prompt

        if request.context and request.context.strip():
            skill_prompt += f"\n\n--- ACTIVE CONTEXT LAYER ---\nTarget Context: {request.context}\n----------------------------"

        content_to_analyze = ""
        if request.input:
            if is_valid_url(request.input):
                scraped_data, error = scrape_site(request.input)
                if not error:
                    content_to_analyze = f"SOURCE MATERIAL (WEBSITE SCRAPE):\nURL: {request.input}\n\nCONTENT:\n{scraped_data}"
                else:
                    content_to_analyze = f"SOURCE MATERIAL: URL {request.input} (Scraping failed, use screenshot if available)."
            else:
                content_to_analyze = f"SOURCE MATERIAL (TEXT):\n\n{request.input}"

        # Determine language for enforcement (simple detection)
        # If input has common Italian words, assume Italian, else English
        is_it = any(word in request.input.lower() for word in [" il ", " la ", " di ", " per ", " un ", " che ", " è ", " sono "])
        lang_name = "ITALIAN" if is_it else "ENGLISH"
        
        # Simple language marker at the start of the skill prompt
        skill_prompt = f"[LANGUAGE: {lang_name}]\n\n" + skill_prompt

        if not GROQ_API_KEY:
            return {"status": "error", "message": "GROQ_API_KEY missing"}

        if request.image and request.skill_type == "aesthetic":
            # CHAINED VISION: Use Moondream to describe, then Groq to analyze
            url_ollama = "http://localhost:11434/api/generate"
            
            img_data = request.image.split(",")[1] if "," in request.image else request.image
            
            # 1. Get a raw visual description from Moondream
            visual_description_prompt = (
                "ACT AS A VISUAL SENSOR. Describe this website screenshot for a Senior UX Strategist. "
                "List specific details about: "
                "1. Dominant colors and accent colors. "
                "2. Typography style (professional, creative, etc.). "
                "3. Visual hierarchy (what stands out first?). "
                "4. Image style (real people, stock, illustrations). "
                "5. Overall aesthetic quality (High, Medium, Low) and vibe."
            )
            
            payload_ollama = {
                "model": "moondream",
                "prompt": visual_description_prompt,
                "images": [img_data],
                "stream": False
            }
            
            try:
                # Get visual cues
                res_v = requests.post(url_ollama, json=payload_ollama, timeout=120)
                visual_cues = res_v.json().get("response", "Visual access limited.")
                
                # 2. Feed visual cues + text to Groq for the full analysis
                combined_content = (
                    f"VISUAL CUES FROM SCREENSHOT:\n{visual_cues}\n\n"
                    f"SOURCE MATERIAL (TEXT):\n{content_to_analyze}"
                )
                
                headers_groq = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                payload_groq = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": skill_prompt},
                        {"role": "user", "content": combined_content}
                    ],
                    "temperature": 0
                }
                
                res_g = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload_groq, headers=headers_groq)
                analysis = res_g.json()["choices"][0]["message"]["content"]
                return {"status": "success", "analysis": analysis}
                
            except Exception as e:
                return {"status": "error", "message": f"Vision Chain Error: {str(e)}"}

        else:
            # Use GROQ API for text-only tasks
            model = "llama-3.3-70b-versatile"
            messages = [{"role": "system", "content": skill_prompt}, {"role": "user", "content": content_to_analyze or "Perform analysis based on available context."}]

            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0
            }
            
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            res_json = res.json()
            
            if res.status_code != 200:
                return {"status": "error", "message": res_json.get("error", {}).get("message", "Groq API Error")}
                
            analysis = res_json["choices"][0]["message"]["content"]
            return {"status": "success", "analysis": analysis}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def read_index(): return FileResponse('index.html')
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
