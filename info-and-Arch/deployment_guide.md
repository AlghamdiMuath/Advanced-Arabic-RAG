
# 07 Deployment Guide

Outlines how to deploy the entire system on-premise, using Docker Compose or Kubernetes.

## Docker Compose Example
version: "3.8" services: data_extraction_service: build: ./data_extraction_service volumes: - ./data:/app/input_pdfs - ./extracted_json:/app/output_json command: python app.py

data_processing_service: build: ./data_processing_service volumes: - ./extracted_json:/app/input_json - ./processed_chunks:/app/processed_chunks command: python app.py

qdrant: image: qdrant/qdrant ports: - "6333:6333"

embedding_service: build: ./embedding_service volumes: - ./processed_chunks:/app/processed_chunks depends_on: - qdrant command: python app.py

opensearch: image: opensearchproject/opensearch:latest environment: - discovery.type=single-node ports: - "9200:9200"

retrieval_service: build: ./retrieval_service depends_on: - qdrant - opensearch command: python app.py

llm_generation_service: build: ./llm_generation_service # Might need GPU pass-through or special Docker base for LLM

rag_api_service: build: ./rag_api_service depends_on: - retrieval_service - llm_generation_service ports: - "8000:8000" command: uvicorn app:app --host 0.0.0.0 --port 8000

## Other Considerations

- **Security**: On-prem firewall, TLS for internal communication.  
- **Logging & Monitoring**: Use Prometheus + Grafana or EFK stack.  
- **Scale**: If usage spikes, horizontally scale the `rag_api_service` or `llm_generation_service`.

---
