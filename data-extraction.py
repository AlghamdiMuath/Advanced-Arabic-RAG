import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
import json
import numpy as np
import os
from PIL import Image
from multiprocessing import Pool, cpu_count
import multiprocessing


def preprocess_pdf(pdf_path):
    """Convert PDF to images."""
    return convert_from_path(pdf_path)


def apply_ocr(image):
    return pytesseract.image_to_string(image, lang='ara')


def process_single_file(pdf_path):
    """Process a single PDF file."""
    images = preprocess_pdf(pdf_path)
    extracted_data = []
    for image in images:
        text = apply_ocr(image)
        extracted_data.append({'text': text, 'layout_metadata': {}})
    return extracted_data


def process_folder(folder_path):
    """Process all PDF files in a folder using multiprocessing."""
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    with Pool(cpu_count()) as pool:
        results = pool.map(process_single_file, pdf_files)

    all_extracted_data = []
    for pdf_path, data in zip(pdf_files, results):
        for item in data:
            item['file_name'] = os.path.basename(pdf_path)
        all_extracted_data.extend(data)

    return all_extracted_data


def save_extracted_data(extracted_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn') 

    folder_path = './data'  # Folder containing PDFs
    output_path = 'extracted_data.json'  # Output JSON file

    # Process PDFs and save results
    extracted_data = process_folder(folder_path)
    save_extracted_data(extracted_data, output_path)

    # Output a preview of the extracted text
    if extracted_data:
        print(extracted_data[0]['text'][:10])
