import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Errore: GROQ_API_KEY non trovata.")
else:
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json()["data"]
        for m in models:
            print(f"- {m['id']}")
    else:
        print(f"Errore API: {response.status_code} - {response.text}")
