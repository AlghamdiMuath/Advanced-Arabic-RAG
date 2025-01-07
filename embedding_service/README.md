# Embedding Service

This microservice processes chunked JSON files containing Arabic text, generates embeddings using a pre-trained Transformer model, and indexes them into a **Qdrant** vector database for efficient similarity search.

## Features
- **Arabic Text Embedding**:
  - Utilizes the `CAMeL-Lab/bert-base-arabic-camelbert-msa` model to generate embeddings.
  - Supports GPU acceleration for faster processing.
- **Qdrant Integration**:
  - Indexes embeddings into a Qdrant collection.
  - Configurable to use cosine similarity for efficient retrieval.
- **Batch Indexing**:
  - Processes multiple JSON chunk files in parallel for scalability.

## Installation
### 1. Clone the Repository
Clone the repository and navigate to this microservice's directory:
```bash
git clone https://github.com/AlghamdiMuath/advanced-arabic-rag
cd advanced-arabic-rag/embedding_service
```
### 2. Install the required dependencies
   ```bash
   pip install -r requirements.txt
   ```
### 2. Install Qdrant
Download and Extract Qdrant in WSL
- 1. Open your WSL (Ubuntu/Debian/etc.) terminal.
- 2. Navigate to a directory where you want to store Qdrant (e.g., your home folder):

```bash
cd ~
   ```
- 3. Download the x86_64-unknown-linux-gnu build (version 1.12.5):
```bash
wget https://github.com/qdrant/qdrant/releases/download/v1.12.5/qdrant-x86_64-unknown-linux-gnu.tar.gz
   ```
If there’s a newer version, just replace v1.12.5 and the filename with the current one.  

- 4. Extract the tarball:

```bash
tar -xvf qdrant-x86_64-unknown-linux-gnu.tar.gz

```
This should leave you with an executable named qdrant.
To check write
```bash
ls
```
- 5. Make the Qdrant binary executable (just in case):

```bash
chmod +x qdrant
```

## Usage
- Running the Server
1. **Ensure chunked JSON files (e.g., _chunks.json) are placed in the processed_chunks folder.**
2. Run Qdrant listening on 0.0.0.0 (all interfaces) at port 6333

```bash
qdrant --uri 0.0.0.0 --port 6333
```
3. Open new WSL terminal (leave the first open and running the qdrant server)
4. **Run the script to index the chunks:*
```bash
python app.py
```

## Configuration
- Model Configuration:
- -Default model: CAMeL-Lab/bert-base-arabic-camelbert-msa.
- -Modify MODEL_NAME in the script to use a different transformer model.
- Qdrant Settings:
- -Default host: localhost.
- -Default port: 6333.
- -Change QDRANT_HOST and QDRANT_PORT as needed.
- Chunk Folder:
- -Default folder: ./processed_chunks.
- -Update CHUNKS_FOLDER to change the path.

## File Structure
- Input Folder (processed_chunks):
- -Place _chunks.json files here. Each file must follow this format:
```bash
[
  {
    "id": "chunk-id-1",
    "text": "Arabic text here...",
    "metadata": {
      "filename": "example.pdf",
      "original_doc_id": "doc-id-1",
      "chunk_index": 0
    }
  }
]
```

## Notes
- Ensure Qdrant is running and accessible before starting the script.
- The model can process up to 512 tokens per text chunk. Longer texts are truncated.