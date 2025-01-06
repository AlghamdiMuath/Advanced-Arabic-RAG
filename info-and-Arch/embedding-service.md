# 03 Embedding Service

This service:
1. Reads processed chunks from `02_Data_Processing_Service`.
2. Generates dense vector embeddings (Arabic/multilingual).
3. Stores embeddings + metadata in a vector database (Qdrant, Weaviate, or Milvus).

## Directory Structure

embedding_service/ ├── requirements.txt ├── app.py └── README.md


## Requirements

- `torch`, `transformers`
- `qdrant-client` (or `weaviate-client`, `pymilvus`, etc.)
- `sentence-transformers` (if using those for quick embedding approaches)

## Example `app.py`

```python
import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-msa"
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
MODEL = AutoModel.from_pretrained(MODEL_NAME)

# Qdrant client (local or Docker-based)
qdrant_client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "arabic_docs"

def embed_text(text):
    inputs = TOKENIZER(text, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        outputs = MODEL(**inputs)
    # Mean pooling approach
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    return embeddings.tolist()

def init_collection():
    try:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    except:
        pass  # Collection might already exist

def index_chunks(chunks_folder):
    for file_name in os.listdir(chunks_folder):
        if not file_name.endswith("_chunks.json"):
            continue
        with open(os.path.join(chunks_folder, file_name), "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            vector = embed_text(record["text"])
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": record["id"],
                    "vector": vector,
                    "payload": record["metadata"]
                }]
            )

if __name__ == "__main__":
    init_collection()
    CHUNKS_FOLDER = "/path/to/processed_chunks"
    index_chunks(CHUNKS_FOLDER)


Enhancements
Fine-Tuning: Create a domain-specific embedding model by fine-tuning on university Q&A data.
Batching: Batch tokenization for speed.
GPU Acceleration: For large volumes, use CUDA if available.