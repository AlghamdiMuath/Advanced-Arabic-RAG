import os
import openai
from typing import List, Dict
import sys
from dotenv import load_dotenv, dotenv_values
load_dotenv()
# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from retrieval_service.app import dense_search


# Make sure your OPENAI_API_KEY is set
openai.api_key = os.getenv("OPENAI_API_KEY")

def retrieve_context(query: str, top_n: int = 3) -> List[Dict[str, str]]:
    return dense_search(query, top_n)


def generate_answer(query: str, context_chunks: List[Dict[str, str]]) -> str:
    """
    Uses the OpenAI ChatCompletion API to generate an Arabic answer,
    incorporating the provided context chunks.
    """
    # Build a single 'context' string by joining the top retrieved chunks
    context_text = "\n".join(f"- {chunk['text']}" for chunk in context_chunks)

    system_content = f"""\
أنت مساعد ذكي. الآتي هو سياق من وثائق الجامعة:
{context_text}

السؤال: {query}
أجب باللغة العربية الفصحى بما يفيد المستخدم، واستشهد بالمقاطع عند الضرورة.
"""
    messages = [
        {"role": "system", "content": system_content},
    ]

    # Call OpenAI's ChatCompletion endpoint
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=messages,
        temperature=0.2,
        max_tokens=300
    )

    # Extract the assistant message
    answer = response.choices[0].message.content
    return answer.strip()


if __name__ == "__main__":
    # Example usage
    user_question = "ما هو آخر موعد لتقديم الطلبات؟"

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = retrieve_context(user_question, top_n=3)

    # Step 2: Generate answer from LLM
    final_answer = generate_answer(user_question, retrieved_chunks)

    print("===== Final Answer =====")
    print(final_answer)
