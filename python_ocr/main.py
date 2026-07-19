# ********************************
#  feature: OCR and Data Extraction from Images
# ********************************

# imports needed for the project
import re
import os
from unittest import result
import pytesseract
from fastapi import FastAPI, File, UploadFile
from PIL import Image

# FastApi init
app = FastAPI()

# setting the path for tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# constants
SEARCH_PATTERNS_CZECH = {
    # receipt
    "Provozovatel": r"Provozovatel:\s*(.+)",
    "Datum": r"Datum:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{2}\s+[0-9]{2}:[0-9]{2})",
    "Platba": r"platby:\s*(.+)",
    "Celkem": r"Cel.*?kem:\s*([0-9]+[\.,][0-9]{2})",

    # invoice
    "Cislo_faktury": r"(?i)(?:Číslo faktury|Faktura č\.|Variabilní symbol):\s*([0-9A-Za-z]+)",
    "Datum_splatnosti": r"(?i)(?:Splatnost|Datum splatnosti):\s*([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4})",
    "Odberatel": r"(?i)Odběratel:\s*(.+)",
    "Banka": r"(?i)(?:Číslo účtu|Účet|IBAN):\s*([A-Za-z0-9/-]+)",
    "Popis": r"(?i)(?:Popis|Předmět|Účel):\s*(.+)"
}

SEARCH_PATTERNS_ENGLISH = {
    # receipt
    "Merchant": r"(?:Merchant|Vendor|Store):\s*(.+)",
    "Date": r"Date:\s*([0-9]{1,4}[-/\.][0-9]{1,2}[-/\.][0-9]{1,4}\s*(?:[0-9]{1,2}:[0-9]{2}(?:\s*[AaPp][Mm])?)?)",
    "Payment": r"(?:Payment|Method|Tender|Paid by):\s*(.+)",
    "Total": r"Total.*?:\s*(?:[$£€]\s*|USD\s*|EUR\s*)?([0-9]+[\.,][0-9]{2})",

    # invoice
    "Invoice_Number": r"(?i)Invoice No[.:]\s*([0-9A-Za-z]+)",
    "Due_Date": r"(?i)Due Date:\s*([0-9]{1,4}[-/\.][0-9]{1,2}[-/\.][0-9]{1,4})",
    "Customer": r"(?i)(?:Customer|Bill To):\s*(.+)",
    "Bank": r"(?i)(?:Bank Account|IBAN|Account No):\s*([A-Za-z0-9/-]+)",
    "Description": r"(?i)(?:Description|Subject|Item):\s*(.+)"
}


""" Function to load and extract text from an image """
def load_image(img_path: str, lang: str) -> str:
    opened_image = Image.open(img_path).convert("L")
    image_text = pytesseract.image_to_string(opened_image, lang=lang)
    return image_text


""" Function to extract data from the document based on the specified language """
def extract_data(img_path: str,lang: str) -> dict[str, str | None]:
    if lang == "ces":
        doc_text = load_image(img_path, "ces")
        search_patterns = SEARCH_PATTERNS_CZECH
    else:
        doc_text = load_image(img_path, "eng")
        search_patterns = SEARCH_PATTERNS_ENGLISH

    result: dict[str, str | None] = {}

    for key, pattern in search_patterns.items():
        match = re.search(pattern, doc_text)

        if match:
            result[key] = match.group(1).strip()
        else:
            result[key] = None
        
        if lang == "ces":
            result["Zbozi"] = {}
        else:
            result["Goods"] = {}
    return result

# ***
# FastAPI
# ***
@app.post("/extract")
async def process(file: UploadFile = File(...), lang: str="ces"):
    read_file = await file.read()

    with open(file.filename, "wb") as f:
        f.write(read_file)

    extracted_data = extract_data(file.filename, lang)

    if os.path.exists(file.filename):
        os.remove(file.filename)

    return {"status": "success",
            "data": extracted_data}

# run FastApi server: uvicorn main:app --reload






