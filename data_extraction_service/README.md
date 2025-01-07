# Data Extraction Service

This microservice provides functionality to extract text from PDF documents, including both text-based and scanned PDFs, using OCR when necessary. The service is built with FastAPI and supports single PDF uploads as well as batch processing of multiple PDFs within a specified folder.

## Features
- Detects whether a PDF is text-based or scanned.
- Extracts text from text-based PDFs using PyMuPDF.
- Performs OCR on scanned PDFs using Tesseract.
- Supports batch processing of PDFs in a folder using multiprocessing.
- Provides REST API endpoints for file uploads and batch processing.

## Installation

1. Clone the repository and navigate to the directory containing this microservice.
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
```
2. Then
```bash
cd advanced-arabic-rag/data_extraction_service
```
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Service
Start the FastAPI server with:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
**Endpoint:** `/health`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "ok",
    "message": "Data Extraction Service is running"
  }
  ```

#### Extract Text from PDF(s)
**Endpoint:** `/extract`
- **Method:** `POST`
- **Parameters:**
  - `file`: Optional PDF file to process (single file scenario).
  - `process_folder`: Boolean flag to process all PDFs in the `./data` folder.
- **Response:** A list of extracted text and metadata:
  ```json
  [
    {
      "filename": "example.pdf",
      "text": "Extracted text content...",
      "metadata": {
        "source_type": "pdf",
        "extraction_method": "text_pdf"
      },
      "tables": null
    }
  ]
  ```

## Folder Structure
- **DATA_FOLDER (`./data`)**: Contains the PDF files to process.
- **OUTPUT_FOLDER (`./data_extraction_output`)**: Stores the extracted JSON outputs.

## Notes
- Ensure Tesseract OCR is installed and configured on your system.
- Update the `PYTESSERACT_CONFIG` in the code if you need to customize OCR settings.
- Logs and warnings will be printed to the console for debugging.

## Example CLI Usage(Run locally) 
To process all PDFs in the `./data` folder without using the API:
```bash
python app.py
```
