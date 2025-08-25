import streamlit as st
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from PyPDF2 import PdfReader

# ==============================
# RAG Setup
# ==============================
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Allow user to pick flan-t5-small (fast) or base (better, but heavier)
MODEL_OPTIONS = {
    "Flan-T5 Small (fast)": "google/flan-t5-small",
    "Flan-T5 Base (better, heavier)": "google/flan-t5-base"
}
selected_model = st.sidebar.selectbox("Choose Generator Model", list(MODEL_OPTIONS.keys()))
MODEL_ID = MODEL_OPTIONS[selected_model]

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
device = 0 if torch.cuda.is_available() else -1

# Load model safely (avoids meta tensor issues)
try:
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
except Exception as e:
    st.error(f"Error loading model {MODEL_ID}: {e}")
    model = None

if model:
    generator = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        device=device
    )
else:
    generator = None

index = None
corpus = []

# ==============================
# Email Generator Setup
# ==============================
email_generator = pipeline(
    "text2text-generation",
    model=MODEL_ID,
    tokenizer=tokenizer,
    device=device
)

EMAIL_TONES = [
    "formal", "polite", "friendly", "concise",
    "encouraging", "apologetic", "persuasive"
]

MAX_EMAIL_TOKENS = 500

def chunk_email_text(text, max_tokens=MAX_EMAIL_TOKENS):
    tokens = tokenizer.encode(text, truncation=False)
    chunks = [tokens[i:i+max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [tokenizer.decode(c) for c in chunks]

def generate_formal_email(recipient, subject, key_points, tone="formal"):
    # Instead of passing key_points directly, we instruct the model to rephrase them
    prompt = (
        f"You are an expert assistant that writes professional emails.\n"
        f"Task: Write a {tone} email to {recipient} with the subject '{subject}'.\n\n"
        f"Instructions:\n"
        f"- Rephrase and expand the following notes naturally, do NOT copy them word-for-word.\n"
        f"- Ensure the email has a clear introduction, body, and closing.\n"
        f"- Maintain the {tone} tone throughout.\n\n"
        f"Notes:\n{key_points}\n\n"
        f"Now write the complete email below:\n"
    )

    # Run generation once (no need to chunk unless user gives extremely long notes)
    output = email_generator(
        prompt,
        max_length=400,
        do_sample=True,             # allow creativity
        top_k=50,
        top_p=0.9,
        temperature=0.85,
        repetition_penalty=2.5,     # discourage repeats
        no_repeat_ngram_size=3      # avoid copy-paste loops
    )

    email_text = output[0]['generated_text'].strip()

    # Post-process: remove duplicate lines if any
    lines = []
    seen = set()
    for line in email_text.split("\n"):
        l = line.strip()
        if l and l.lower() not in seen:
            seen.add(l.lower())
            lines.append(l)
    return "\n".join(lines)# ==============================


import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key="AIzaSyBJkof8MSKqFBLJEVAYZOrWWWbNzdVCDRU")


def generate_email_from_g(recipient, subject, key_points, tone="formal"):
    """
    Generate an email using Gemini (Gemini 1.5 models).
    """

    prompt = (
        f"Write a {tone} email to {recipient} about '{subject}' "
        f"including the following points: {key_points}"
    )

    # Load the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-1.5-pro" for more capability

    # Generate response
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 250,
            "temperature": 0.7,
            "top_p": 0.92,
        }
    )

    # Extract the text from the response
    return response.text
# Example usage
# recipient = "John Doe"
# subject = "Project Update"
# key_points = "The project is on schedule, milestone 2 completed, next review meeting on Aug 28."
# tone = "formal"
#
# email_text = generate_email(recipient, subject, key_points, tone)
# print(email_text)


# Utilities
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

def load_docs_from_files(uploaded_files):
    docs = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    docs.extend(chunk_text(f"[Page {page_num}] {text}"))
        elif uploaded_file.name.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
            docs.extend(chunk_text(text))
    return docs

def build_index(docs):
    global index, corpus
    corpus = docs
    embeddings = embedder.encode(corpus, convert_to_numpy=True, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

def safe_truncate(text, max_length=400):
    tokens = tokenizer.encode(text, truncation=True, max_length=max_length)
    return tokenizer.decode(tokens)

def answer_query(query, top_k=5):
    global index, corpus
    if generator is None:
        return "Model not loaded correctly.", []
    if index is None or not corpus:
        return "No documents indexed yet. Please upload and process documents first.", []

    query_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, top_k)
    hits = [corpus[i] for i in I[0]]

    pairs = [[query, h] for h in hits]
    scores = cross_encoder.predict(pairs)
    reranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)

    context = "\n".join([r[0] for r in reranked[:3]])
    raw_prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {query}\nAnswer:"
    prompt = safe_truncate(raw_prompt, max_length=400)

    output = generator(prompt, max_new_tokens=200, do_sample=False)
    answer_text = output[0]['generated_text']

    sources = []
    for r in reranked[:3]:
        snippet = r[0][:200]
        page_info = ""
        if "[Page" in r[0]:
            page_info = r[0].split("]")[0] + "]"
        sources.append(f"{page_info} - {snippet}")
    return answer_text, sources

# ==============================
# Streamlit UI
# ==============================
st.title("📄 Document Q&A + Email Generator")

tab1, tab2 = st.tabs(["RAG Q&A", "Email Generator"])

# ------------------------------
# Tab 1: RAG Q&A
# ------------------------------
with tab1:
    uploaded_files = st.file_uploader("Upload PDFs or text files", type=["pdf", "txt"], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Process Documents"):
            docs = load_docs_from_files(uploaded_files)
            build_index(docs)
            st.success(f"{len(docs)} document chunks indexed!")

    query = st.text_input("Enter your question:")
    if st.button("Get Answer"):
        if query:
            with st.spinner("Generating answer..."):
                answer, sources = answer_query(query)
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Top Sources")
            for s in sources:
                st.write(s)

# ------------------------------
# Tab 2: Email Generator
# ------------------------------
with tab2:
    recipient = st.text_input("Recipient Name", "John Doe")
    subject = st.text_input("Email Subject", "Project Update")
    key_points = st.text_area("Key Points", "The project is on schedule, milestone 2 completed, next review meeting on Aug 28.")
    tone = st.selectbox("Tone", EMAIL_TONES)

    if st.button("Generate Email"):
        with st.spinner("Generating email..."):
            email_text = generate_email_from_g(recipient, subject, key_points, tone)
            st.subheader("Generated Email")
            st.write(email_text)

with tab3:
    st.subheader("💬 Support Assistant")
    user_query = st.text_area("Ask your question:")
    if st.button("Get Support Answer"):
        if user_query:
            with st.spinner("Searching knowledge base..."):
                answer, sources = rag_answer(user_query)
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Top Sources")
            for s in sources:
                st.write(s)

            if st.button("Not satisfied? Create JIRA Bug"):
                st.success("✅ A JIRA bug has been created with your query. (Simulated)")