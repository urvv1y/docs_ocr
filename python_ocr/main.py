# ********************************
#  feature: OCR and Data Extraction from Images - receipts
# ********************************

# imports needed for the project
import re
import pytesseract
from fastapi import FastAPI, File, UploadFile
from PIL import Image

# FastApi init
app = FastAPI()

# setting the path for tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# constants
SEARCH_PATTERNS_CZECH = {
    "Provozovatel": r"Provozovatel:\s*(.+)",
    "Datum": r"Datum:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{2}\s+[0-9]{2}:[0-9]{2})",
    "Platba": r"platby:\s*(.+)",
    "Celkem": r"Cel.*?kem:\s*([0-9]+[\.,][0-9]{2})"
}

SEARCH_PATTERNS_ENGLISH = {
    "Merchant": r"(?:Merchant|Vendor|Store):\s*(.+)",
    "Date": r"Date:\s*([0-9]{1,4}[-/\.][0-9]{1,2}[-/\.][0-9]{1,4}\s*(?:[0-9]{1,2}:[0-9]{2}(?:\s*[AaPp][Mm])?)?)",
    "Payment": r"(?:Payment|Method|Tender|Paid by):\s*(.+)",
    "Total": r"Total.*?:\s*(?:[$£€]\s*|USD\s*|EUR\s*)?([0-9]+[\.,][0-9]{2})"
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
    return result

# ***
# FastAPI
# ***
@app.post("/extract")
async def process(file: UploadFile = File(...), lang: str="ces"):
    read_file = await file.read()
    return {"status": "success",
            "data": result}







