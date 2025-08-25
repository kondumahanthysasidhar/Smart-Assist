import streamlit as st
import requests
import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# =======================================
# Configurations
# =======================================
JIRA_URL = "https://kondumahanthysasidhar-1756003049553.atlassian.net"
JIRA_EMAIL = "kondumahanthysasidhar@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0QZvU7GRWvJlCcenYxQ6uHLR7K8HeqWUnYSLzu6jckt1hn2wmKexr8jGzK4fjWS3LVWmfJ0NLGVe_1jgKGvOjAi_2dkcPCieri_3DmK2Zw0PYv-riuWrytzqOBTvS8-LEZU1luJUAb1t9mzrVeZGagX9-Jjb1opC8jWKKVIWSiCo=FFF03EAA"
PROJECT_KEY = "TEST123"
INDEX_NAME = "prodsupport"


# =======================================
# Cache Embedder
# =======================================
@st.cache_resource
def load_embedder():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedder = load_embedder()

def get_embedding(text: str):

    embedding = embedder.encode(text, convert_to_numpy=True)
    return embedding.tolist()


# =======================================
# Semantic Search with ES
# =======================================
def semantic_search(query_text, k=3):
    es = Elasticsearch(
        ["https://localhost:9200"],
        basic_auth=("elastic", "aGBptvP2zLgrr5gM7NrJ"),
        verify_certs=False
    )

    st.info(f"🔍 Searching for: **{query_text}**")
    query_vector = get_embedding(query_text)

    search_query = {
        "knn": {
            "field": "embedded_question",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 10
        }
    }

    try:
        response = es.search(index=INDEX_NAME, body=search_query)
        hits = response["hits"]["hits"]

        results = []
        for hit in hits:
            src = hit["_source"]
            results.append({
                "score": hit["_score"],
                "issue_id": src.get("issue_id"),
                "question": src.get("question"),
                "description": src.get("description"),
                "solution": src.get("solution")
            })
        return results
    except Exception as e:
        st.error(f"❌ Error during search: {e}")
        return []


# =======================================
# Create Jira Bug
# =======================================
def create_jira_bug(summary, description, issue_type="Bug"):
    url = f"{JIRA_URL}/rest/api/3/issue"

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ]
            },
            "issuetype": {"name": issue_type}
        }
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        return response_data["key"], f"{JIRA_URL}/browse/{response_data['key']}"
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP Error: {err}")
        st.error(f"Response Content: {err.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    return None, None


# =======================================
# Streamlit UI
# =======================================
st.set_page_config(page_title="Support Chat", layout="wide")
st.title("💬 Support Chatbot")

query = st.text_input("Enter your query")

col1, col2 = st.columns(2)

# --- Search Column ---
with col1:
    if st.button("🔍 Search Knowledge Base"):
        if query:
            with st.spinner("Searching knowledge base..."):
                results = semantic_search(query)
            if results:
                st.success(f"✅ Found {len(results)} results")
                for r in results:
                    st.markdown(f"""
                    **Issue ID:** {r['issue_id']}  
                    **Description:** {r['description']}  
                    **Solution:** {r['solution']}  
                    """)
            else:
                st.warning("No results found.")
        else:
            st.warning("Please enter a query.")

# --- Jira Column ---
with col2:
    st.subheader("🚨 Create Jira Bug")
    bug_summary = st.text_input("Bug Summary", value=query if query else "")
    bug_description = st.text_area("Bug Description", height=150, value="Describe the bug here...")
    bug_type = st.selectbox("Issue Type", ["Bug", "Task", "Story"])

    if st.button("Create Bug in Jira"):
        if bug_summary and bug_description:
            with st.spinner("Creating Jira bug..."):
                bug_id, bug_url = create_jira_bug(bug_summary, bug_description, bug_type)
            if bug_id:
                st.success(f"✅ Jira Bug created: [{bug_id}]({bug_url})")
            else:
                st.error("❌ Failed to create Jira Bug.")
        else:
            st.warning("Please enter both Summary and Description.")
