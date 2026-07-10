# imports needed for the project
import pytesseract
from PIL import Image

# setting the path for tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def load_image_czech(img):

    opened_image = Image.open(img)
    image = pytesseract.image_to_string(opened_image, lang="ces")
    return image

def load_image_english(img):
    opened_image = Image.open(img)
    image = pytesseract.image_to_string(opened_image, lang="eng")
    return image


