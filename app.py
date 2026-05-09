import os
import requests
import re
import base64
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

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
    images: Optional[List[str]] = None

def is_valid_url(text: str):
    pattern = re.compile(r'^(https?:\/\/)?(([a-z0-9-]+\.)+[a-z]{2,})(\/.*)?$', re.IGNORECASE)
    return re.match(pattern, text.strip()) and ' ' not in text.strip()

def scrape_site(url_input: str):
    url = url_input.strip().lower()
    if not url.startswith('http'): url = 'https://' + url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']): tag.decompose()
        return soup.get_text(separator=' ', strip=True)[:15000], None
    except Exception as e:
        return None, str(e)

@app.api_route("/", methods=["GET", "POST"])
async def universal_route(request: Request):
    if request.method == "GET":
        return FileResponse("index.html")
    
    try:
        body = await request.json()
        req = AnalysisRequest(**body)
        
        skill_map = {"copy": "skill.md", "structure": "skill-2.md", "aesthetic": "skill-3.md", "recap": "skill-4.md"}
        skill_file = skill_map.get(req.skill_type, "skill.md")
        
        with open(skill_file, "r", encoding="utf-8") as f:
            base_skill_prompt = f.read()
        
        is_it = any(word in req.input.lower() for word in [" il ", " la ", " di ", " per "])
        lang = "ITALIAN" if is_it else "ENGLISH"
        
        prompt = f"[LANGUAGE: {lang}]\n### RULES ###\n1. Response in {lang} ONLY.\n" + base_skill_prompt

        # --- GROQ VISION INTEGRATION ---
        visual_cues = []
        if req.images and len(req.images) > 0 and GROQ_API_KEY:
            for idx, img_b64 in enumerate(req.images):
                try:
                    # Preparazione payload Vision per Groq
                    vision_payload = {
                        "model": "llama-3.2-90b-vision-preview",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe this UI screenshot for a UX audit. Focus on colors, spacing, typography, and overall visual hierarchy. Be surgical."},
                                    {"type": "image_url", "image_url": {"url": img_b64}}
                                ]
                            }
                        ],
                        "temperature": 0.1
                    }
                    v_headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                    v_res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=vision_payload, headers=v_headers)
                    if v_res.status_code == 200:
                        cue = v_res.json()["choices"][0]["message"]["content"]
                        visual_cues.append(f"SCREENSHOT {idx+1} VISUAL ANALYSIS: {cue}")
                except Exception as ve:
                    print(f"Vision Error: {ve}")

        visual_context = "\n\n".join(visual_cues)
        content = ""
        if is_valid_url(req.input):
            data, err = scrape_site(req.input)
            content = f"SITE TEXT CONTENT:\n{data}" if not err else f"URL: {req.input}"
        else:
            content = f"USER TEXT:\n{req.input}"

        final_content = content
        if visual_context:
            final_content = f"### MANDATORY VISUAL CONTEXT ###\n{visual_context}\n\n### CONTENT TO AUDIT ###\n{content}"

        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": final_content}
            ],
            "temperature": 0.2
        }
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        
        if res.status_code != 200:
            return JSONResponse({"status": "error", "message": "Groq Error"}, status_code=500)
            
        return {"status": "success", "analysis": res.json()["choices"][0]["message"]["content"]}
        
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
