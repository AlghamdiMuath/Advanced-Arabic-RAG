# 04 Retrieval Service

Implements a hybrid approach:
1. Dense retrieval from Qdrant (semantic).
2. Sparse retrieval from OpenSearch or Elasticsearch (keyword).
3. Combines and re-ranks the top hits.

## Directory Structure
retrieval_service/ ├── requirements.txt ├── app.py └── README.md



## Requirements

- `qdrant-client` (or other vector DB client)
- `opensearch-py` or `elasticsearch` library
- Possibly a cross-encoder re-ranker: `transformers`, `sentence-transformers`

## Example `app.py`

```python
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from qdrant_client import QdrantClient
from opensearchpy import OpenSearch

# Qdrant
qdrant_client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "arabic_docs"

# OpenSearch
os_client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_compress=True
)
OS_INDEX = "arabic_docs_sparse"

# Cross-Encoder re-ranker (optional)
RE_RANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Replace with Arabic-friendly
ranker_tokenizer = AutoTokenizer.from_pretrained(RE_RANKER_NAME)
ranker_model = AutoModelForSequenceClassification.from_pretrained(RE_RANKER_NAME)

def dense_search(query, top_k=10):
    # For Qdrant, we need a vector representation of the query
    # (reuse the same model from embedding_service or a smaller model).
    # Stub, returns top_k points
    pass

def sparse_search(query, top_k=10):
    # Standard keyword match in OpenSearch
    body = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["text", "metadata.*"]
            }
        }
    }
    results = os_client.search(index=OS_INDEX, body=body)
    # parse hits...
    return []

def re_rank(query, candidates, top_n=3):
    # Convert query + candidate text into a cross-encoder score
    # Sort by descending score, return top_n
    pass

def hybrid_search(query):
    dense_results = dense_search(query)
    sparse_results = sparse_search(query)
    combined = dense_results + sparse_results
    # re_rank them
    final_results = re_rank(query, combined)
    return final_results

if __name__ == "__main__":
    test_query = "ما هي سياسة القبول في الجامعة؟"
    hits = hybrid_search(test_query)
    print(hits)

Enhancements
Cross-Encoder Model: Fine-tune an Arabic cross-encoder.
Weighting Strategy: Combine dense and sparse scores with a custom formula before re-ranking.
Metadata Filtering: e.g., date range, doc type.