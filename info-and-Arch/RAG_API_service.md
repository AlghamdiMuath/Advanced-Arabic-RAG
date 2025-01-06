

# 06 RAG API Service

Provides a unified API endpoint:
1. Accepts user queries (HTTP POST/GET).
2. Runs retrieval + re-ranking.
3. Calls LLM generation.
4. Returns the final answer.

## Directory Structure
rag_api_service/ ├── requirements.txt ├── app.py └── README.md


## Requirements

- `fastapi` or `flask`
- `uvicorn` or `gunicorn` for production

## Example `app.py` (FastAPI)

```python
from fastapi import FastAPI, Request
from retrieval_service import hybrid_search
from llm_generation_service import generate_answer

app = FastAPI()

@app.post("/query")
async def query_endpoint(request: Request):
    data = await request.json()
    user_query = data.get("query", "")

    # 1. Retrieve
    top_chunks = hybrid_search(user_query)  # returns list of chunk dicts

    # 2. Generate
    answer = generate_answer(user_query, top_chunks)

    return {"answer": answer, "chunks_used": top_chunks}

# if needed: uvicorn main:app --reload

Enhancements
Authentication: Role-based access for staff.
Rate Limiting: Prevent overload on the LLM.
Logging: Save query+answer pairs for future fine-tuning.