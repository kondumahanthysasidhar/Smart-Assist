import os
import requests
from elasticsearch import Elasticsearch
from uuid import uuid4
import time

# === Config ===
GEMINI_API_KEY = 'AIzaSyBJkof8MSKqFBLJEVAYZOrWWWbNzdVCDRU'
GEMINI_EMBEDDING_URL = "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"


def create_connection():
    es = Elasticsearch("http://localhost:9200",http_auth=('elastic','+KSJW_0otPNu7Mt4ek4P'))
    if(es.ping() == True):
        return es
    else:
        return ''
elastic = create_connection()
# === Step 1: Chunk Text ===
def chunk_text(text, max_tokens=300):
    sentences = text.split('.')
    chunks = []
    current = ""
    for sentence in sentences:
        if len((current + sentence).split()) < max_tokens:
            current += sentence + '.'
        else:
            chunks.append(current.strip())
            current = sentence + '.'
    if current:
        chunks.append(current.strip())
    return chunks

# === Step 2: Get Embedding from Gemini ===
def get_gemini_embedding(text):
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    response = requests.post(GEMINI_EMBEDDING_URL, headers=headers, params=params, json=body)
    response.raise_for_status()
    return response.json()['embedding']['values']

# === Step 3: Index into Elasticsearch ===
def index_chunks(pdf_id, chunks):
    for i, chunk in enumerate(chunks):
        vector = get_gemini_embedding(chunk)
        elastic.index(index="pdf_chunks", id=f"{pdf_id}_{i}", body={
            "pdf_id": pdf_id,
            "chunk": chunk,
            "embedding": vector,
            "chunk_id": f"{pdf_id}_{i}"
        })

# === Step 4: Query Handler ===
def search_chunks(pdf_id, query, top_k=5):
    query_vector = get_gemini_embedding(query)
    script_query = {
        "script_score": {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"pdf_id": pdf_id}}
                    ]
                }
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }
    res = elastic.search(index="pdf_chunks", body={"size": top_k, "query": script_query})
    return [(hit['_source']['chunk'], hit['_source']['chunk_id']) for hit in res['hits']['hits']]

# === Step 5: Ask Gemini 1.5 Pro ===
def ask_gemini(query, context_chunks):
    context = "\n---\n".join([f"[Chunk ID: {cid}]\n{chunk}" for chunk, cid in context_chunks])
    payload = {
        "contents": [
            {"role": "user", "parts": [
                {"text": f"Context:\n{context}\n\nQuestion: {query}\n\nPlease cite the chunk IDs used in the answer."}
            ]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
    response = requests.post(url, headers=headers, params=params, json=payload)
    response.raise_for_status()
    return response.json()['candidates'][0]['content']['parts'][0]['text']

# === Usage ===
if __name__ == "__main__":
    create_connection()
    input_text = """
    This agreement may be terminated by either party upon 30 days written notice.
All intellectual property remains with the original owner.
    Payment is due within 15 days of invoice receipt.
    The confidentiality clause survives termination.
    """
    pdf_id = str(uuid4())

    # Ingest
    chunks = chunk_text(input_text)
    index_chunks(pdf_id, chunks)

    # Query
    question = "How can either party terminate the agreement?"
    results = search_chunks(pdf_id, question)
    time.sleep(120)
    answer = ask_gemini(question, results)
    print("Answer:\n", answer)
