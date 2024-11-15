import os
from groq import Groq
import streamlit as st

# Set your Groq API key here (consider storing it as an environment variable for security)
groq_api_key = st.secrets["groq"]["api_key"]

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

def extract_information_with_groq(entity_name: str, search_snippets: str, user_prompt: str):
    try:
        # Check if search snippets are not empty
        if not search_snippets.strip():
            return "Search snippets are empty. Cannot proceed with extraction."

        # Constructing the prompt
        full_prompt = (
            f"You are a helpful assistant tasked with extracting specific information. "
            f"{user_prompt.replace('{Company}', entity_name)} using the following search results:\n\n"
            f"{search_snippets}\n\n"
            "Please provide only the extracted information as a response."
        )

        print("\n--- Prompt Sent to Groq API ---")
        print(full_prompt)

        # Making the API call
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an assistant that extracts specific information."},
                {"role": "user", "content": full_prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.0,
            max_tokens=512,
            top_p=1.0
        )

        print("\n--- Full Groq API Response ---")
        print(response)

        # Checking if response contains choices and content correctly
        if response and response.choices:
            extracted_content = response.choices[0].message.content
            if extracted_content:
                return extracted_content
            return "Groq API returned content, but it was empty."
        else:
            return "Groq API returned an empty response."

    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return f"Error during Groq API call: {e}"

# Example usage
if __name__ == "__main__":
    entity = "OpenAI"
    search_snippets = """
    OpenAI is an AI research and deployment company. Our mission is to ensure that artificial general intelligence benefits all of humanity.
    Contact email: info@openai.com.
    """
    user_prompt = "Get me the email of {Company}"

    result = extract_information_with_groq(entity, search_snippets, user_prompt)
    print("\nExtracted Information:", result)
