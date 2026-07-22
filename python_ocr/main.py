# ********************************
#  feature: OCR and Data Extraction from Images
# ********************************

# imports needed for the project
import json
import os
import pytesseract
from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
from dotenv import load_dotenv
import cv2
import numpy as np
from pyzbar.pyzbar import decode

#
load_dotenv()
key = os.getenv("GROQ_API_KEY")
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)

# FastApi init
app = FastAPI()

# setting the path for tesseract executable NO NEED FOR DOCKER
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


""" Function to load and extract text from an image """
def load_image(img_path: str, lang: str) -> str:
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Image at path {img_path} could not be loaded.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    image_text = pytesseract.image_to_string(thresh, lang=lang, config='--psm 4')
    return image_text

def extract_qr_code(img_path: str) -> list:
    """Function to extract QR code data from an image"""
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Image at path {img_path} could not be loaded.")
    qr_codes = decode(img)
    qr_data_list = [qr.data.decode('utf-8') for qr in qr_codes]
    return qr_data_list


def ai_extract(doc_text: str, lang: str, doc_type: str) -> dict:
    """Function using AI to extract data from the document"""

    if doc_type == "invoice":
        if lang == "ces":
            json_structure = """{
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
                    }"""
            
            prompt = """
        You are a strict data extraction assistant. Extract data from the provided Czech OCR text into a valid JSON object.
        Do not make up any data. If a piece of information is missing, set its value to null.
        Format the "Celkem" value strictly as a number without currency symbols (e.g., "150.50").
        
        You must return EXACTLY this JSON structure {json_structure}, replacing the examples with actual extracted data:
        If no goods are found in the text, return an empty object for Zbozi like this: "Zbozi": {}."""

        else:
            json_structure = """{
            
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
            }"""
            prompt = """
        You are a strict data extraction assistant. Extract data from the provided English OCR text into a valid JSON object.
        Do not make up any data. If a piece of information is missing, set its value to null.
        Format the "Total" value strictly as a number without currency symbols (e.g., "150.50").
        
        You must return EXACTLY this JSON structure {json_structure}, replacing the examples with actual extracted data:
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
    else:
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
                "Celkem": "number or null"
            }
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
                "Total": "number or null"
            }
            """

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        response_format={"type": "json_object"},
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": doc_text}],
            temperature=0.1
    )
    response_content = response.choices[0].message.content
    extracted_json = json.loads(response_content)
    return extracted_json

# ***
# FastAPI
# ***
@app.post("/extract")
async def process(file: UploadFile = File(...), lang: str="ces", doc_type: str="invoice"):
    read_file = await file.read()
    file_path = file.filename
    with open(file.filename, "wb") as f:
        f.write(read_file)

    extracted_data = load_image(file_path, lang)
    ai_process_data = ai_extract(extracted_data, lang, doc_type)

    # uncomment IF you want to delete the uploaded file after processing
    #if os.path.exists(file_path):
    #    os.remove(file_path)

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

# UI
# http://localhost:8080 



