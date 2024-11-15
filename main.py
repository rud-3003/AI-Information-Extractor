import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import time
import requests
import re
from groq import Groq
from typing import Dict

# Set up Streamlit page configuration
st.set_page_config(page_title="AI Information Extraction Agent", layout="wide")
st.title("AI Information Extraction Dashboard")

serp_api_key = st.secrets["serpapi"]["api_key"]

# Globally set the Groq API Key and model
groq_api_key = st.secrets["groq"]["api_key"]
client = Groq(api_key=groq_api_key)

# Function to display temporary status messages
def display_temp_message(message, status_type='info', duration=2):
    placeholder = st.empty()
    getattr(placeholder, status_type)(message)
    time.sleep(duration)
    placeholder.empty()

# Function to connect to Google Sheets
def connect_google_sheet(sheet_url):
    if "google_sheet_df" not in st.session_state:
        try:
            display_temp_message("Connecting to Google Sheets...", 'info')
            
            # Define the Google Sheets API scope
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            client = gspread.authorize(credentials)

            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            sheet = client.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)

            data = worksheet.get_all_records()
            st.session_state["google_sheet_df"] = pd.DataFrame(data)
        
        except gspread.exceptions.APIError as api_error:
            display_temp_message(f"Google Sheets API Error: {api_error}", 'error')
        except gspread.exceptions.SpreadsheetNotFound:
            display_temp_message("Spreadsheet not found. Please check the URL.", 'error')
        except Exception as e:
            display_temp_message(f"Error connecting to Google Sheets: {e}", 'error')
            st.session_state["google_sheet_df"] = None
    
    return st.session_state.get("google_sheet_df")

# Function to extract the placeholder from the prompt
def get_placeholder_column(prompt):
    match = re.search(r"{(.+?)}", prompt)
    return match.group(1) if match else None

# Function to perform a search using SerpAPI
def perform_search(entity_name, custom_prompt):
    # Replace the placeholder with the actual entity name in the custom prompt
    placeholder_column = get_placeholder_column(custom_prompt)
    query = custom_prompt.replace(f"{{{placeholder_column}}}", entity_name)
    
    # Set up SerpAPI parameters
    params = {
        "api_key": serp_api_key,
        "q": query,
        "location": "India",
        "google_domain": "google.com",
        "num": 3,  # Limit to a single result for efficiency
        "output": "json"
    }
    
    try:
        # Make the request and return the response as JSON
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200:
            result = response.json()
            
            # Check if search results contain snippets
            if "organic_results" in result and len(result["organic_results"]) > 0:
                # Extract the first snippet available
                snippet = result["organic_results"][0].get("snippet", "")
                if snippet:
                    return {"snippet": snippet}
                else:
                    display_temp_message(f"No snippet found for query: {query}", 'warning')
                    return None
            else:
                display_temp_message(f"No organic results for query: {query}", 'warning')
                return None
        else:
            display_temp_message(f"Error with SerpAPI request: {response.status_code}", 'error', duration=5)
            return None
    except requests.RequestException as e:
        display_temp_message(f"Request Error: {e}", 'error', duration=5)
        return None


# Function to extract information using Groq API
def extract_information_with_groq(entity_name: str, search_snippets: str, user_prompt: str):
    try:
        if not search_snippets.strip():
            return "Search snippets are empty. Cannot proceed with extraction."

        # Log received search snippet
        print(f"Search Snippet for '{entity_name}': {search_snippets}")

        # Replace any placeholder enclosed in {} with the entity_name
        full_prompt = re.sub(r"{.*?}", entity_name, user_prompt)
        full_prompt = (
            f"You are a helpful assistant tasked with extracting specific information. "
            f"{full_prompt} using the following search results:\n\n"
            f"{search_snippets}\n\n"
            "Please provide only the extracted information as a response."
        )

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


# Handling file uploads and Google Sheet inputs
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
sheet_url = st.text_input("Enter Google Sheet URL")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state["csv_df"] = df
        st.dataframe(df.head())
    except Exception as e:
        display_temp_message(f"CSV reading error: {e}", 'error')

if sheet_url:
    google_sheet_df = connect_google_sheet(sheet_url)
    if google_sheet_df is not None:
        st.dataframe(google_sheet_df.head())

csv_df = st.session_state.get("csv_df")
google_sheet_df = st.session_state.get("google_sheet_df")
active_df = csv_df if csv_df is not None else google_sheet_df

if active_df is not None:
    selected_column = st.selectbox("Select column for entities", active_df.columns)
    if selected_column:
        custom_prompt = st.text_input("Enter prompt (e.g., 'Find the location of {Fruits}')")
        
        # Add a button to trigger the extraction process
        if st.button("Run Extraction"):
            if custom_prompt:
                entities = active_df[selected_column].dropna().unique()
                search_results = {}
                extracted_info = {}

                # Display a temporary status message
                display_temp_message("Running extraction process...", 'info', duration=1)

                # Loop through entities and perform search + extraction
                for entity in entities:
                    search_result = perform_search(entity, custom_prompt)
                    if search_result:
                        search_snippet = search_result.get("snippet", "")
                        search_results[entity] = search_result
                        extracted_info[entity] = extract_information_with_groq(entity, search_snippet, custom_prompt)

                # Create a DataFrame to display the results
                extracted_info_df = pd.DataFrame(extracted_info.items(), columns=["Entity", "Extracted Information"])
                st.dataframe(extracted_info_df)

                # Add a download button for the extracted information
                st.download_button(
                    label="Download Extracted Information as CSV",
                    data=extracted_info_df.to_csv(index=False),
                    file_name="extracted_information.csv",
                    mime="text/csv"
                )

