# -------------- Stage: immagine base ------------------------------------------------------------ #
# Usiamo una immagine Python ufficiale, leggera (slim = senza pacchetti inutili)
FROM python:3.11-slim

# -------------- Installazione di wkhtmltopdf ---------------------------------------------------- #
# Su Linux lo installiamo come pacchetto di sistema — niente .exe, niente path manuali
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    # Dipendenze grafiche necessarie a wkhtmltopdf per renderizzare HTML
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -------------- Setup dell'app ------------------------------------------------------------------ #
# Cartella di lavoro dentro il container
WORKDIR /app

# Copia prima i requirements e installali (ottimizza la cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice
COPY main.py .

# -------------- Avvio --------------------------------------------------------------------------- #
# Espone la porta 8000 (quella su cui ascolta FastAPI)
EXPOSE 8000

# Comando di avvio dell'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
