from jira import JIRA

# Your Jira instance details and credentials
JIRA_URL = "https://kondumahanthysasidhar-1756003049553.atlassian.net/"
JIRA_EMAIL = "kondumahanthysasidhar@gmail.com"
# jira_token = "ATATT3xFfGF0YiqxIYvOFWuPTwIMThRbWdkae39iTunSCNigOzt32c1xoFu6605Rgp5rnHBNWiDD-0xaD6GtFxJFYEmCQf1Bd4EnWAXw18J2wTvKqqqNvxeghz1C9kDd16c3bbBcM9sISqefa7MpgHR4yZKTj804m6jz83aU7Er-XLj36YGqwkY=85A10F48"  # Generate from Atlassian account
JIRA_API_TOKEN = "ATATT3xFfGF0QZvU7GRWvJlCcenYxQ6uHLR7K8HeqWUnYSLzu6jckt1hn2wmKexr8jGzK4fjWS3LVWmfJ0NLGVe_1jgKGvOjAi_2dkcPCieri_3DmK2Zw0PYv-riuWrytzqOBTvS8-LEZU1luJUAb1t9mzrVeZGagX9-Jjb1opC8jWKKVIWSiCo=FFF03EAA"
import requests
import json
import os

# --- Configuration ---
# It's best practice to load these from environment variables rather than hardcoding.
# JIRA_URL = "https://your-domain.atlassian.net"
# JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "your-email@example.com")
# JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "your_api_token_here")
PROJECT_KEY = "TEST123"  # The key for your Jira project


def create_jira_story(summary, description, issue_type="Bug"):
    """
    Creates a story in a Jira project.
    """
    url = f"{JIRA_URL}/rest/api/3/issue"

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }

    print(f"Sending request to create story: '{summary}'")

    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        print(f"Successfully created story! Key: {response_data['key']}")
        print(f"URL: {JIRA_URL}/browse/{response_data['key']}")
        return response_data

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"Response Content: {err.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return None


if __name__ == "__main__":
    # --- Define the story you want to create ---
    story_summary = "Automated Story: Set up new user account"
    story_description = "As a new employee, I need an account to access the company's internal systems."

    # --- Create the story ---
    create_jira_story(story_summary, story_description)