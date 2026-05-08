# Usa un'immagine Python leggera
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file delle dipendenze e installali
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice
COPY . .

# Esponi la porta 7860 (quella standard di Hugging Face)
EXPOSE 7860

# Comando per avviare l'app sulla porta corretta per HF
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
