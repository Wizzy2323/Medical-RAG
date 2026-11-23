

from pydantic import BaseModel
from app.llm import generate_answer

from fastapi.security import OAuth2PasswordRequestForm
from app.retrieval import retrieve_user_chunks, index_document


from app.database import get_documents_by_user, create_document, create_user, get_current_user, get_user_by_email
from app.auth import hash_password
from app.auth import (
    verify_password,
    create_access_token
)

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from app.pdf_utils import extract_text_from_pdf

from jose import jwt, JWTError

import time

app = FastAPI()


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user)
):
    start = time.time()

    print("Received question:", request.question)

    chunks = retrieve_user_chunks(user_id, request.question)
    print("Retrieval completed in", round(time.time() - start, 2), "seconds")

    if not chunks:
        return {
            "answer": "No documents found. Please upload a document first."
        }

    context = "\n\n".join(chunks)

    llm_start = time.time()

    answer = generate_answer(
        request.question,
        context
    )

    print("LLM completed in", round(time.time() - llm_start, 2), "seconds")

    return {
        "answer": answer
    }


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@app.post("/auth/register")
def register(request: RegisterRequest):

    existing_user = get_user_by_email(request.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    password_hash = hash_password(request.password)

    create_user(
        request.name,
        request.email,
        password_hash
    )

    return {
        "message": "User registered successfully"
    }


class LoginRequest(BaseModel):
    email: str
    password: str



@app.post("/auth/login")
def login(request: LoginRequest):

    user = get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user_id = user[0]
    password_hash = user[3]

    if not verify_password(
        request.password,
        password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user_id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }



@app.get("/documents")
def get_documents(
    user_id: int = Depends(get_current_user)
):

    documents = get_documents_by_user(user_id)

    return {
        "documents": documents
    }

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user)
):
    
    file_bytes = await file.read()

    text = extract_text_from_pdf(file_bytes)

    document_id = create_document(
        user_id,
        file.filename,
        file.content_type,
        text
    )
    chunk_count = index_document(user_id, document_id, text)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "text_length": len(text),
        "chunks_indexed": chunk_count
    }



@app.post("/auth/token")
def login_form(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form.username)

    if not user or not verify_password(form.password, user[3]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "access_token": create_access_token(user[0]),
        "token_type": "bearer"
    }