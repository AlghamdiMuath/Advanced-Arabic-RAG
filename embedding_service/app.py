import os
import json
import torch
from typing import List
from transformers import AutoTokenizer, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct
)
from tqdm import tqdm

# ------------------ CONFIG ------------------
# Model and Tokenizer
MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-msa"
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
MODEL = AutoModel.from_pretrained(MODEL_NAME)

# If you have a GPU, you can uncomment this:
device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL.to(device)

# Qdrant Client config
QDRANT_HOST = "localhost"    # or IP
QDRANT_PORT = 6333
COLLECTION_NAME = "arabic_docs"

# Path to the folder containing "_chunks.json" files
CHUNKS_FOLDER = "./processed_chunks"

# Vector size for the chosen model
# For CAMeL BERT base: hidden size = 768
VECTOR_SIZE = 768

# Initialize Qdrant client (assumes Qdrant is up & running)
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


# ------------------ EMBEDDING FUNCTION ------------------
def embed_text(text: str) -> List[float]:
    """
    Embeds the text using the loaded Transformer model.
    Returns a 768-dimensional list of floats (for BERT base).
    Uses a simple "mean pooling" across the last hidden states.
    """
    inputs = TOKENIZER(
        text,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )
    # If using GPU:
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = MODEL(**inputs)
    
    # outputs.last_hidden_state: [batch_size, seq_len, hidden_dim]
    # We'll do a simple mean of the seq_len dimension
    hidden_states = outputs.last_hidden_state.squeeze(0)  # shape: [seq_len, 768]
    embedding_vector = hidden_states.mean(dim=0)          # shape: [768]
    
    # Optionally move to CPU if using GPU
    # embedding_vector = embedding_vector.cpu()

    return embedding_vector.tolist()


# ------------------ QDRANT COLLECTION INIT ------------------
def init_collection():
    """
    Creates a Qdrant collection (if it doesn't exist) with
    a vector dimension of 768 and cosine similarity distance.
    """
    try:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"[INFO] Created collection '{COLLECTION_NAME}'.")
    except Exception as e:
        # If the collection already exists, skip or handle exception
        print(f"[INFO] Collection '{COLLECTION_NAME}' might already exist: {e}")


# ------------------ INDEXING CHUNKS ------------------
def index_chunks(chunks_folder: str):
    """
    Reads all *_chunks.json files in the chunks_folder, embeds their text,
    and upserts them into Qdrant.
    Each record is stored as:
      - id: record["id"]
      - vector: embedding
      - payload: record["metadata"]
    """
    # Gather all files that end with "_chunks.json"
    all_chunk_files = [
        f for f in os.listdir(chunks_folder)
        if f.lower().endswith("_chunks.json")
    ]
    if not all_chunk_files:
        print(f"[INFO] No chunk files found in {chunks_folder}.")
        return

    print(f"[INFO] Found {len(all_chunk_files)} chunk files to index.")

    for file_name in tqdm(all_chunk_files, desc="Indexing chunk files"):
        file_path = os.path.join(chunks_folder, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        # Optionally, you can embed in batch for efficiency.
        # We'll do a simple loop for clarity.
        # If you do batch embedding, you should tokenize multiple texts at once 
        # and pass them to MODEL for faster inference on GPU.

        points_to_upsert = []
        for record in records:
            text = record["text"]
            record_id = record["id"]
            # metadata = record.get("metadata", {})

            # Embed text
            vector = embed_text(text)

            # Create a Qdrant PointStruct
            point = PointStruct(
                id=record_id,
                vector=vector,
                # Merge the chunk text with metadata so Qdrant stores it all
                payload={
                    "text": text,         # <-- Add the text here
                    **record["metadata"]            # Spread the metadata keys
                }
            )
            points_to_upsert.append(point)

        # Batch upsert the entire list of points
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points_to_upsert
        )


# ------------------ MAIN ------------------
if __name__ == "__main__":
    """
    Usage:
      1) Start Qdrant (on localhost:6333 or your chosen host/port).
      2) Ensure you have chunked JSON files from the Data Processing Service 
         in CHUNKS_FOLDER (each file ending with _chunks.json).
      3) python app.py
    """
    # Step 1: Initialize Qdrant collection
    init_collection()

    # Step 2: Index chunk files
    index_chunks(CHUNKS_FOLDER)

    print("[INFO] Embedding & indexing complete.")
