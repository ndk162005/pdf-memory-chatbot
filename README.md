# PDF Memory Chatbot

A specialized conversational AI designed to ingest, process, and retrieve information from PDF documents using Ollama, Sentence Transformers, and ChromaDB.

## Features

- **Document Ingestion:** Upload and parse PDF documents accurately using PyMuPDF.
- **Smart Chunking:** Text is broken into manageable chunks for effective embedding generation.
- **Vector Search:** Uses Sentence Transformers to create embeddings and ChromaDB for quick retrieval.
- **Conversational Memory:** Remembers past conversation turns for coherent interactions.
- **Local LLM Integration:** Communicates with local instances of Ollama for fully private processing.

## Prerequisites

- Python 3.10 or higher
- Ollama installed locally
- The `qwen3:8b` model pulled in Ollama (`ollama pull qwen3:8b`)

## Installation

1. Clone or navigate to the project repository.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start your local Ollama server if not already running.
2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
3. Open your browser and navigate to `http://127.0.0.1:8000` to interact with the frontend, or use the API docs at `http://127.0.0.1:8000/docs`.

## Configuration

The application uses environment variables for configuration. Key variables include:

- `OLLAMA_BASE_URL`: Defaults to `http://localhost:11434`
- `OLLAMA_MODEL`: Defaults to `qwen3:8b`
- `EMBEDDING_MODEL_NAME`: Defaults to `all-MiniLM-L6-v2`
- `MAX_CHUNK_SIZE`: Defaults to `1000`
- `CHUNK_OVERLAP`: Defaults to `100`

## Architecture Summary

1. **Uploads:** User uploads a PDF to `/upload`. 
2. **Ingestion & Vectorization:** The app extracts text, splits it into chunks, embeds it using local Sentence Transformers, and stores it in ChromaDB.
3. **Conversational Engine:** When asked a question, it queries ChromaDB for relevant document chunks, combines them with chat history, and sends the prompt to the Ollama model to generate an answer.
4. **State Storage:** Conversations and chunks are managed with structured storage.

## Technology Stack

- **Backend:** FastAPI, Uvicorn
- **PDF Parsing:** PyMuPDF
- **Embeddings:** Sentence Transformers
- **Vector Database:** ChromaDB
- **LLM Integration:** Ollama
