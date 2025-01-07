import os
import uuid
import json
import fitz           # PyMuPDF
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from multiprocessing import Pool, cpu_count
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tqdm import tqdm
from typing import List, Optional

# ---------------------- CONFIG & GLOBALS ----------------------
DATA_FOLDER = "./data"   # Where PDFs are stored locally
OUTPUT_FOLDER = "./data_extraction_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# e.g. `tesseract-ocr-ara` package for Arabic
PYTESSERACT_CONFIG = r'--psm 6 -l ara'  # page segmentation + Arabic language

app = FastAPI(title="Data Extraction Service", version="1.0")


# ---------------------- UTILS & OCR FUNCTIONS ----------------------
def is_text_pdf(pdf_path: str) -> bool:
    """
    Use PyMuPDF to check if the PDF has any text.
    If we find text, we consider it a 'text-based' PDF; otherwise, it's scanned.
    """
    text_found = False
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text().strip()
                if text:
                    text_found = True
                    break
    except Exception as e:
        print(f"[WARN] Could not open PDF {pdf_path}: {e}")
    return text_found

def extract_text_pdf(pdf_path: str) -> str:
    """
    Extract text from text-based PDF using PyMuPDF.
    Returns a concatenation of text from all pages.
    """
    extracted = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            extracted.append(page.get_text())
    return "\n".join(extracted)

def ocr_scanned_pdf(pdf_path: str) -> str:
    """
    For a scanned PDF, convert each page to an image, then OCR with pytesseract.
    Returns combined text from all pages.
    """
    try:
        pages = convert_from_path(pdf_path)
    except Exception as e:
        print(f"[ERROR] pdf2image failed on {pdf_path}: {e}")
        return ""

    text_blocks = []
    for page_image in pages:
        # Convert PIL image to OpenCV (numpy array)
        open_cv_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
        # OCR with Tesseract
        page_text = pytesseract.image_to_string(open_cv_image, config=PYTESSERACT_CONFIG)
        text_blocks.append(page_text.strip())

    return "\n".join(text_blocks)


# ---------------------- MAIN EXTRACTION LOGIC ----------------------
def process_pdf_file(pdf_path: str) -> dict:
    """
    Main function that:
    1) Checks if PDF is text-based or scanned
    2) Extracts text
    3) Returns a final dict with all the data
    """
    file_name = os.path.basename(pdf_path)
    if not file_name.lower().endswith(".pdf"):
        return {}

    pdf_id = str(uuid.uuid4())
    text_based = is_text_pdf(pdf_path)
    
    if text_based:
        extracted_text = extract_text_pdf(pdf_path)
        extraction_method = "text_pdf"
    else:
        extracted_text = ocr_scanned_pdf(pdf_path)
        extraction_method = "scanned_pdf"
    output_data = {
        "id": pdf_id,
        "filename": file_name,
        "text": extracted_text,
        "metadata": {
            "source_type": "pdf",
            "extraction_method": extraction_method,
        }
        }

    return output_data


def process_and_save_pdf(pdf_path: str) -> str:
    """
    Orchestrates the PDF processing and saves output JSON to disk.
    Returns the path to the JSON file.
    """
    data = process_pdf_file(pdf_path)
    if not data:
        return ""

    out_file_name = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
    out_file_path = os.path.join(OUTPUT_FOLDER, out_file_name)

    with open(out_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return out_file_path


def process_all_pdfs_in_folder(folder_path: str) -> List[str]:
    """
    Parallelize processing of all PDFs in the folder
    using multiprocessing.Pool.
    Returns a list of JSON files generated.
    """
    pdf_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]
    if not pdf_files:
        print("[INFO] No PDF files found in folder.")
        return []

    # Use multiple CPU cores
    num_workers = max(1, cpu_count() - 1)
    print(f"[INFO] Found {len(pdf_files)} PDF files. Using {num_workers} workers...")

    results = []
    with Pool(processes=num_workers) as pool:
        # tqdm for a progress bar, chunksize=1 for demonstration
        for res in tqdm(pool.imap(process_and_save_pdf, pdf_files), total=len(pdf_files)):
            results.append(res)

    return results


# ---------------------- FASTAPI DATA MODELS ----------------------
class ExtractionResponse(BaseModel):
    filename: str
    text: str
    metadata: dict
    tables: Optional[List[dict]] = None

#“file upload” and “folder processing” in a single endpoint for demonstration.
#you might separate them.

# ---------------------- FASTAPI ROUTES ----------------------
@app.get("/health")
def health_check():
    """A simple health check."""
    return {"status": "ok", "message": "Data Extraction Service is running"}

@app.post("/extract", response_model=List[ExtractionResponse])
async def extract_endpoint(
    file: Optional[UploadFile] = File(None),
    process_folder: bool = False
):
    """
    Endpoint to extract text (and optional table data).
    - If `file` is provided, we process that single PDF.
    - If `process_folder` is True, we process all PDFs in `DATA_FOLDER`.
    Returns a list of extraction results.
    """
    results = []

    if file:
        # Single file scenario
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF.")

        # Save uploaded file to a temp path
        temp_pdf_path = os.path.join(DATA_FOLDER, f"upload_{uuid.uuid4()}.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(await file.read())

        # Process
        out_json_path = process_and_save_pdf(temp_pdf_path)
        if not out_json_path:
            raise HTTPException(status_code=500, detail="Extraction failed.")

        # Read JSON back to return it
        with open(out_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clean up
        os.remove(temp_pdf_path)

        # Return as a list
        results.append(data)
    elif process_folder:
        # Process entire folder
        json_files = process_all_pdfs_in_folder(DATA_FOLDER)
        # Load each JSON and append to results
        for jf in json_files:
            if not jf:
                continue
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                results.append(data)
    else:
        # No file and no folder flag -> error
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded or process_folder not specified."
        )

    # Convert raw dict to Pydantic models for a consistent response
    pydantic_results = []
    for r in results:
        pydantic_results.append(ExtractionResponse(
            filename=r["filename"],
            text=r["text"],
            metadata=r["metadata"],
            tables=r.get("tables", [])
        ))

    return pydantic_results


# ---------------------- ENTRY POINT ----------------------
if __name__ == "__main__":
#     """
#     If you want to run this as a script (without FastAPI),
#     you can call process_all_pdfs_in_folder(DATA_FOLDER).
#     Otherwise, typically you run with uvicorn:
#       uvicorn app:app --host 0.0.0.0 --port 8000
#     """
#     # Example CLI usage (no server):
    process_all_pdfs_in_folder(DATA_FOLDER)
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
