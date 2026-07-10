# imports needed for the project
from email.mime import image

import pytesseract
from PIL import Image

# setting the path for tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_image_czech(img):

    opened_image = Image.open(img).convert("L")
    image_text = pytesseract.image_to_string(opened_image, lang="ces")
    return image_text

def load_image_english(img):
    opened_image = Image.open(img).convert("L")
    image_text = pytesseract.image_to_string(opened_image, lang="eng")
    return image_text

print(load_image_czech("doc_test.jpg"))


