# HTML to PDF API

API FastAPI per convertire HTML in PDF. Pensata per girare su ZimaOS come container Docker e ricevere chiamate da N8N.

---

## Struttura del progetto

```
html-to-pdf-api/
  ├── main.py            ← FastAPI app
  ├── Dockerfile         ← istruzioni per Docker
  ├── requirements.txt   ← dipendenze Python
  └── README.md          ← questo file
```

---

## Deploy su ZimaOS

### 1. Copia i file sul server

Trasferisci la cartella `html-to-pdf-api` su ZimaOS.
Puoi usare SFTP, SCP, o una USB. Esempio con SCP da terminale Mac/Linux:

```bash
scp -r ./html-to-pdf-api utente@IP-ZIMAOS:/home/utente/
```

### 2. Entra nel server ZimaOS via SSH

```bash
ssh utente@IP-ZIMAOS
```

### 3. Vai nella cartella del progetto

```bash
cd html-to-pdf-api
```

### 4. Builda l'immagine Docker

Questo comando legge il Dockerfile e crea l'immagine. La prima volta ci vorrà qualche minuto (scarica Python, installa wkhtmltopdf, ecc.).

```bash
docker build -t html-to-pdf-api .
```

✅ Se vedi `Successfully built` e `Successfully tagged` sei a posto.

### 5. Avvia il container

```bash
docker run -d \
  --name html-to-pdf \
  --restart unless-stopped \
  -p 8000:8000 \
  html-to-pdf-api
```

Spiegazione dei flag:
- `-d` → gira in background (detached)
- `--name html-to-pdf` → nome leggibile del container
- `--restart unless-stopped` → si riavvia automaticamente se ZimaOS si riavvia
- `-p 8000:8000` → espone la porta 8000 all'esterno

### 6. Verifica che sia attivo

Apri il browser o usa curl:

```bash
curl http://IP-ZIMAOS:8000/health
```

Risposta attesa:
```json
{"status": "healthy"}
```

Puoi anche vedere la documentazione automatica dell'API (generata da FastAPI) su:
```
http://IP-ZIMAOS:8000/docs
```

---

## Comandi Docker utili

```bash
# Vedere i log in tempo reale
docker logs -f html-to-pdf

# Fermare il container
docker stop html-to-pdf

# Riavviare il container
docker restart html-to-pdf

# Vedere tutti i container attivi
docker ps

# Aggiornare l'app dopo modifiche al codice:
docker stop html-to-pdf
docker rm html-to-pdf
docker build -t html-to-pdf-api .
docker run -d --name html-to-pdf --restart unless-stopped -p 8000:8000 html-to-pdf-api
```

---

## Configurazione N8N

### Nodo: HTTP Request

| Campo | Valore |
|---|---|
| **Method** | `POST` |
| **URL** | `http://IP-ZIMAOS:8000/convert` |
| **Authentication** | None |
| **Body Content Type** | `JSON` |
| **Response Format** | `File` |

### Body JSON

```json
{
  "html": "{{ $json.html }}",
  "filename": "documento.pdf"
}
```

### Esempio body per test rapido in N8N

```json
{
  "html": "<html><body><h1>Test</h1><p>Funziona!</p></body></html>",
  "filename": "test.pdf"
}
```

---

## Test diretto via curl (utile per debug)

```bash
curl -X POST http://IP-ZIMAOS:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body><h1>Ciao</h1></body></html>", "filename": "test.pdf"}' \
  --output test.pdf
```

---

## Troubleshooting

**Il container non si avvia**
```bash
docker logs html-to-pdf
```

**wkhtmltopdf non trovato**
Entra nel container e verifica:
```bash
docker exec -it html-to-pdf bash
which wkhtmltopdf
wkhtmltopdf --version
```

**N8N non raggiunge l'API**
- Verifica che ZimaOS e N8N siano sulla stessa rete locale
- Prova a pingare l'IP di ZimaOS da dove gira N8N
- Controlla che la porta 8000 non sia bloccata da un firewall
