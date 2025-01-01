import re
from camel_tools.utils.dediac import dediac_ar
from camel_tools.tokenizers.word import simple_word_tokenize
import json

def normalize_arabic(text):
    # Remove diacritics
    text = dediac_ar(text)
    # Unify ligatures (e.g., convert different forms of alef to a standard form)
    text = re.sub(r'[إأٱآا]', 'ا', text)
    return text

def tokenize_arabic(text):
    tokens = simple_word_tokenize(text)
    return tokens

def chunk_text(tokens, chunk_size=512, overlap=50):
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def preprocess_text(text):
    normalized_text = normalize_arabic(text)
    tokens = tokenize_arabic(normalized_text)
    chunks = chunk_text(tokens)
    return chunks

def handle_multilingual_queries(text, target_language='ar'):
    # Placeholder for translation API integration
    return text

def process_document(document, document_name):
    preprocessed_chunks = preprocess_text(document)
    processed_data = []
    for i, chunk in enumerate(preprocessed_chunks):
        processed_data.append({
            'document_name': document_name,
            'section': i,
            'text': ' '.join(chunk)
        })
    return processed_data

def save_processed_data(processed_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

def load_extracted_data(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    return extracted_data

# Example usage
input_path = 'extracted_data.json'  # Output from data-extraction.py
output_path = 'processed_data.json'
extracted_data = load_extracted_data(input_path)

all_processed_data = []
for item in extracted_data:
    document_text = item['text']
    document_name = item.get('document_name', 'unknown_document')
    processed_data = process_document(document_text, document_name)
    all_processed_data.extend(processed_data)

save_processed_data(all_processed_data, output_path)