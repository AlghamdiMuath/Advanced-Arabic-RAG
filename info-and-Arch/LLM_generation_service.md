# 05 LLM Generation Service

Handles the actual RAG pipeline step:
1. Receives a user query.
2. Calls `04_Retrieval_Service` to get top relevant chunks.
3. Feeds TOP 3 retrieved context + user query into a local LLM (both are part of a fitting prompt template).
4. Returns a natural-language answer.

## Directory Structure

llm_generation_service/ ├── requirements.txt ├── app.py └── README.md


## Requirements

- `transformers`
- The local LLM model weights (LLaMA-2, BloomZ, or JAIS)
- for the sake of immediate testing use OPENAI API

## Example `app.py`

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Example: LLaMA-2
LLM_NAME = "/path/to/local/llama2" 
tokenizer = AutoTokenizer.from_pretrained(LLM_NAME)
model = AutoModelForCausalLM.from_pretrained(LLM_NAME, device_map="auto")

def generate_answer(query, context_chunks):
    # Construct the prompt
    context_text = "\n".join([f"- {c['text']}" for c in context_chunks])
    system_prompt = f"""
    أنت مساعد ذكي. الآتي هو سياق من وثائق الجامعة:
    {context_text}

    السؤال: {query}
    أجب باللغة العربية الفصحى بما يفيد المستخدم، واستشهد بالمقاطع عند الضرورة.
    """
    inputs = tokenizer(system_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.2,
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

if __name__ == "__main__":
    # Stub: simulate retrieved chunks
    context = [{"text": "يجب على الطلاب تقديم طلباتهم قبل 1 مارس."}]
    question = "ما هو آخر موعد لتقديم الطلبات؟"
    print(generate_answer(question, context))

Enhancements
Prompt Templates: Maintain multiple templates for different types of questions (policy, factual, summary).
Citation Format: Insert references to chunk metadata in the generated text.
Chunk Selection: Provide only the top 3–5 chunks to the LLM to avoid prompt overload.
