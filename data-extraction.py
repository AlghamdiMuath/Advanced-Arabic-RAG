import pytesseract
from pytesseract import Output
import easyocr
from pdf2image import convert_from_path
import json
import numpy as np
import os
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
        return {'message': 'Tesseract doesn\'t provide accurate layout metadata'}
        # data = pytesseract.image_to_data(image, output_type=Output.DICT)
        # return data

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

def process_folder(folder_path, use_easyocr=False):
    all_extracted_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            extracted_data = extract_content_from_pdf(pdf_path, use_easyocr)
            for data in extracted_data:
                data['file_name'] = filename  # Add the file name to each chunk of data
            all_extracted_data.extend(extracted_data)
    return all_extracted_data

# Example usage:
folder_path = './data'  # Folder containing PDFs
output_path = 'extracted_data.json'  # Single JSON file for all extracted data
extracted_data = process_folder(folder_path, use_easyocr=False)
save_extracted_data(extracted_data, output_path)

# First ten characters of the output in the text element of the JSON
print(json.load(open('extracted_data.json', 'r', encoding='utf-8'))[0]['text'][:10])