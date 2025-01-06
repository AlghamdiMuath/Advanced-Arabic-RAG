# Project Overview

**Goal**  
Create a fully on-premises, Arabic-focused RAG (Retrieval-Augmented Generation) system that:
1. Ingests and extracts text from PDF files (including scanned docs).
2. Processes and normalizes Arabic text.
3. Generates semantic embeddings and stores them in a vector database.
4. Provides hybrid retrieval (dense + sparse).
5. Uses an Arabic-capable LLM to generate natural-language answers.
6. Is modular enough to be adapted to any Arabic-speaking university with minimal coding effort.

## Architecture Diagram (Conceptual)
[PDFs/Scanned Docs] --> [01 Data Extraction Service] --> [02 Data Processing Service] --> [03 Embedding Service] --> [Vector DB / Sparse Index] -> [04 RAG API Service] --> [LLM] | [Answer to user]


## Technology Stack
- **Python 3.9+**  
- **OCR**: PaddleOCR or Tesseract  
- **Layout & Table Extraction**: LayoutLMv3 / DocTR (optional)  
- **Arabic Processing**: CAMeL Tools, Farasa  
- **Embeddings**: Hugging Face Transformers (AraBERT, MARBERT, XLM-R)  
- **Vector Database**: Qdrant, Weaviate, or Milvus (on-prem)  
- **Sparse Index**: OpenSearch or Elasticsearch (on-prem)  
- **LLM**: Locally hosted LLaMA-2, BloomZ, or specialized Arabic LLM (JAIS)  
- **Orchestration**: Docker Compose or Kubernetes (on-prem)

---
