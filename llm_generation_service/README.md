# LLM Generation Service

The **LLM Generation Service** combines retrieval-augmented generation (RAG) techniques with OpenAI's ChatCompletion API (**Temporarily, later will be a locally hosted model**)to generate context-aware answers in Arabic. It retrieves relevant chuncks/contexts from the knowledge base we created and uses it to craft precise, user-centric responses in Modern Standard Arabic (MSA).

## Features
- **Contextual Retrieval**:
  - Uses the `dense_search` function from the Retrieval Service to fetch the top N most relevant context chunks for a given query.
- **Answer Generation**:
  - Leverages OpenAI's GPT models (e.g., `gpt-3.5-turbo` or `gpt-4`) to generate high-quality answers.
  - Incorporates the retrieved context to produce accurate and informative responses.
- **Arabic Language Support**:
  - Generates answers in Modern Standard Arabic (MSA), ensuring clarity and professionalism.

## Installation
### 1. Clone the Repository
Clone the repository and navigate to this microservice's directory:
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
cd advanced-arabic-rag/llm_generation_service
```
### 2. Install Python Dependencies
- Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
- Create a .env file in the root of the repository or ensure OPENAI_API_KEY is set in your environment: 
```bash
OPENAI_API_KEY="your_openai_api_key"
```
## Usage
### Running the Service
- 1. Provide a user query in Arabic.
- 2. The service will:
- - Retrieve the top N relevant context chunks using the Retrieval Service, then rerank it (quality of reranking depends on the model selection in retrieval service).

- -Use the OpenAI API to generate a context-aware answer in Arabic.

- 3. Service Run command:
```bash
python app.py
```
### Example Query and Output
- Input Query:
```bash

ما هو آخر موعد لتقديم الطلبات؟
```

- Example Output:
```bash

===== Final Answer =====
آخر موعد لتقديم الطلبات هو 15 أغسطس 2023، وفقاً للوثائق المرفقة.
```

## Configuration
### Models:
- Retrieval: The service uses the dense_search function from the Retrieval Service for retrieving context chunks.
- Generation: Uses OpenAI's gpt-3.5-turbo or gpt-4 for answer generation.
### Parameters:
- top_n: Number of context chunks to retrieve (default: 3).
- temperature: Controls randomness in the output (default: 0.2).
- max_tokens: Maximum length of the generated answer (default: 300).
## Notes
- Ensure the Retrieval Service is functional and accessible before running this service.
- OpenAI API key is required to use the ChatCompletion endpoint.
- Replace the model name (gpt-3.5-turbo) with gpt-4 if access is available for higher quality answers.
## Dependencies
- run:
```bash
- **pip install requirements.txt**
```
- retrieval_service (from the same repository)
### Compatible with other services in the advanced-arabic-rag project.
