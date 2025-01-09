import os
import sys
from typing import Dict, Any, List

from fastapi import FastAPI, Request

# --------------------------------------------------------------------
# Optionally, if the retrieval & LLM code is outside this folder, e.g.:
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from llm_generation_service.app import generate_answer, retrieve_context 
# --------------------------------------------------------------------

app = FastAPI(title="RAG API Service", version="1.0.0")
   
# ------------------ ACTUAL FASTAPI ENDPOINT ------------------
@app.post("/query")
async def query_endpoint(request: Request):
    """
    Endpoint that:
    1) Reads JSON with 'query'
    2) Calls retrieval (top N chunks)
    3) Calls LLM generation with those chunks
    4) Returns final answer + the chunks used
    """
    data = await request.json()
    user_query = data.get("query", "")

    # 1) Retrieve top chunks
    top_chunks = retrieve_context(user_query)

    # 2) Generate final answer using LLM
    final_answer = generate_answer(user_query, top_chunks)

    return {
        "answer": final_answer,
        "chunks_used": top_chunks
    }


# ------------------ MAIN / RUNNER ------------------
if __name__ == "__main__":
    """
    For dev testing, run:
      uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    Or just:
      python app.py
    (If you have the code to auto-run the server. If not, see below.)
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
