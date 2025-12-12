# Setup Instructions for RAG System

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will install:
- Flask and web dependencies
- FAISS-CPU (vector similarity search)
- Sentence Transformers (embeddings)
- Google Generative AI (Gemini API)
- NumPy (numerical operations)

The installation may take a few minutes, especially for sentence-transformers which will download the embedding model on first use.

## Step 2: Set Gemini API Key

### Option A: Using .env file (Local Development)

The `.env` file has been created with your API key. Make sure it contains:

```
GEMINI_API_KEY=AIzaSyA0zZO5SqlgN6QdiRnC0mroRhNnR9JXvc8
```

### Option B: Environment Variable (Production/Render)

In Render dashboard:
1. Go to your service settings
2. Navigate to "Environment" section
3. Add new environment variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyA0zZO5SqlgN6QdiRnC0mroRhNnR9JXvc8`
4. Save and redeploy

## Step 3: Build FAISS Index

After installing dependencies, build the RAG index:

```bash
python3 build_rag_index.py
```

This will:
- Load Q&A pairs from `data/niya_qa_pairs.json`
- Create embeddings (takes 1-2 minutes first time)
- Build FAISS index
- Save to `data/niya_faiss.index`

**Expected output:**
```
==================================================
Building RAG Index for Niya Help Bot
==================================================

1. Loading Q&A pairs from data/niya_qa_pairs.json...
   Loaded 12 Q&A pairs

2. Initializing RAG system...

3. Building FAISS index...
   This may take a few minutes for the first time...
Loading embedding model...
Embedding model loaded!
FAISS index built and saved with 12 Q&A pairs

==================================================
✅ RAG Index built successfully!
==================================================

Total Q&A pairs: 12
Index saved to: data/niya_faiss.index
Q&A data saved to: data/niya_qa_pairs.json

Similarity threshold: 0.75
Ready to use RAG system!
```

## Step 4: Test the System

1. Start your Flask app:
   ```bash
   python3 app.py
   # or
   gunicorn -c gunicorn_config.py app:app
   ```

2. Open the app in browser and log in

3. Click the Niya help bot icon (floating button)

4. Try typing a question like:
   - "How do I mark attendance?"
   - "How to add a student?"
   - "What is attendance?"

5. You should see:
   - Your question appears on the right
   - Typing indicator appears
   - Niya's response appears on the left

## Troubleshooting

### "ModuleNotFoundError: No module named 'faiss'"
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct virtual environment

### "RAG index not initialized"
- Run: `python3 build_rag_index.py`
- Check that `data/niya_faiss.index` exists

### "Gemini API error"
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota/limits in Google AI Studio
- Ensure internet connection for API calls

### Memory Issues (512MB RAM)
- The system should work, but if you encounter issues:
  - Use smaller embedding model (change in `utils/rag_system.py`)
  - Reduce number of Q&A pairs
  - Consider using external API only (no local embeddings)

## Files Created

- `data/niya_faiss.index` - FAISS vector index (generated)
- `data/niya_embeddings.pkl` - Embeddings cache (generated)
- `data/niya_qa_pairs.json` - Q&A database (source)

## Next Steps

- Add more Q&A pairs to `data/niya_qa_pairs.json`
- Rebuild index after adding pairs: `python3 build_rag_index.py`
- Customize similarity threshold in `utils/rag_system.py`

