import streamlit as st
from transformers import pipeline

# ==============================
# Streamlit Setup
# ==============================
st.set_page_config(page_title="Summarizer", layout="wide")
st.title("📝 Text Summarizer")
st.write("Paste text below (or upload a large file) and get a concise summary!")

# ==============================
# Load Summarizer (cached)
# ==============================
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="google/flan-t5-small")

summarizer = load_summarizer()

# ==============================
# Chunking Utility for Large Texts
# ==============================
def chunk_text(text, max_chunk_length=1000, overlap=100):
    """Split long text into overlapping chunks to avoid token limit issues."""
    words = text.split()
    chunks, start = [], 0

    while start < len(words):
        end = min(start + max_chunk_length, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_chunk_length - overlap
    return chunks

# ==============================
# Input Section
# ==============================
text_input = st.text_area("✍️ Enter text here", height=300)

uploaded_file = st.file_uploader("Or upload a text file", type=["txt"])
if uploaded_file:
    text_input = uploaded_file.read().decode("utf-8")

# ==============================
# Summarization Logic
# ==============================
if st.button("Generate Summary"):
    if text_input.strip():
        with st.spinner("Summarizing..."):
            chunks = chunk_text(text_input, max_chunk_length=700, overlap=50)
            partial_summaries = []

            for i, chunk in enumerate(chunks, start=1):
                st.info(f"⏳ Summarizing chunk {i}/{len(chunks)}...")
                summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]["summary_text"]
                partial_summaries.append(summary)

            # Combine summaries into a final summary
            final_input = " ".join(partial_summaries)
            final_summary = summarizer(final_input, max_length=200, min_length=60, do_sample=False)[0]["summary_text"]

        st.subheader("📌 Final Summary")
        st.write(final_summary)

        st.subheader("🔍 Intermediate Summaries (per chunk)")
        for i, s in enumerate(partial_summaries, start=1):
            st.markdown(f"**Chunk {i}:** {s}")
    else:
        st.warning("⚠️ Please enter some text or upload a file.")
