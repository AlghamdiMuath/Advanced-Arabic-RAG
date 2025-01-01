import pytesseract
from pytesseract import Output
import easyocr
from pdf2image import convert_from_path
import json
import numpy as np
from PIL import Image

def preprocess_pdf(pdf_path):
    # Convert PDF to images (PIL Image objects)
    images = convert_from_path(pdf_path)
    return images

def apply_ocr(image, use_easyocr=False):
    if use_easyocr:
        # Ensure the image is in a format that easyocr can process (NumPy array or path)
        image_np = np.array(image)  # Convert PIL Image to NumPy array
        reader = easyocr.Reader(['ar'])  # Arabic language
        result = reader.readtext(image_np)
        text = ' '.join([res[1] for res in result])
    else:
        text = pytesseract.image_to_string(image, lang='ara')
    return text

def extract_layout_metadata(image, use_easyocr=False):
    if use_easyocr:
        # EasyOCR doesn't have a direct equivalent to image_to_data, so handle it differently if needed
        return {'message': 'EasyOCR doesn\'t provide detailed layout metadata directly'}
    else:
        # Extract layout metadata using pytesseract
        data = pytesseract.image_to_data(image, output_type=Output.DICT)
        return data

def extract_content_from_pdf(pdf_path, use_easyocr=False):
    images = preprocess_pdf(pdf_path)
    extracted_data = []
    for image in images:
        # Apply OCR to the image
        text = apply_ocr(image, use_easyocr)
        # Extract layout metadata (if not using EasyOCR)
        layout_metadata = extract_layout_metadata(image, use_easyocr)
        extracted_data.append({
            'text': text,
            'layout_metadata': layout_metadata
        })
    return extracted_data

def save_extracted_data(extracted_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

# usage
pdf_path = './AcademicRegulationsArabic_page1.pdf'
output_path = 'extracted_data.json'
extracted_data = extract_content_from_pdf(pdf_path, use_easyocr= [False, True][0]) 
save_extracted_data(extracted_data, output_path)


#first ten letters of the output in the text element of the json
# print(json.load(open('extracted_data.json', 'r', encoding='utf-8'))[0]['text'][:10])