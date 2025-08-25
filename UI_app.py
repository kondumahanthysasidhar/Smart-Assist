import streamlit as st

from application.RAG import load_docs_from_files, build_index, answer_query, getCuda

st.set_page_config(page_title="RAG Document QA", layout="wide")

st.title("📄 Document Q&A with RAG (Zephyr-7B)")
# ✅ CUDA status flag
gpu_name,gpu_mem = getCuda()
st.success(f"✅ CUDA available: {gpu_name} ({gpu_mem} GB VRAM)")

uploaded_files = st.file_uploader("Upload your documents (PDF/TXT)", type=["pdf", "txt"], accept_multiple_files=True)

if uploaded_files:
    if st.button("Process Documents"):
        with st.spinner("Building index..."):
            docs = load_docs_from_files(uploaded_files)
            build_index(docs)
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
