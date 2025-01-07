# Data processing Service
This microservice processes JSON files containing Arabic text, cleans and normalizes the text, and splits it into manageable chunks for further use. It supports both fixed-size and semantic chunking methods and leverages the Camel Tools library for Arabic text cleaning and tokenization.

## Features
- Arabic Text Cleaning:
Removes Tatweel/Kashida.
Normalizes Unicode and Arabic-specific characters (Alef, Alef Maksura, Teh Marbuta, etc.).
Removes diacritics.
- Tokenization:
Tokenizes Arabic text into words using the Camel Tools tokenizer.
- Chunking Options:
Fixed-size Chunking: Splits text into fixed-size chunks with optional overlap.
Semantic Chunking: Splits text based on semantic boundaries like paragraphs.

## Installation

1. Clone the repository and navigate to the directory containing this microservice.
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
```
2. Then
```bash
cd advanced-arabic-rag/data_processing_service
```
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Service
- Processing All JSON Files
1- Place JSON files containing extracted Arabic text in the data_extraction_output folder.
2- Run the script:
```bash
python app.py
```
3- Processed files will be saved in the processed_chunks folder with _chunks.json appended to the filenames.

## Configuration
- Chunk Size: Set CHUNK_SIZE to define the size of fixed chunks (default: 512 tokens).
- Overlap: Set CHUNK_OVERLAP for the overlap size between chunks (default: 50 tokens).
- Semantic Chunking: Enable by setting USE_SEMANTIC_CHUNKING = True.
## File Structure
- Input Folder (data_extraction_output): Place input JSON files here.
- Output Folder (processed_chunks): Processed chunked JSON files will be stored here.
## Example Input and Output

- Input JSON Example:
```bash
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "example.pdf",
  "text": "النص العربي الذي يحتاج إلى تنظيف وتقسيم..."
}
```

- Output JSON Example:
```bash
[
  {
    "id": "chunk-uuid-1",
    "text": "النص العربي الأول...",
    "metadata": {
      "filename": "example.pdf",
      "original_doc_id": "123e4567-e89b-12d3-a456-426614174000",
      "chunk_index": 0
    }
  },
  {
    "id": "chunk-uuid-2",
    "text": "النص العربي الثاني...",
    "metadata": {
      "filename": "example.pdf",
      "original_doc_id": "123e4567-e89b-12d3-a456-426614174000",
      "chunk_index": 1
    }
  }
]
```
## Notes
- Ensure all input JSON files follow the required structure with a text field.
- Camel Tools must be installed for text normalization and tokenization.