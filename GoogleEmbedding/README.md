#OPTIONAL FOLDER - GoogleEmbedding

# ☁️ Google Cloud Embeddings (Lightweight Setup)

This folder contains alternative backend logic that uses **Google Generative AI** for text embeddings instead of local Hugging Face models.

## ⚙️ How to Use

### 1. Prerequisites
Ensure your `.env` file in the main project folder has your Google API key:
```env
GEMINI_API_KEY=your_actual_api_key_here

### 2. Replace Backend Logic
------------------------------
Copy code from: google_llm.py
Paste into: llm_helper.py (in the main folder)
------------------------------
Copy code from: google_vector.py
Paste into: vector_db.py (in the main folder)
------------------------------

### 3. Clean Dependencies
------------------------------
**Remove:** torch, transformers, sentence-transformers, unstructured 

**Ensure you have:** langchain-google-genai, google-genai
------------------------------