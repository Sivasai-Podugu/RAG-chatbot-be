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
MAX_SCRAPE_LEVELS=3      # Maximum levels of web scraping depth (default: 2)
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
- GET `/api/clear_conversation`: to clear the conversations with ids
          
## Implementation Details

The system uses a simplified Retrieval Augmented Generation (RAG) approach with the following components:

- **Document Storage**: Stores processed document content as plain text for efficient retrieval and context building.
- **Text Processing**: Custom document processor extracts and chunks text from PDFs, DOCX, and TXT files in the assets folder.
- **Web Scraping**: Uses BeautifulSoup4 to recursively scrape and extract support content from the Angel One website, with configurable depth via environment variable.
- **LLM Integration**: Utilizes Google's Gemini Pro model to generate contextually relevant answers based on both document and web-scraped data.
- **Conversation Management**: Maintains conversation history for each user session, enabling context-aware responses.
- **API Endpoints**: Exposes endpoints for answering questions, clearing conversation history, and health checks via FastAPI.

## Future Improvements

- **Enhanced Text Processing**: Implement advanced chunking, summarization, and preprocessing for better context management.
- **Multi-Modal Support**: Add the ability to process and respond to image-based or tabular queries.
- **Caching Layer**: Introduce caching for frequently asked questions to improve response speed and reduce LLM calls.
- **Analytics Dashboard**: Develop a dashboard for monitoring usage, popular queries, and system performance.
- **Custom Training**: Fine-tune the LLM with domain-specific data for improved accuracy and relevance.
- **Vector Embeddings**: Optionally reintroduce semantic search using vector embeddings for large-scale document sets.
- **Multilingual Support**: Extend the system to support multiple languages for broader accessibility.

        
