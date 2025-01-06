
---

# `02_DATA_PROCESSING_SERVICE.md`

```markdown
# 02 Data Processing Service

This service:
1. Reads JSON files produced by `01_Data_Extraction_Service`.
2. Cleans and normalizes Arabic text.
3. Splits text into chunks (semantic or fixed-length).
4. Outputs ready-to-embed text segments in JSON.

## Directory Structure
data_processing_service/ ├── requirements.txt ├── app.py └── README.md


## Requirements

- `camel-tools` or `farasa` for tokenization and normalization
- `nltk`, `regex` for additional cleaning
- Possibly `unidecode` if needed

## Example `app.py`

```python
import os
import json
import re
from camel_tools.tokenizers.word import simple_word_tokenize

INPUT_FOLDER = "/output_json/mulitple-jsons"
OUTPUT_FOLDER = "/path/to/processed_chunks"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def clean_arabic_text(text):
    # Example: remove tatweel, excessive spaces, etc.
    text = re.sub(r"ـ+", "", text)  # remove tatweel
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(tokens, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        start += (chunk_size - overlap)
    return chunks

def process_json_files():
    for file_name in os.listdir(INPUT_FOLDER):
        if not file_name.endswith(".json"):
            continue

        input_path = os.path.join(INPUT_FOLDER, file_name)
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_text = data.get("text", "")
        cleaned_text = clean_arabic_text(raw_text)
        tokens = simple_word_tokenize(cleaned_text)
        text_chunks = chunk_text(tokens)

        processed_records = []
        for i, chunk in enumerate(text_chunks):
            record_id = f"{data['id']}_chunk_{i}"
            record = {
                "id": record_id,
                "text": chunk,
                "metadata": {
                    "filename": data["filename"],
                    "original_doc_id": data["id"],
                    "chunk_index": i
                }
            }
            processed_records.append(record)

        out_file = os.path.join(OUTPUT_FOLDER, file_name.replace(".json", "_chunks.json"))
        with open(out_file, "w", encoding="utf-8") as f_out:
            json.dump(processed_records, f_out, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_json_files()

Enhancements
Semantic Chunking: Split by headings or paragraphs using regex or ML-based segmenters.
Normalization Toggles: Some tasks require diacritics for disambiguation. Provide config options.