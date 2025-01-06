import os
import json
from typing import List, Dict, Any

import torch
from transformers import (
    AutoTokenizer,
    AutoModel,
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from opensearchpy import OpenSearch


# ------------- CONFIG ----------------
# Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "arabic_docs"

# OpenSearch
OS_HOST = "localhost"
OS_PORT = 9200
OS_INDEX = "arabic_docs_sparse"

# Model for embedding the query (matching the one used in your embedding_service)
EMBED_MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-msa"
# Model for cross-encoder re-ranking (here we just use an English cross-encoder as example)
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
# For Arabic re-ranking, replace with a suitable cross-encoder if available.

TOP_K = 10  # how many results to fetch from each system before combining
FINAL_TOP_N = 5  # how many final results we want after re-ranking


# ------------- INIT CLIENTS ----------------

# Qdrant client
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# OpenSearch client
# os_client = OpenSearch(
#     hosts=[{"host": OS_HOST, "port": OS_PORT}],
#     http_compress=True
# )

# Load query embedding model (same approach as your Embedding Service)
embed_tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME)
embed_model = AutoModel.from_pretrained(EMBED_MODEL_NAME)
embed_model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
embed_model.to(device)

# Load cross-encoder re-ranker model
ranker_tokenizer = AutoTokenizer.from_pretrained(RERANK_MODEL_NAME)
ranker_model = AutoModelForSequenceClassification.from_pretrained(RERANK_MODEL_NAME)
ranker_model.eval()
ranker_model.to(device)


# ------------- HELPER FUNCTIONS ----------------
def embed_query(text: str) -> List[float]:
    """
    Embeds the query text using the same approach as your embedding service (mean pooling).
    Returns a list of floats (vector).
    """
    inputs = embed_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = embed_model(**inputs)  # last_hidden_state shape: [1, seq_len, hidden_size]
    # Mean pool
    hidden_states = outputs.last_hidden_state.squeeze(0)  # [seq_len, hidden_size]
    mean_vec = hidden_states.mean(dim=0)  # [hidden_size]
    return mean_vec.cpu().tolist()


def dense_search(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Searches Qdrant for semantic matches.
    Returns a list of dicts: { "text": ..., "score": ..., "metadata": ... }
    """
    query_vector = embed_query(query)
    # Use "search" method from Qdrant
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False  # we don't need the vectors in the response
    )

    # search_result is a list of ScoredPoint
    results = []
    for point in search_result:
        payload = point.payload or {}
        print(payload)
        text_val = payload.get("text", None)  # If you stored text in the payload, or store it differently
        score = point.score
        results.append({
            "text": text_val,
            "score": score,       # Qdrant's similarity score
            "metadata": payload
        })
    return results


def sparse_search(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Searches OpenSearch for keyword matches (multi_match on "text" + "metadata.*").
    Returns a list of dicts: { "text": ..., "score": ..., "metadata": ... }
    """
    search_body = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["text", "metadata.*"]
            }
        }
    }

    resp = os_client.search(index=OS_INDEX, body=search_body)
    hits = resp["hits"]["hits"]

    results = []
    for hit in hits:
        source = hit["_source"]
        results.append({
            "text": source.get("text", ""),
            "score": hit["_score"],
            "metadata": source.get("metadata", {})
        })
    return results


def re_rank(query: str, candidates: List[Dict[str, Any]], top_n: int = FINAL_TOP_N) -> List[Dict[str, Any]]:
    """
    Re-rank candidates using a cross-encoder. 
    Each candidate is a dict with "text" and possibly "score" from prior steps.
    We'll produce a new 'rerank_score' and sort by it.
    Returns the top_n highest scoring docs.
    """
    if not candidates:
        return []

    # Prepare batch inputs for the cross-encoder
    # The cross-encoder needs pairs: (query, doc_text)
    pairs = [(query, c["text"] if c["text"] else "") for c in candidates]
    
    # Tokenize in batch
    batch = ranker_tokenizer.batch_encode_plus(
        pairs,
        truncation=True,
        max_length=512,
        return_tensors="pt",
        padding=True
    )
    batch = {k: v.to(device) for k, v in batch.items()}

    with torch.no_grad():
        outputs = ranker_model(**batch)
        # For a typical cross-encoder for ranking, the logits shape is [batch_size, 1].
        # We take the first (or only) dimension as the score.
        scores = outputs.logits.squeeze(-1)  # shape: [batch_size]

    # Move back to CPU
    scores = scores.cpu().tolist()  # a list of floats

    # Attach new re-rank score
    for i, score in enumerate(scores):
        candidates[i]["rerank_score"] = score

    # Sort candidates by descending rerank_score
    candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    # Return top_n
    return candidates[:top_n]


def hybrid_search(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Combines dense + sparse retrieval, then re-ranks with cross-encoder.
    Returns final top_n hits.
    """
    dense_results = dense_search(query, top_k)
    sparse_results = sparse_search(query, top_k)

    # Combine them (we could do a union or just a list)
    combined = dense_results + sparse_results

    # Optionally deduplicate if the same text appears in both results 
    # (we can deduplicate by doc ID or text).
    # For demo, we'll skip that step.

    # Re-rank them with cross-encoder
    final_ranked = re_rank(query, combined, top_n=FINAL_TOP_N)
    return final_ranked


# ------------- MAIN ----------------
if __name__ == "__main__":
    test_query = "بماذا يتميز برنامج السنه التحضيريه بجامعه الملك فهد للبترول والمعادن ؟"

    # Run hybrid search
    hits = dense_search(test_query)
    for i, hit in enumerate(hits, start=1):
        print(f"Rank: {i}")
        print(f"Text: {hit['text']}")
        print(f"Sparse/Dense Score: {hit.get('score', None)}")
        print(f"Re-rank Score: {hit.get('rerank_score', None)}")
        print(f"Metadata: {hit['metadata']}")
        print("-" * 40)
