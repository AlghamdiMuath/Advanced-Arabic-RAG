import os
import json
import re
import uuid
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# -- Camel Tools imports --
from camel_tools.utils.dediac import dediac_ar
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.normalize import (
    normalize_unicode,
    normalize_alef_ar,
    normalize_alef_maksura_ar,
    normalize_teh_marbuta_ar
)

# ---------------------- CONFIGURATION ----------------------
INPUT_FOLDER = "./data_extraction_output"  # folder with JSON from Data Extraction
OUTPUT_FOLDER = "./processed_chunks"       # where we'll store chunked JSON
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

USE_SEMANTIC_CHUNKING = False  # switch to True if you want paragraph-based chunking

# ---------------------- ARABIC TEXT CLEANING ----------------------
def clean_arabic_text(text: str) -> str:
    """
    Cleans & normalizes Arabic text:
      1) Removes tatweel/kashida (ـــ).
      2) Removes extra spaces.
      3) Normalizes Unicode (NFKC).
      4) Removes diacritics.
      5) Normalizes various Alef forms, Teh Marbuta, Alef Maksura, etc.

    Adjust the steps or remove any you don’t need.
    """

    # 1) Remove tatweel
    text = re.sub(r"ـ+", "", text)

    # 2) Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # 3) Normalize Unicode (compatibility=True => NFKC)
    text = normalize_unicode(text, compatibility=True)

    # 4) Remove diacritics
    text = dediac_ar(text)

    # 5) Normalize various forms of Alef
    text = normalize_alef_ar(text)

    # 6) Normalize Alef Maksura -> Yeh
    text = normalize_alef_maksura_ar(text)

    # 7) Normalize Teh Marbuta -> Heh
    text = normalize_teh_marbuta_ar(text)

    return text


# ---------------------- TOKENIZATION ----------------------
def tokenize_arabic(text: str) -> list:
    """
    Tokenizes Arabic text using camel_tools.simple_word_tokenize.
    If you prefer Farasa, uncomment & adapt accordingly.
    """
    tokens = simple_word_tokenize(text)
    return tokens

# ---------------------- CHUNKING ----------------------
def chunk_text_fixed(tokens, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Fixed-size chunking by token count.
    E.g., chunk_size=512, overlap=50 => each chunk has 512 tokens, with
    50-token overlap with the previous chunk.
    """
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        start += (chunk_size - overlap)
    return chunks

def chunk_text_semantic(text: str) -> list:
    """
    Example "semantic" chunking by paragraph or heading breaks.
    Real-world usage could get more sophisticated (e.g. ML-based segmenters).
    """
    # Split on blank lines => paragraphs
    paragraphs = re.split(r"\n\s*\n", text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


# ---------------------- MAIN PROCESSING ----------------------
def process_single_json(json_path: str) -> str:
    """
    Reads one JSON file, cleans & normalizes Arabic text, splits into chunks,
    and saves an output JSON with chunked records.
    Returns the path to the new JSON file, or "" on failure.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON {json_path}: {e}")
        return ""

    raw_text = data.get("text", "")
    if not raw_text.strip():
        print(f"[WARN] No text found in {json_path}. Skipping.")
        return ""

    cleaned_text = clean_arabic_text(raw_text)

    # Either do semantic chunking or fixed chunking
    if USE_SEMANTIC_CHUNKING:
        text_chunks = chunk_text_semantic(cleaned_text)
    else:
        # Tokenize -> chunk
        tokens = tokenize_arabic(cleaned_text)
        text_chunks = chunk_text_fixed(tokens, CHUNK_SIZE, CHUNK_OVERLAP)

    processed_records = []
    base_id = data.get("id") or str(uuid.uuid4())
    filename = data.get("filename", "unknown_file")

    for i, chunk in enumerate(text_chunks):
        record_id = str(uuid.uuid4())
        record = {
            "id": record_id,
            "text": chunk,
            "metadata": {
                "filename": filename,
                "original_doc_id": base_id,
                "chunk_index": i
            }
        }
        processed_records.append(record)

    # Write out the new JSON file
    base_name = os.path.basename(json_path)
    out_file_name = base_name.replace(".json", "_chunks.json")
    out_path = os.path.join(OUTPUT_FOLDER, out_file_name)

    try:
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(processed_records, f_out, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write processed JSON for {json_path}: {e}")
        return ""

    return out_path


def process_all_json_files(input_folder: str):
    """
    Scans for .json files in the input folder, processes them in parallel,
    and writes chunked JSON outputs to OUTPUT_FOLDER.
    """
    all_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".json")]
    if not all_files:
        print(f"[INFO] No JSON files found in {input_folder}. Nothing to do.")
        return

    json_paths = [os.path.join(input_folder, f) for f in all_files]
    print(f"[INFO] Found {len(json_paths)} JSON files. Processing in parallel...")

    num_workers = max(1, cpu_count() - 1)
    results = []

    with Pool(processes=num_workers) as pool:
        for result_path in tqdm(pool.imap(process_single_json, json_paths), total=len(json_paths)):
            results.append(result_path)

    print("[INFO] Done. Generated chunked JSON:")
    for r in results:
        if r:
            print("  -", r)


if __name__ == "__main__":
    """
    Usage:
      1) Place extracted JSON files in `INPUT_FOLDER`.
      2) Run `python app.py`.
      3) Check `OUTPUT_FOLDER` for new _chunks.json files.
    """
    process_all_json_files(INPUT_FOLDER)
