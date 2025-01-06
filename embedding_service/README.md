# Embedding Service

Generates vector embeddings for Arabic text chunks and stores them in a Qdrant vector DB.

## Features
- Uses [CAMeL-Lab/bert-base-arabic-camelbert-msa](https://huggingface.co/CAMeL-Lab/bert-base-arabic-camelbert-msa) by default.
- Mean pooling to produce a single 768-d vector per chunk.
- Batch upsert to Qdrant with metadata.

## Setup & Requirements
1. **Install Qdrant** (on-prem or Docker).  
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
