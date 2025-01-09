# Advanced-Arabic-RAG

## Overview
**Advanced-Arabic-RAG** is a modular, fully on-premise solution for **Arabic-focused Retrieval-Augmented Generation (RAG)**. The system is designed to **extract**, **process**, and **embed** Arabic documents while providing a **conversational Q&A interface** powered by local and scalable services.

This repository is structured to allow independent testing and deployment of each service while enabling an integrated workflow for RAG tasks. It supports document ingestion, processing, embedding, retrieval, and answer generation, all tailored for Modern Standard Arabic (MSA).

---

## Repository Structure
Below is the directory structure, where each microservice has its dedicated folder with a specific `README.md` for detailed usage instructions:

```plaintext
.
├── data_extraction_service/       # Extracts text from PDFs
├── data_processing_service/       # Cleans and chunks Arabic text
├── embedding_service/             # Embeds chunks into a vector database
├── retrieval_service/             # Handles dense retrieval from Qdrant
├── llm_generation_service/        # Generates answers using retrieved context
├── rag_api_service/               # Unified API interface for the RAG pipeline
├── docker-compose.yml             # Example Docker Compose setup
├── .gitignore                     # Git ignore rules
└── README.md                      # General project documentation (this file)
```
---

## Services Overview
### 1- data_extraction_service

- Extracts text from PDF files (text-based and scanned) into JSON format.
- Supports single file and batch processing.

### 2. data_processing_service

- Cleans, normalizes, and tokenizes Arabic text.
- Splits text into manageable chunks for embedding.

### 3. embedding_service

- Generates dense vector embeddings for text chunks.
- Stores embeddings and metadata in a vector database (Qdrant).

### 4. retrieval_service

- Performs dense retrieval using Qdrant (with plans for hybrid retrieval).
- Ranks results using a cross-encoder.

### 5. llm_generation_service

- Fetches relevant context and generates answers in Arabic.
- Temporarily uses OpenAI's GPT models (future plan: local LLM support).

### 6. rag_api_service

- Provides a unified _/query_ endpoint for retrieval and answer generation.
- Combines all services for a seamless RAG pipeline.

## Getting Started
### 1. Clone the Repository
```bash
git clone https://github.com/AlghamdiMuath/Advanced-Arabic-RAG.git
cd Advanced-Arabic-RAG
```
### 2. Set Up Environment
- Install Python 3.9+. (used 3.12)
- Ensure system dependencies for OCR (e.g., Tesseract, PaddleOCR) and Qdrant are installed.

### 3. Configure Microservices
- Navigate to each service directory and install dependencies:
```bash
cd <service_directory>
pip install -r requirements.txt
```
- or download all from the consolodated requirements.txt on the root:
```bash
pip install -r requirements.txt
```
- Update configurations (e.g., API keys,folder paths) in .env files or service-specific settings.

## Running the Full Project
### Option 1: Running Services Manually
Start services individually in the following order:

1. _data_extraction_service_: Extract text from PDFs.
2. _data_processing_service_: Process and chunk the extracted text.
3. _embedding_service_: Embed the chunks and store them in Qdrant (follow the steps for running the qdrant server).
4. _retrieval_service_: Enable context retrieval.
5. _llm_generation_service_: Generate answers using retrieved context.
6. _rag_api_service_: Launch the unified API for user queries.

## Testing Guidelines
### Testing Each Service
To test services independently:
1. Navigate to the service folder:
```bash
cd <service_directory>
```
2. Follow the specific instructions in its **README.md**.

## Integrated Workflow
1. Start the rag_api_service:
```bash

cd rag_api_service
uvicorn app:app --host 0.0.0.0 --port 8000
```

2. Send a query to the /query endpoint:
```bash

{
  "query": "ما هي شروط القبول في الجامعة؟"
}
```
