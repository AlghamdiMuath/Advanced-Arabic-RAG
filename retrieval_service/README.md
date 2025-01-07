# Retrieval service

This microservice performs hybrid search **(only dense for now)** for Arabic text by combining dense semantic search using Qdrant, sparse keyword search using OpenSearch, and re-ranking results with a cross-encoder model.

## Features
- **Dense Search**:
  - Uses `CAMeL-Lab/bert-base-arabic-camelbert-msa` for embedding queries and document vectors.
  - Retrieves top matches based on cosine similarity using Qdrant.
- **Sparse Search** future plan:
  - Executes keyword-based search using OpenSearch across text and metadata fields.
- **Re-ranking**:
  - Refines results using a cross-encoder for improved ranking based on query relevance.
- **Hybrid Search** future plan:
  - Combines dense and sparse results for a comprehensive retrieval pipeline.

## Installation
### 1. Clone the Repository
Clone the repository and navigate to this microservice's directory:
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
cd advanced-arabic-rag/retrieval_service
```

### 2. Install Python Dependencies
- Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install Qdrant 
-Explained in the **embedding_service** README

### 4. Start the Server
Ensure Qdrant is running:
- Qdrant: http://127.0.0.1:6333

## Usage
### Running the Service
- 1. Modify the script if needed to adjust parameters like TOP_K and FINAL_TOP_N.
- 2. Run the script to perform dense search:
```bash
python app.py
```

## Configuration
- Qdrant Settings:
- -Host: localhost
- -Port: 6333
- -Collection: arabic_docs
- Models:
- -Query Embedding: CAMeL-Lab/bert-base-arabic-camelbert-msa
- -Re-ranking: cross-encoder/ms-marco-MiniLM-L-6-v2 (replace with an Arabic cross-encoder if available).
## Example Input and Output

### Example Query
```bash

بماذا يتميز برنامج السنه التحضيريه بجامعه الملك فهد للبترول والمعادن ؟
```

### Example Output
```bash

Rank: 1
Text: النص الأول المتعلق بالاستعلام...
Sparse/Dense Score: 0.89
Re-rank Score: 4.76
Metadata: {...}
----------------------------------------
Rank: 2
Text: النص الثاني المتعلق بالاستعلام...
Sparse/Dense Score: 0.85
Re-rank Score: 4.53
Metadata: {...}
----------------------------------------
```

## Notes
- **Replace the re-rank model with a suitable Arabic cross-encoder for better results.**
- Ensure all models and services (Qdrant) are correctly installed and running.
- The script is optimized for GPU but will fallback to CPU if no GPU is available.