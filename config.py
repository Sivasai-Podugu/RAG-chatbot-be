import os
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from typing import List

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize sentence transformer for embeddings
sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')

# Custom embedding function using sentence-transformers
class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, texts: List[str]) -> List[List[float]]:
        return sentence_transformer.encode(texts).tolist()

# Initialize ChromaDB
chroma_client = chromadb.Client()
custom_ef = CustomEmbeddingFunction()

# Create or get the collection
collection = chroma_client.get_or_create_collection(
    name="angel_one_docs",
    embedding_function=custom_ef
)

documents_data = "";