# ********************************
#  feature: OCR and Data Extraction from Images
# ********************************

# imports needed for the project
import json
import re
import os
from unittest import result
import pytesseract
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

#
load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(base_url="http://ollama:11434/v1", api_key="ollama")

# FastApi init
app = FastAPI()

# setting the path for tesseract executable NO NEED FOR DOCKER
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# constants
SEARCH_PATTERNS_CZECH = {
    # receipt + invoice (common)
    "Provozovatel": r"(?i)(?:Dodavatel|Provozovatel|Obchodník|Firma)[\s:]*([A-Za-z0-9\s\.\-,]+)",
    "Datum": r"(?i)(?:Datum|Vystaveno|Datum vystavení)[\s:]*([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4})",
    "Platba": r"(?i)(?:Platba|Forma úhrady|Způsob úhrady|Placeno|Úhrada)[\s:]*([^\n]+)",
    "Celkem": r"(?i)(?:Celkem|K úhradě|Suma)[\s\w]*?([0-9\s]+[\.,][0-9]{2})",

    # invoice only
   "Cislo_faktury": r"(?i)(?:Číslo faktury|Faktura č\.|Variabilní symbol|Doklad č\.)[\s:]*([0-9A-Za-z]+)",
    "Datum_splatnosti": r"(?i)(?:Splatnost|Datum splatnosti)[\s:]*([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{2,4})",
    "Odberatel": r"(?i)Odběratel[\s:]*(.+)",
    "Banka": r"(?i)(?:Číslo účtu|Účet|IBAN)[\s:]*([A-Za-z0-9\/\-]+)",
    "Popis": r"(?i)(?:Popis|Předmět|Účel|Fakturujeme vám)[\s:]*(.+)"
}

SEARCH_PATTERNS_ENGLISH = {
    # receipt + invoice (common)
   "Merchant": r"(?i)(?:Merchant|Vendor|Store|Supplier)[\s:]*([A-Za-z0-9\s\.\-,]+)",
    "Date": r"(?i)(?:Date|Invoice Date)[\s:]*([0-9]{1,4}[-/\.][0-9]{1,2}[-/\.][0-9]{1,4})",
    "Payment": r"(?i)(?:Payment|Method|Tender|Paid by)[\s:]*([^\n]+)",
    "Total": r"(?i)(?:Total|Amount Due|Balance)[\s\w]*?([0-9\s]+[\.,][0-9]{2})",

    # invoice
    "Invoice_Number": r"(?i)(?:Invoice No[.:]?|Reference)[\s:]*([0-9A-Za-z]+)",
    "Due_Date": r"(?i)Due Date[\s:]*([0-9]{1,4}[-/\.][0-9]{1,2}[-/\.][0-9]{1,4})",
    "Customer": r"(?i)(?:Customer|Bill To)[\s:]*(.+)",
    "Bank": r"(?i)(?:Bank Account|IBAN|Account No)[\s:]*([A-Za-z0-9\/\-]+)",
    "Description": r"(?i)(?:Description|Subject|Item)[\s:]*(.+)"
}

def amount_cleaner(amount: str) -> str:
    """ Function to clean and format the amount string """
    if not amount:
        return amount
    amount = amount.replace(" ", "").replace(",", ".")
    return amount


""" Function to load and extract text from an image """
def load_image(img_path: str, lang: str) -> str:
    opened_image = Image.open(img_path).convert("L")
    image_text = pytesseract.image_to_string(opened_image, lang=lang, config='--psm 4')
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
            val = match.group(1).strip()
            if key in ["Celkem", "Total"]:
                val = amount_cleaner(val)
            result[key] = val
        else:
            result[key] = None
        
        if lang == "ces":
            result["Zbozi"] = {}
        else:
            result["Goods"] = {}
    return result


def ai_extract(doc_text: str, lang: str) -> dict:
    """Function using AI to extract data from the document"""
    if lang == "ces":
        prompt = """
        You are a strict data extraction assistant. Extract data from the provided Czech OCR text into a valid JSON object.
        Do not make up any data. If a piece of information is missing, set its value to null.
        Format the "Celkem" value strictly as a number without currency symbols (e.g., "150.50").
        
        You must return EXACTLY this JSON structure, replacing the examples with actual extracted data:
        {
            "Provozovatel": "string or null",
            "Datum": "string or null",
            "Platba": "string or null",
            "Celkem": "number or null",
            "Cislo_faktury": "string or null",
            "Datum_splatnosti": "string or null",
            "Odberatel": "string or null",
            "Banka": "string or null",
            "Popis": "string or null",
            "Zbozi": {
                "Název prvního produktu": {
                    "Mnozstvi": "string or null",
                    "Cena": "string or null",
                    "DPH": "string or null"
                }
            }
        }
        If no goods are found in the text, return an empty object for Zbozi like this: "Zbozi": {}.
        """
    else:
        prompt = """
        You are a strict data extraction assistant. Extract data from the provided English OCR text into a valid JSON object.
        Do not make up any data. If a piece of information is missing, set its value to null.
        Format the "Total" value strictly as a number without currency symbols (e.g., "150.50").
        
        You must return EXACTLY this JSON structure, replacing the examples with actual extracted data:
        {
            "Merchant": "string or null",
            "Date": "string or null",
            "Payment": "string or null",
            "Total": "number or null",
            "Invoice_Number": "string or null",
            "Due_Date": "string or null",
            "Customer": "string or null",
            "Bank": "string or null",
            "Description": "string or null",
            "Goods": {
                "Name of the first item": {
                    "Quantity": "string or null",
                    "Price": "string or null"
                }
            }
        }
        If no goods are found in the text, return an empty object for Goods like this: "Goods": {}.
        """
    response = client.chat.completions.create(
        model = "qwen2.5:1.5b",
        response_format={"type": "json_object"},
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": doc_text}],
            temperature=0.1;
    )
    response_content = response.choices[0].message.content
    extracted_json = json.loads(response_content)
    return extracted_json

# ***
# FastAPI
# ***
@app.post("/extract")
async def process(file: UploadFile = File(...), lang: str="ces"):
    read_file = await file.read()
    file_path = file.filename
    with open(file.filename, "wb") as f:
        f.write(read_file)

    extracted_data = load_image(file_path, lang)
    ai_process_data = ai_extract(extracted_data, lang)
    return {"status": "success",
            "data": ai_process_data}

# run FastApi server: uvicorn main:app --reload

# -------
# FOR DOCKER
# docker-compose up -d --build
# - builds
# - run from the root of the project where docker-compose.yml is located
# docker ps
# - verify running containers
# docker-compose logs -f
# - logs of all containers
# docker-compose down
# - shutdown all containers
# docker-compose stop
# - stops all containers
# dockeer-compose up -d
# - without the build

# see pgadmin localhost:5432

# POST
# invoice http://localhost:8080/api/upload-invoice
# receipt http://localhost:8080/api/upload

# GET
# invoices http://localhost:8080/api/invoices
# receipts http://localhost:8080/api/receipts



