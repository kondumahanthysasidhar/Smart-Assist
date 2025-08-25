import streamlit as st

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Smart Assistant",
    page_icon="💼",
    layout="wide",
)

# ==============================
# CUSTOM CSS (ADP-like styling)
# ==============================
st.markdown("""
    <style>
        /* Global Styling */
        .stApp {
            background-color: #ffffff;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: #2b2b2b;
        }

        /* Navbar */
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 1rem;
            background-color: #00338D; /* ADP corporate blue */
            border-bottom: 2px solid #f0f0f0;
        }
        .nav-button {
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            background: transparent;
            color: #ffffff;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: 0.3s;
            font-size: 16px;
        }
        .nav-button:hover {
            background: #0050d4;
        }

        /* Active Tab */
        .active-tab {
            background: #0050d4;
            font-weight: 600;
        }

        /* Card Containers */
        .card {
            background: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }

        /* Section Headings */
        h2, h3, h4 {
            color: #00338D;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# NAVIGATION BAR
# ==============================
tabs = ["📄 RAG Q&A", "✉️ Email Generator", "💬 Support Chat", "⚙️ Settings"]

if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = tabs[0]

def set_tab(tab):
    st.session_state["selected_tab"] = tab

# Render navbar
st.markdown('<div class="nav-container">' +
    "".join([f'<button class="nav-button {"active-tab" if tab == st.session_state["selected_tab"] else ""}" onclick="window.location.href=\'#{tab.replace(" ", "-")}\';">{tab}</button>'
             for tab in tabs]) +
    '</div>', unsafe_allow_html=True)

# ==============================
# TAB CONTENT
# ==============================
selected_tab = st.session_state["selected_tab"]

if selected_tab == "📄 RAG Q&A":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Ask Questions from Documents 📚")
    st.file_uploader("Upload PDFs or TXT files", type=["pdf", "txt"], accept_multiple_files=True)
    st.text_input("Enter your question:")
    st.button("Get Answer")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "✉️ Email Generator":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Generate Professional Emails ✍️")
    st.text_input("Recipient")
    st.text_input("Subject")
    st.text_area("Key Points")
    st.selectbox("Tone", ["formal", "polite", "friendly", "concise", "encouraging", "apologetic", "persuasive"])
    st.button("Generate Email")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "💬 Support Chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Support Chatbot 🤝")
    st.text_input("Ask your support question")
    st.button("Search Knowledge Base")
    st.button("Create Jira Bug 🚨")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "⚙️ Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("App Settings ⚡")
    st.toggle("Dark Mode")
    st.text_input("API Key")
    st.button("Save Settings")
    st.markdown('</div>', unsafe_allow_html=True)
