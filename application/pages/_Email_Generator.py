import streamlit as st

st.set_page_config(page_title="Email Generator", layout="wide")


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










st.title("✉️ AI Email Generator")




recipient = st.text_input("Recipient")
subject = st.text_input("Subject")
key_points = st.text_area("Key Points")
tone = st.selectbox("Tone", ["formal", "polite", "friendly", "concise", "apologetic"])

if st.button("Generate Email"):
    with st.spinner("Generating email..."):
        email_text = generate_email_from_g(recipient, subject, key_points, tone)
        st.subheader("Generated Email")
        st.write(email_text)
