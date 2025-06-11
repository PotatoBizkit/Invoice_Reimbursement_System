# Invoice_Reimbursement_System
## Project Overview

This project is a smart **Invoice Reimbursement System** designed to help and analyze whether uploaded expense invoices are to be **fully reimbursed**, **partially reimbursed**, or **declined** by comparing against company policy document and a simple **RAG (Retrieval-Augmented Generation) chatbot** is designed to retrieve information about processed invoices based on user query.

## Installation Instructions

To run this project locally:

1. **Clone this repository**  
   ```bash
   git clone https://github.com/PotatoBizkit/Invoice_Reimbursement_System.git
   cd Invoice_Reimbursement_System
   
2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate     # Linux/macOS
   env\Scripts\activate      # Windows

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Run the server**
   ```bash
   uvicorn main:app --reload

5. **For testing the chatbot endpoint**
   ```bash
   uvicorn ragbot:app --reload

## Usage Guide

API Endpoint 1: Analyze Invoices
* Endpoint: /analyze_invoices
* Method: POST
* Form Data Required:
  * policy_file (DOCX file)
  * invoices_zip (ZIP containing PDFs)
  * employee_name (String)

  Curl Example:
     ```bash
     curl -X POST http://127.0.0.1:8000/analyze_invoices \
       -F "policy_file=@Dataset/Policy-Nov-2024.pdf.docx" \
       -F "invoices_zip=@Dataset/Cab Bills.zip" \
       -F "employee_name=Gojo Satoru"

This will:
* Extract the text from the policy and each invoice.
* Call a Groq-hosted LLaMA model to determine reimbursement status.
* Store all invoice data into a ChromaDB vector database.

API Endpoint 2: RAG Chatbot
* Endpoint: /ragbot
* Method: POST
* Body: JSON
  * query: your question about any stored invoice(s)

  Curl Example:
    ```bash
    curl -X POST http://127.0.0.1:8000/ragbot \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"Show me all fully reimbursed invoices for Yuji\"}"

Returns a chatbot-style response using RAG (retrieves invoice context, then uses LLM to reply).

## Technical Details

* Framework: FastAPI
* LLM Provider: Groq using meta-llama/llama-4-scout-17b-16e-instruct
* Embedding Model: all-MiniLM-L6-v2 from SentenceTransformers
* Vector Database: ChromaDB
* Invoice Parsing: pypdf for PDFs, python-docx for DOCX policy files
* Project Structure:
    ```bash
    .
    ├── main.py                 # Handles invoice analysis and storage
    ├── invoice.py              # Utilities for reading invoices, policy, generating prompts and extracting dates
    ├── dbstore.py              # Stores invoices into vector DB
    ├── ragbot.py               # Chatbot logic using RAG + LLM
    ├── testing_vector_database.py  # Utility to test vector search results
    ├── chroma_db/              # Local persistent vector DB files
    └── Dataset/                # Example invoice and policy files (excluded from Git)

## Prompt Design

For invoice evaluation, the prompt clearly gives the model:
* The company policy as reference
* The full extracted invoice text
* A request for a structured JSON response with status and reason

For the chatbot:
* The top 5 most relevant invoices are retrieved using vector search
* The context is injected into a system prompt
* Then the user's question is appended to get a final response
