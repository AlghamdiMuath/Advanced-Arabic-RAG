import json
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch

# Load preprocessed data
def load_preprocessed_data(input_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise FileNotFoundError(f"Error loading file {input_path}: {e}")

# Initialize the embedding model and tokenizer
def initialize_model(model_name='aubmindlab/bert-base-arabertv02'):  # AraBERT
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        raise RuntimeError(f"Error initializing model {model_name}: {e}")

# Generate embeddings for text chunks
def generate_embeddings(text_chunks, tokenizer, model, batch_size=32):
    model.eval()
    embeddings = []

    with torch.no_grad():
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            inputs = tokenizer(batch, return_tensors='pt', padding=True, truncation=True, max_length=512)
            outputs = model(**inputs)
            batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()  # Average pooling
            embeddings.extend(batch_embeddings)

    return np.array(embeddings)

# Save embeddings and metadata in binary format
def save_embeddings_binary(embeddings, metadata, output_path):
    try:
        np.savez_compressed(output_path, embeddings=embeddings, metadata=metadata)
    except Exception as e:
        raise IOError(f"Error saving embeddings to {output_path}: {e}")

# Save embeddings in JSON format (fallback)
def save_embeddings_json(embeddings, metadata, output_path):
    try:
        data = [
            {'embedding': embedding.tolist(), 'metadata': meta}
            for embedding, meta in zip(embeddings, metadata)
        ]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise IOError(f"Error saving embeddings to {output_path}: {e}")

# Main execution block
if __name__ == "__main__":
    input_path = 'processed_data.json'  # Output from data-processing.py
    output_path_binary = 'embeddings.npz'
    output_path_json = 'embeddings.json'
    model_name = 'aubmindlab/bert-base-arabertv02'

    # Load data
    preprocessed_data = load_preprocessed_data(input_path)

    # Prepare inputs
    text_chunks = [item['text'] for item in preprocessed_data]
    metadata = [{'document_name': item['document_name'], 'section': item['section']} for item in preprocessed_data]

    # Initialize model
    tokenizer, model = initialize_model(model_name)

    # Generate embeddings
    embeddings = generate_embeddings(text_chunks, tokenizer, model)

    # Save embeddings
    save_embeddings_binary(embeddings, metadata, output_path_binary)
    save_embeddings_json(embeddings, metadata, output_path_json)
