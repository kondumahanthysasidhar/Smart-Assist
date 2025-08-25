import streamlit as st
import torch
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from PyPDF2 import PdfReader

st.set_page_config(page_title="RAG Document QA", layout="wide")
st.title("📄 Document Q&A with RAG")

# ==============================Ś
# Cached Model Loaders
# ==============================
@st.cache_resource
def load_embedder():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def load_cross_encoder():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

@st.cache_resource
def load_generator():
    MODEL_ID = "google/flan-t5-small"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    device = 0 if torch.cuda.is_available() else -1
    gen = pipeline(
        "text2text-generation",
        model=MODEL_ID,
        tokenizer=MODEL_ID,
        device=device
    )
    return gen, tokenizer

# Load models once
embedder = load_embedder()
cross_encoder = load_cross_encoder()
generator, tokenizer = load_generator()

# ==============================
# Initialize session state
# ==============================
if "index" not in st.session_state:
    st.session_state.index = None
if "corpus" not in st.session_state:
    st.session_state.corpus = []

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
# Document loader
# ==============================
def load_docs_from_files(uploaded_files):
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
    embeddings = embedder.encode(
        [doc["text"] for doc in docs],
        convert_to_numpy=True,
        show_progress_bar=True
    )
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


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
    if st.session_state.index is None or not st.session_state.corpus:
        return "No documents indexed yet. Please upload and process documents first.", []

    # Step 1: Search FAISS
    query_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = st.session_state.index.search(query_emb, top_k)
    hits = [st.session_state.corpus[i] for i in I[0]]

    # Step 2: Rerank
    pairs = [[query, h["text"]] for h in hits]
    scores = cross_encoder.predict(pairs)
    reranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)

    # Step 3: Prompt
    context = "\n".join([r[0]["text"] for r in reranked[:3]])
    raw_prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {query}\nAnswer:"
    prompt = safe_truncate(raw_prompt, max_length=400)

    # Step 4: Generate
    output = generator(prompt, max_new_tokens=200, do_sample=False)
    answer_text = output[0]["generated_text"]

    # Step 5: Sources
    sources = [
        f"{r[0]['source']} (page {r[0]['page']}) → {r[0]['text'][:200]}"
        if r[0]["page"] else f"{r[0]['source']} → {r[0]['text'][:200]}"
        for r in reranked[:3]
    ]
    return answer_text, sources


# =========================================================================================
# ✅ CUDA status flag
gpu_name, gpu_mem = getCuda()
st.success(f"✅ CUDA available: {gpu_name} ({gpu_mem} GB VRAM)")

uploaded_files = st.file_uploader("Upload your documents (PDF/TXT)", type=["pdf", "txt"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Process Documents"):
        with st.spinner("Building index..."):
            docs = load_docs_from_files(uploaded_files)
            st.session_state.corpus = docs
            st.session_state.index = build_index(docs)
        st.success("✅ Documents processed and indexed!")

query = st.text_input("Ask a question:")

if query:
    with st.spinner("Generating answer..."):
        answer, sources = answer_query(query)
    st.subheader("Answer")
    st.write(answer)

    if sources:
        st.subheader("Top Sources")
        for i, s in enumerate(sources, 1):
            st.markdown(f"**Source {i}:** {s}")
