from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pdfkit
import io
import logging

# -------------- Setup ---------------------------------------------------------------------------- #

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HTML to PDF Converter",
    description="API per convertire HTML in PDF, da usare con N8N",
    version="1.0.0"
)

# Configurazione pdfkit — su Linux wkhtmltopdf è installato nel sistema, nessun path manuale
config = pdfkit.configuration()


# -------------- Schema della richiesta ----------------------------------------------------------- #

class ConvertRequest(BaseModel):
    html: str
    filename: str = "output.pdf"    # nome del file restituito, opzionale
    page_height: str = "1500mm"     # altezza pagina — default dal tuo script originale
    page_width: str = "300mm"       # larghezza pagina — default dal tuo script originale


# -------------- Endpoints ------------------------------------------------------------------------ #

@app.get("/")
def root():
    return {"status": "ok", "message": "HTML to PDF API è attiva"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/convert")
def convert_html_to_pdf(request: ConvertRequest):
    """
    Riceve un HTML come stringa e restituisce un PDF scaricabile.

    Body JSON atteso:
    {
        "html": "<html>...</html>",
        "filename": "mio-documento.pdf",   ← opzionale
        "page_height": "1500mm",           ← opzionale, default 1500mm
        "page_width": "300mm"              ← opzionale, default 300mm
    }
    """
    logger.info(f"Richiesta ricevuta — file: {request.filename} | dimensioni: {request.page_width} x {request.page_height}")

    # Le options vengono costruite a partire dai parametri della richiesta
    options = {
        'page-height': request.page_height,
        'page-width': request.page_width,
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': ''
    }

    try:
        # Converte l'HTML in PDF direttamente in memoria (nessun file temporaneo su disco)
        pdf_bytes = pdfkit.from_string(
            request.html,
            False,              # False = non salvare su file, restituisci bytes
            configuration=config,
            options=options
        )

        logger.info("Conversione completata con successo")

        # Restituisce il PDF come stream scaricabile
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )

    except Exception as e:
        logger.error(f"Errore durante la conversione: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Errore conversione: {str(e)}")
