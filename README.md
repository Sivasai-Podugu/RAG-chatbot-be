# RAG Chatbot Backend

This is the backend service for the Angel One Support chatbot. It uses Google's Gemini AI combined with RAG (Retrieval Augmented Generation) to provide accurate answers based on Angel One's documentation.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Google API key:
```
# Required
GOOGLE_API_KEY=your-api-key-here

# Optional
PORT=4000                # Port for the server to run on (default: 4000)
MAX_SCRAPE_LEVELS=3      # Maximum levels of web scraping depth (default: 5)
```

4. Create an `assets` folder in the backend directory and place your insurance PDFs there.

5. Run the server:
```bash
python app.py
```

The server will run on http://localhost:8000.

## API Endpoints

- POST `/api/answer`: Get an answer to a question
- GET `/api/health`: Health check endpoint

## Implementation Details

The system uses:
- ChromaDB for vector storage and similarity search
- Sentence Transformers for embeddings (all-MiniLM-L6-v2 model)
- Google's Gemini Pro for answer generation
- BeautifulSoup4 for web scraping
- PyPDF2 for PDF processing