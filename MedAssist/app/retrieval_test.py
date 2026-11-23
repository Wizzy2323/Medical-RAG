from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
model = SentenceTransformer("all-MiniLM-L6-v2")
chunks = [
    "The patient reported occasional headaches.",
    "Hemoglobin was measured at 11.2 g/dL.",
    "The patient was prescribed iron supplements.",
    "Blood pressure was recorded as 130/85."
]
chunk_embeddings = model.encode(chunks)
chunk_embeddings = np.array(
    chunk_embeddings,
    dtype="float32"
)
dimension = chunk_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(chunk_embeddings)
def retrieve_chunks(question:str):

    query = question

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )

    distances, indices = index.search(
        query_embedding,
        2
    )
    retrieved_chunks=[];

    for i in range(len(indices[0])):
        chunk_id = indices[0][i]

        retrieved_chunks.append(chunks[chunk_id])

    return retrieved_chunks