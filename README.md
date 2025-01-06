# Advanced Arabic RAG Project

This repository contains a modular, fully on-premise solution for **Arabic-focused Retrieval-Augmented Generation (RAG)**.  
The system is designed to ingest, extract, process, and embed Arabic documents—then provide a **conversational Q&A** interface using **local large language models** (LLMs).

---

## Overview

1. **Data Extraction Service**  
   - Converts PDFs (text-based or scanned) into JSON with extracted text and metadata.
2. **Data Processing Service**  
   - Cleans, normalizes, and tokenizes Arabic text; splits it into manageable chunks.
3. **Embedding Service**  
   - Generates dense vector embeddings from the cleaned chunks and stores them in a vector database.
4. **Retrieval Service**  
   - Supports both dense (vector) and sparse (keyword-based) retrieval.
5. **LLM Generation Service**  
   - Loads a local Arabic-compatible language model (e.g., LLaMA-2, BloomZ, or JAIS) to generate answers.
6. **RAG API Service**  
   - A unified API endpoint that receives user queries, retrieves context, and calls the LLM to produce final answers.

---

## Repository Structure (Proposed)

```bash
.
├── data_extraction_service/      # Microservice folder
├── data_processing_service/      # Microservice folder
├── embedding_service/            # Microservice folder
├── retrieval_service/            # Microservice folder
├── llm_generation_service/       # Microservice folder
├── rag_api_service/              # Unified API microservice folder
├── docker-compose.yml            # Example Docker Compose setup
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
Note: The individual .md files (e.g., DATA_EXTRACTION_SERVICE.md) inside the info-and-arch contain more technical details and instructions to help developers implement each microservice.

Getting Started
Clone the Repo

bash
Copy code
git clone https://github.com/AlghamdiMuath/Advanced-Arabic-RAG.git
cd Advanced-Arabic-RAG
Review the Docs

Start with OVERVIEW.md to get a bird’s-eye view.
Move sequentially through the markdown files to understand each microservice.
Set Up Environment

Install Python 3.9+ and Docker (if you plan to use Docker Compose).
(Optional) Install any system-level dependencies required by OCR or ML libraries.
Configure Services

Each microservice folder has its own requirements.txt (or equivalent).
Update paths in config variables (INPUT_FOLDER, OUTPUT_FOLDER, etc.) based on your environment.
Run Services

Option A: Use Docker Compose.
bash
Copy code
docker-compose up --build
Option B: Run each microservice manually (e.g., python app.py) and set the appropriate ENV variables for connections.