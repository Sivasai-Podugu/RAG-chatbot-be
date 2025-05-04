import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List

# Load environment variables
load_dotenv()

# Initialize Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Store the model name as a string instead of initializing SentenceTransformer
sentence_transformer_model = 'all-MiniLM-L6-v2'

# Store documents as a string instead of using ChromaDB collection
documents_data = ""

# Store collection documents as a list of strings
collection_documents = []

# Function to add documents to the collection_documents list
def add_to_collection(documents, ids=None):
    """Add documents to the collection_documents list"""
    global collection_documents
    collection_documents.extend(documents)
    return {"count": len(collection_documents)}

# Create a mock collection object with the necessary methods
class MockCollection:
    def __init__(self):
        pass
        
    def count(self):
        """Return the number of documents in the collection"""
        return len(collection_documents)
        
    def add(self, documents, ids=None):
        """Add documents to the collection"""
        return add_to_collection(documents, ids)
        
    def get(self):
        """Query the collection"""
        return {
            "documents": [collection_documents] if collection_documents else [[]]
        }

# Create a mock collection object
collection = MockCollection()

# Function to update documents_data
def update_documents_data(new_data):
    """Update the documents_data variable with new data"""
    global documents_data
    documents_data = new_data