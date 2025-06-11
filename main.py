from fastapi import FastAPI, UploadFile, Form
import zipfile
import os
import uuid
import re
from invoice import get_policy, get_invoice, prompt, get_date
from dbstore import store
import json
from groq import Groq
import shutil

client = Groq(api_key="")

app = FastAPI()

@app.post("/analyze_invoices")
async def analyze_invoices(policy_file: UploadFile, invoices_zip: UploadFile, employee_name: str = Form(...)):
    policy_path = "temp_policy.docx" #Uploaded policy file stored temporarily since FastAPI makes it available only in memory
    with open(policy_path, "wb") as f:
        f.write(await policy_file.read())

    policy_text = get_policy(policy_path)

    zip_path = "temp_invoices.zip" #Similarly store uploaded invoice zip file stored temporarily
    with open(zip_path, "wb") as f:
        f.write(await invoices_zip.read())

    invoices_folder = "temp_invoices_folder"
    if os.path.exists(invoices_folder):
        shutil.rmtree(invoices_folder)
    os.makedirs(invoices_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref: #extracting pdfs in temporary folder
        zip_ref.extractall(invoices_folder)
    
    for root, dirs, files in os.walk(invoices_folder): #recursively goes through all files in folders and subfolders
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                pdf_text = get_invoice(pdf_path)

                invoice_prompt = prompt(policy_text, pdf_text) 

                response = client.chat.completions.create( #calls llama 4 scout model
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": "You are helping me analyze invoices."},
                        {"role": "user", "content": invoice_prompt}
                    ],
                    temperature=0 #we do this for deterministic behaviour
                )

                result_text = response.choices[0].message.content #this takes first response of the model out of multiple available

                json_match = re.search(r'\{.*\}', result_text, re.DOTALL) #looks for pattern of form '{...}'
                if json_match:
                    json_text = json_match.group(0)
                    try:
                        result_json = json.loads(json_text) #converts string to python dictionary
                        status = result_json.get("status", "Unknown").strip().title() #status extracted stripping extra spaces in title case
                        reason = result_json.get("reason", "No reason provided.").strip() #reason extracted stripping extra spaces

                        print(f"\nParsed response for {filename}:\nstatus - {status}\nreason - {reason}\n")

                    except Exception as e: #give error if trouble in parsing JSON
                        print(f"Error parsing extracted JSON for {filename}: {e}")
                        status = "Error"
                        reason = "Failed to parse extracted JSON."
                else: #error if not got JSON
                    print(f"Error: Could not find valid JSON in LLM response for {filename}.")
                    status = "Error"
                    reason = "Failed to parse LLM response."

                invoice_id = str(uuid.uuid4()) #create universal unique identifier
                date = get_date(pdf_text) #extract date from invoice text

                store(invoice_id, employee_name.strip(), date, pdf_text, status, reason) #embedding and metadata stored in vector DB

    return {"success": True, "message": "Invoices processed and stored."}