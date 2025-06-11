from docx import Document
import pypdf
import re

def get_policy(doc_path):
    '''This function takes path of the .docx file as argment and
    gets a list of paragraphs from provided document, then it takes 
    the text and joins them by new line to form a single string.'''
    text = "\n".join([p.text for p in Document(doc_path).paragraphs])
    return text

def get_invoice(pdf_path):
    '''Similar to get_policy function takes path of .pdf file as argument and 
    this function creates a 'reader' that reads texts from pdf and provides 
    a single long string.'''
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for pg in reader.pages:
        text += pg.extract_text()
    return text

def prompt(policy, pdf):
    '''prompt function takes policy of company and invoice text as argument 
    and creates a prompt for LLM requesting output in JSON format.'''
    prompt = f"""
    I want your help to check if this invoice can be reimbursed or not according to company rules and
    here is the company policy about reimbursements {policy} and here is the invoice content {pdf}.
    Can you please tell me if this invoice is "Fully Reimbursed", "Partially Reimbursed" or 
    "Declined". Also explain why you think so, based on the policy. Kindly reply in this JSON format:
    {{
        "status": "...",
        "reason": "..."
    }}
    """
    return prompt

def get_date(text):
    '''get_date function takes a invoice text as argument and 
    extracts date from it as raw string and returns it upon match.'''
    pattern1 = r'(\d{1,2} [A-Za-z]{3,9} \d{4})'

    pattern2 = r'([A-Za-z]{3,9} \d{1,2}, \d{4})'

    match1 = re.search(pattern1, text)
    if match1:
        return match1.group(0)

    match2 = re.search(pattern2, text)
    if match2:
        return match2.group(0)

    return "Unknown"