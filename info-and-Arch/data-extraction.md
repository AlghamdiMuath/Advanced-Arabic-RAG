# 01 Data Extraction Service

This service ingests Arabic PDFs (including scanned) and outputs structured JSON files containing:
- Extracted text (page by page, or entire doc).
- Basic metadata (filename, pages, time of extraction).
- Optional: Bounding box/visual layout data for tables and images.

## 1. Directory Structure

data_extraction_service/ ├── requirements.txt ├── app.py ├── Dockerfile └── README.md

## 2. Requirements

- **Python Libraries**:
  - `paddleocr` or `pytesseract`
  - `opencv-python` (if needed for image pre-processing)
  - `pdfminer.six` or `pymupdf` (for non-scanned PDF text extraction)
  - `tqdm` (for progress bars)
  - `requests` or `httpx` (if hooking into a cloud service, optional)

requirements.txt (example)
paddleocr==2.6.0 pdfminer.six==20221105 opencv-python==4.7.0.68 tqdm==4.64.1

## 3. Example `app.py`

```python
import os
import json
import uuid
from paddleocr import PaddleOCR
from pdfminer.high_level import extract_text
from tqdm import tqdm

ocr = PaddleOCR(lang='ar', use_gpu=False)  # or True if GPU available

INPUT_FOLDER = "/path/to/input_pdfs"
OUTPUT_FOLDER = "/path/to/output_json"

def extract_text_from_pdf(pdf_path):
    """Extract text from native PDF (non-scanned) using pdfminer."""
    return extract_text(pdf_path)

def extract_text_from_scanned(pdf_path):
    """Use OCR on scanned PDF pages (simple approach)."""
    # Convert PDF to images (e.g., using pdf2image or OpenCV) then pass to OCR
    # We'll do a stub here:
    text_content = []
    # for page_image in pdf_images:
    #     result = ocr.ocr(page_image, cls=True)
    #     # parse result into text
    #     text_content.append(parsed_text)
    return "\n".join(text_content)

def process_pdfs():
    for file_name in tqdm(os.listdir(INPUT_FOLDER)):
        if not file_name.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(INPUT_FOLDER, file_name)
        # Quick detection: try reading text. If text is empty, assume scanned.
        native_text = extract_text_from_pdf(pdf_path)
        if len(native_text.strip()) > 0:
            extracted_text = native_text
        else:
            extracted_text = extract_text_from_scanned(pdf_path)

        output_data = {
            "id": str(uuid.uuid4()),
            "filename": file_name,
            "text": extracted_text,
            "metadata": {
                "source_type": "pdf",
                "extraction_method": "OCR" if len(native_text.strip()) == 0 else "pdfminer",
            }
        }

        out_file = os.path.join(OUTPUT_FOLDER, file_name.replace(".pdf", ".json"))
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_pdfs()

. Enhancements
Parallelization: Use multiprocessing or a task queue (e.g., RabbitMQ) to handle many PDFs.
Table/Visual Extraction: Integrate LayoutLMv3 or DocTR for bounding boxes and table structures.
Error Handling: Gracefully handle corrupt PDFs or missing fonts.