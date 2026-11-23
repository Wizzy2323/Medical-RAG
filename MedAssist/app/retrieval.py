import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.chunker import chunk_text
from app.database import create_chunks, get_chunks_by_user

# Defaults chosen from the evaluation sweep (see app/evaluate.py)
CHUNK_SIZE = 100
OVERLAP = 20
TOP_K = 3

model = SentenceTransformer("all-MiniLM-L6-v2")

# user_id -> (faiss index, chunk texts)
_index_cache = {}


def embed_texts(texts):
    embeddings = model.encode(texts)
    return np.array(embeddings, dtype="float32")


def build_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


def search_index(index, chunks, question, top_k=TOP_K):
    k = min(top_k, len(chunks))
    query_embedding = embed_texts([question])
    distances, indices = index.search(query_embedding, k)

    return [chunks[i] for i in indices[0] if i != -1]


def index_document(
    user_id,
    document_id,
    text,
    chunk_size=CHUNK_SIZE,
    overlap=OVERLAP
):
    """Chunk -> embed -> store in MySQL. Returns number of chunks."""
    chunks = chunk_text(text, chunk_size, overlap)

    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    create_chunks(
        document_id,
        user_id,
        [(c, e.tobytes()) for c, e in zip(chunks, embeddings)]
    )

    _index_cache.pop(user_id, None)

    return len(chunks)


def _load_user_index(user_id):
    if user_id in _index_cache:
        return _index_cache[user_id]

    rows = get_chunks_by_user(user_id)

    if not rows:
        return None

    chunks = [r[0] for r in rows]
    embeddings = np.vstack(
        [np.frombuffer(r[1], dtype="float32") for r in rows]
    )

    entry = (build_index(embeddings), chunks)
    _index_cache[user_id] = entry

    return entry


def retrieve_user_chunks(user_id, question, top_k=TOP_K):
    entry = _load_user_index(user_id)

    if entry is None:
        return []

    index, chunks = entry

    return search_index(index, chunks, question, top_k)
