# RAG API Service

The **RAG API Service** provides a RESTful API interface for retrieval-augmented generation (RAG). It integrates a retrieval system with a language model to deliver context-aware answers in Arabic. Users can query the API, and the service retrieves relevant context chunks from the knowledge base created before, then generates the final response using OpenAI's GPT models.

## Features
- **API Interface**:
  - A simple and efficient `/query` endpoint for interacting with the RAG system.
- **Contextual Retrieval**:
  - Fetches the top relevant chunks using the `retrieve_context` function.
- **Answer Generation**:
  - Generates answers in Modern Standard Arabic (MSA) using the `generate_answer` function.
- **Easy Integration**:
  - Compatible with other services in the **advanced-arabic-rag** project.

## Installation
### 1. Clone the Repository
Clone the repository and navigate to this microservice's directory:
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
cd advanced-arabic-rag/rag_api_service
```

### 2. Install Python Dependencies
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```
### 3. Set Up Environment Variables
Ensure the .env file with the OPENAI_API_KEY is in the root of the project, or set the environment variable manually:
```bash
OPENAI_API_KEY="your_openai_api_key"
```
## Usage
### Running the Service
Start the FastAPI server:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
### API Endpoint
Endpoint: /query
- Method: POST
- Input: JSON object with a query field (Arabic text).
- Output: JSON object containing:
-- answer: The generated response.
-- chunks_used: List of context chunks used for the response.
Example Request:
```bash
{
  "query": "ما هي شروط الالتحاق بجامعة الملك فهد للبترول والمعادن؟"
}
```
Example Response:
```bash
{
  "answer": "شروط الالتحاق بجامعة الملك فهد للبترول والمعادن تشمل اجتياز السنة التحضيرية وتقديم الوثائق المطلوبة.",
  "chunks_used": [
    {
      "text": "الوثيقة الأولى المتعلقة بشروط القبول...",
      "metadata": {
        "filename": "admissions.pdf",
        "chunk_index": 0
      }
    },
    {
      "text": "الوثيقة الثانية حول الوثائق المطلوبة...",
      "metadata": {
        "filename": "requirements.pdf",
        "chunk_index": 3
      }
    }
  ]
}
```

## Configuration
### - Models:
- Retrieval: Uses the retrieve_context function to fetch context chunks.
- Generation: Leverages the generate_answer function for LLM-powered responses.
### - Server Settings:
- Default Host: 0.0.0.0
- Default Port: 8000

## Notes
- Ensure the llm_generation_service and retrieval_service are functional and accessible.
- OpenAI API key is required to enable LLM-based generation.
- The service is designed to work seamlessly with other components of the advanced-arabic-rag project.

## Dependencies
- Project dependencies: llm_generation_service, retrieval_service