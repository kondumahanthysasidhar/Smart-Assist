import torch
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from PyPDF2 import PdfReader


# ==============================
# Embedding & Reranking models
# ==============================
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# ==============================
# Generator model (Flan-T5 small for speed, switch to base if you want)
# ==============================
MODEL_ID = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
device = 0 if torch.cuda.is_available() else -1

generator = pipeline(
    "text2text-generation",
    model=MODEL_ID,
    tokenizer=MODEL_ID,
    device=device
)

# ==============================
# Global FAISS index + corpus
# ==============================
index = None
corpus = []  # will hold dicts: {"text": chunk, "page": n, "source": filename}


# ==============================
# Utility: GPU info
# ==============================
def getCuda():
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory // (1024 ** 3)
        return gpu_name, gpu_mem
    return "CPU", 0


# ==============================
# Chunking utility
# ==============================
def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ==============================
# Document loader with chunking + metadata
# ==============================
def load_docs_from_files(uploaded_files):
    """
    Reads PDF or text files and splits them into chunks with metadata.
    """
    docs = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                for chunk in chunk_text(text):
                    docs.append({
                        "text": chunk,
                        "page": page_num,
                        "source": uploaded_file.name
                    })
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
            for chunk in chunk_text(text):
                docs.append({
                    "text": chunk,
                    "page": None,
                    "source": uploaded_file.name
                })
    return docs


# ==============================
# Build FAISS index
# ==============================
def build_index(docs):
    """
    Builds a FAISS vector index from the given documents.
    """
    global index, corpus
    corpus = docs
    embeddings = embedder.encode([doc["text"] for doc in corpus],
                                 convert_to_numpy=True,
                                 show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)


# ==============================
# Safe truncation for generator
# ==============================
def safe_truncate(text, max_length=400):
    tokens = tokenizer.encode(text, truncation=True, max_length=max_length)
    return tokenizer.decode(tokens)


# ==============================
# Answer query (RAG)
# ==============================
def answer_query(query, top_k=5):
    """
    Answers a query using RAG and returns top sources with page numbers.
    """
    global index, corpus
    if index is None or not corpus:
        return "No documents indexed yet. Please upload and process documents first.", []

    # Step 1: Search FAISS
    query_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, top_k)
    hits = [corpus[i] for i in I[0]]

    # Step 2: Rerank
    pairs = [[query, h["text"]] for h in hits]
    scores = cross_encoder.predict(pairs)
    reranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)

    # Step 3: Build safe prompt
    context = "\n".join([r[0]["text"] for r in reranked[:3]])
    raw_prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {query}\nAnswer:"
    prompt = safe_truncate(raw_prompt, max_length=400)

    # Step 4: Generate
    output = generator(prompt, max_new_tokens=200, do_sample=False)
    answer_text = output[0]["generated_text"]

    # Return answer + top sources (snippet + page/source)
    sources = [
        f"{r[0]['source']} (page {r[0]['page']}) → {r[0]['text'][:200]}"
        if r[0]["page"] else f"{r[0]['source']} → {r[0]['text'][:200]}"
        for r in reranked[:3]
    ]

    return answer_text, sources
