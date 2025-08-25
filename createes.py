import json
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# --- Configuration ---
ES_HOST = "http://localhost:9200"
INDEX_NAME = "prodsupport"

# --- Connect to Elasticsearch ---
try:
    es = Elasticsearch(
    ["https://localhost:9200"],
    basic_auth=("elastic", "aGBptvP2zLgrr5gM7NrJ"),
    verify_certs=False
)
    if not es.ping():
        raise ConnectionError("Could not connect to Elasticsearch.")
    print("✅ Successfully connected to Elasticsearch.")
except Exception as e:
    print(f"❌ An error occurred during connection: {e}")
    exit()

# index_mapping = {
#     "mappings": {
#         "properties": {
#             "issue_id": {"type": "integer"},
#             "description": {"type": "text"},
#             "solution": {"type": "text"},
#             "question": {"type": "text"},
#             "attachments": {"type": "keyword"},
#             "embedded_question": {
#                 "type": "dense_vector",
#                 "dims": 384,   # dimension of sentence-transformers/all-MiniLM-L6-v2
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }
#
# # Delete old index if exists
# if es.indices.exists(index=INDEX_NAME):
#     es.indices.delete(index=INDEX_NAME)
#
# # Create fresh index
# es.indices.create(index=INDEX_NAME, body=index_mapping)
# print(f"✅ Index '{INDEX_NAME}' created successfully.")
#
# --- Embedding Model ---
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#
def get_embedding(text: str):
    """
    Generates a dense vector embedding for a given text.
    """
    embedding = embedder.encode(text, convert_to_numpy=True)
    return embedding.tolist()
#
#
# # --- Sample Documents (list of dicts) ---
def ingest():
    sample_documents = [
        {
            "issue_id": 12345,
            "description": "The 'Submit' button on the contact form is not working when a user clicks it.",
            "solution": "Updated the JavaScript event listener for the button to correctly handle the 'click' event.",
            "question": "What is the expected behavior when a user clicks the 'Submit' button?",
            "attachments": ["screenshot_form_error.png", "log_file_2023-10-27.txt"],
            "embedded_question": get_embedding("What is the expected behavior when a user clicks the 'Submit' button?")
        },
        {
            "issue_id": 12346,
            "description": "Landing page is not getting loaded even after successful onboarding and getting errored out",
            "solution": "Try to wait for for 15 mins and try again as the ETL is being run",
            "question": "Landing page is not getting loaded even after successful onboarding and getting errored out",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("Landing page is not getting loaded even after successful onboarding and getting errored out")
        },
        {
            "issue_id": 12347,
            "description": "Error while loading audit",
            "solution": "Dev team needs team is working on it will get it fixed shortly",
            "question": "audit trail is getting failed",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("audit trail is getting failed")
        },
        {
            "issue_id": 12348,
            "description": "client user is not able to view our product",
            "solution": "Use associate portal and add respective client user permissions",
            "question": "Why does client user not able to see our product",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("Why does client user not able to see our product")
        },
        {
            "issue_id": 12349,
            "description": "what is header lockout",
            "solution": "header lockout is a period during which tax system will not allow changes from tax credits",
            "question": "what is header lockout?",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("what is header lockout?")
        },
        {
            "issue_id": 12340,
            "description": "I am not able to view assigned client user for a client",
            "solution": "Makes sure you have added appropriate permissions and also the user is active , and not suspended",
            "question": "I am not able to view assigned client user for a client",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("I am not able to view assigned client user for a client")
        },
        {
            "issue_id": 12341,
            "description": "I have made a mistake in credit package",
            "solution": "You can archive the credit package and then re upload the latest credit package",
            "question": "I have made a mistake in credit package",
            "attachments": ["login_error.png"],
            "embedded_question": get_embedding("I have made a mistake in credit package")
        }
    ]

    # --- Index the Documents ---
    for doc in sample_documents:
        try:
            response = es.index(
                index=INDEX_NAME,
                id=doc["issue_id"],
                document=doc
            )
            print(f"✅ Document {doc['issue_id']} indexed successfully. Response: {response['result']}")
        except Exception as e:
            print(f"❌ Error while indexing document {doc['issue_id']}: {e}")


# --- Semantic Search ---
def semantic_search(query_text, k=3):
    """
    Performs a semantic search using kNN on the embedded_question field.
    """
    print(f"\n🔍 Searching for: '{query_text}'")
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
        response = es.search(
            index=INDEX_NAME,
            body=search_query
        )
        hits = response["hits"]["hits"]
        print(f"✅ Found {len(hits)} results.")
        for hit in hits:
            src = hit["_source"]
            print("---")
            print(f"Score: {hit['_score']}")
            print(f"Issue ID: {src['issue_id']}")
            print(f"Question: {src['question']}")
            print(f"Description: {src['description']}")
            print(f"Solution: {src['solution']}")
    except Exception as e:
        print(f"❌ Error during search: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    user_query = "server error"
    # semantic_search(user_query, k=2)
    ingest()
# "ATATT3xFfGF0YiqxIYvOFWuPTwIMThRbWdkae39iTunSCNigOzt32c1xoFu6605Rgp5rnHBNWiDD-0xaD6GtFxJFYEmCQf1Bd4EnWAXw18J2wTvKqqqNvxeghz1C9kDd16c3bbBcM9sISqefa7MpgHR4yZKTj804m6jz83aU7Er-XLj36YGqwkY=85A10F48"