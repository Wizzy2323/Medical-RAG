# Medical-RAG - Medical Document Q&A using RAG

MedAssist is a FastAPI-based retrieval-augmented generation application that answers questions from user-uploaded medical PDFs. It combines PDF text extraction, semantic chunk retrieval with FAISS, and a local Ollama language model.

> MedAssist provides document-grounded information, not diagnosis or medical advice. A qualified healthcare professional should verify important medical conclusions.

## Features

- JWT-authenticated user registration and login
- User-specific PDF document storage
- PDF text extraction with PyMuPDF
- Configurable word-based text chunking
- Sentence-Transformer embeddings and FAISS similarity search
- Context-grounded answers through Ollama
- Document and retrieval evaluation utilities

## Tech Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Database | MySQL |
| Embeddings | Sentence Transformers |
| Vector search | FAISS |
| PDF parsing | PyMuPDF |
| Language model | Ollama |
| Authentication | JWT and bcrypt |

## Project Structure

```text
MedAssist/
  app/
    auth.py
    chunker.py
    database.py
    llm.py
    main.py
    pdf_utils.py
    retrieval.py
    evaluate.py
    schema_chunks.sql
```

## Setup

### 1. Create the environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configure MySQL and environment variables

Create the database and required tables. Copy `.env.example` to `.env`, then set the database credentials and a long random `MEDASSIST_SECRET_KEY`.

PowerShell environment variables can also be set temporarily:

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="your-password"
$env:DB_NAME="medassist"
$env:MEDASSIST_SECRET_KEY="replace-with-a-long-random-secret"
```

Run the schema against your `medassist` database:

```powershell
mysql -u root -p medassist < MedAssist/app/schema_chunks.sql
```

Your database must also contain `users`, `documents`, and the existing related tables referenced by the application.

### 3. Install and run Ollama

```powershell
ollama pull llama3.2:3b
ollama serve
```

### 4. Start the API

Run from the repository root:

```powershell
$env:PYTHONPATH="MedAssist"
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Evaluation

```powershell
$env:PYTHONPATH="MedAssist"
python -m app.evaluate
python -m app.evaluate --llm
```

The retrieval evaluation sweeps chunk sizes and top-k values. The optional `--llm` mode adds answer accuracy and latency measurement.

## API Overview

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Service health check |
| `/auth/register` | POST | Create an account |
| `/auth/login` | POST | Obtain a JWT |
| `/auth/token` | POST | OAuth-compatible login |
| `/documents` | GET | List documents for the current user |
| `/documents/upload` | POST | Upload and index a PDF |
| `/chat` | POST | Ask a document-grounded question |

## Security

Never commit `.env` or database credentials. Use a strong, private JWT secret and restrict database permissions in deployed environments.

## License

This project is available under the MIT License.
