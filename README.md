# AI Information Extraction Dashboard

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Installation & Setup](#installation--setup)
5. [Environment Variables](#environment-variables)
6. [How to Run](#how-to-run)
7. [Video Demonstration](#video-demonstration)
8. [License](#license)

---

## Project Overview
This project is an **AI Information Extraction Dashboard** built using Streamlit. It integrates with **Google Sheets**, **SerpAPI**, and the **Groq API** to extract relevant information from online search snippets based on user prompts. The system allows users to input custom queries, perform searches, and extract structured information using a pre-trained language model.

## Features
- Connects to Google Sheets for reading data.
- Performs automated web searches using SerpAPI.
- Extracts relevant information from search results using the Groq API.
- Supports uploading CSV files.
- Allows users to download extracted information as a CSV file.

## Tech Stack
- **Streamlit**: Web interface
- **Pandas**: Data manipulation
- **gspread**: Google Sheets API integration
- **Google OAuth2**: For authentication with Google Sheets
- **SerpAPI**: For performing Google searches
- **Groq API**: For natural language processing and information extraction

---

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- `pip` package manager

### Required Python Packages
Install the necessary dependencies:

```bash
pip install streamlit pandas gspread google-auth requests
```

### Cloning the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

## Environment Variables
The project requires access to various API keys and service account credentials. Create a `secrets.toml` file in the `.streamlit` folder with the following structure:

```bash
# .streamlit/secrets.toml

[serpapi]
api_key = "YOUR_SERPAPI_KEY"

[groq]
api_key = "YOUR_GROQ_API_KEY"

[gcp_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "your_private_key"
client_email = "your_client_email"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your_client_cert_url"
```
`Note`: Ensure the `.streamlit/secrets.toml` file is not tracked by Git for security purposes.

## How to Run
1. Upload or Connect to Google Sheets:
 - You can either upload a CSV file or enter a Google Sheets URL.
2. Select a Column: Choose the column containing the entities you want to search for.
3. Enter a Custom Prompt: Enter a prompt, e.g., Find the location of {Entity}.
4. Click the Button: Click the "Run Extraction" button to initiate the search and extraction process.
To start the Streamlit app:

```bash
Copy code
streamlit run main.py
```

## Video Demonstration
For a complete walkthrough and demonstration of how this project works, watch the video below:

[![Watch the video](https://img.youtube.com/vi/9M7a7lVSsfI/maxresdefault.jpg)](https://www.youtube.com/watch?v=9M7a7lVSsfI)

## License
This project is licensed under the MIT License.
