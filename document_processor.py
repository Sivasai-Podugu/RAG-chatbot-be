import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
from typing import List
from config import collection, update_documents_data
import time
import docx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""

    @staticmethod
    def process_documents() -> List[str]:
        """Process documents from the assets folder including PDF, TXT, and DOCX files"""
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        if not os.path.exists(assets_dir):
            return []

        documents = []
        for filename in os.listdir(assets_dir):
            file_path = os.path.join(assets_dir, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Process based on file extension
            if file_extension == '.pdf':
                text = DocumentProcessor.extract_text_from_pdf(file_path)
            elif file_extension == '.txt':
                text = DocumentProcessor.extract_text_from_txt(file_path)
            elif file_extension == '.docx':
                text = DocumentProcessor.extract_text_from_docx(file_path)
            else:
                # Skip unsupported file types
                continue
                
            if text:
                # Split text into smaller chunks
                chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
                documents.extend(chunks)
        return documents
    
    @staticmethod
    def extract_text_from_txt(txt_path: str) -> str:
        """Extract text from a TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT {txt_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(docx_path: str) -> str:
        """Extract text from a DOCX file"""
        try:
            doc = docx.Document(docx_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except ImportError:
            print("python-docx module not installed. Please install it with: pip install python-docx")
            return ""
        except Exception as e:
            print(f"Error reading DOCX {docx_path}: {e}")
            return ""

    @staticmethod
    def scrape_and_process_documents():
        """Scrape the Angel One support website and process documents"""
        base_url = "https://www.angelone.in/support"
        
        documents = []
        try:
            # Scrape main page first
            documents.extend(DocumentProcessor.scrape_page(base_url))
            
            # Find and scrape all linked pages recursively up to the specified levels deep
            visited_urls = set([base_url])
            urls_to_visit = set(DocumentProcessor.find_sub_pages(base_url))
            
            # Track the current level of recursion
            current_level = 1
            # Get max_levels from environment variable, default to 5 if not set
            max_levels = int(os.getenv("MAX_SCRAPE_LEVELS", 5))
            
            print(f"Will scrape up to {max_levels} levels deep")
            
            while urls_to_visit and current_level <= max_levels:
                print(f"Scraping level {current_level} with {len(urls_to_visit)} URLs to visit")
                
                # Get URLs for the current level
                current_urls = urls_to_visit.copy()
                urls_to_visit = set()
                
                for page_url in current_urls:
                    if page_url not in visited_urls:
                        # Add a small delay to avoid overwhelming the server
                        time.sleep(0.5)
                        
                        # Scrape the page content
                        page_documents = DocumentProcessor.scrape_page(page_url)
                        documents.extend(page_documents)
                        
                        # Mark as visited
                        visited_urls.add(page_url)
                        
                        # Find new sub-pages to visit in the next level
                        new_urls = DocumentProcessor.find_sub_pages(page_url)
                        for url in new_urls:
                            if url not in visited_urls:
                                urls_to_visit.add(url)
                
                # Move to the next level
                current_level += 1
            
            print(f"Scraped a total of {len(visited_urls)} pages across {current_level-1} levels")
            
            # Process documents (PDF, TXT, DOCX)
            local_documents = DocumentProcessor.process_documents()
            
            # Add local documents to documents_data in config.py
            if local_documents:
                # Join all document chunks into a single string
                local_docs_text = " ".join(local_documents)
                # Update the documents_data variable using the function
                update_documents_data(local_docs_text)
                print(f"Added {len(local_documents)} local document chunks to documents_data")
            
            # Add web-scraped documents to collection
            if documents:
                collection.add(
                    documents=documents,
                    ids=[f"doc_{i}" for i in range(len(documents))]
                )
                print(f"Added {len(documents)} web-scraped documents to collection")
            
        except Exception as e:
            print(f"Error processing documents: {e}")
            DocumentProcessor.add_fallback_content()

    @staticmethod
    def scrape_page(url: str) -> List[str]:
        """Scrape a single page and extract text content"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from relevant sections
            content_sections = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'div.content'])
            
            documents = []
            for section in content_sections:
                text = section.get_text().strip()
                if text and len(text) > 20:  # Filter out very short texts
                    documents.append(text)
            
            return documents
        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            return []

    @staticmethod
    def find_sub_pages(url: str) -> List[str]:
        """Find all sub-pages linked from the given URL"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            # Extract and filter relevant links
            sub_pages = set()
            base_domain = url.split('/')[2]  # e.g., www.angelone.in
            
            for link in links:
                href = link['href']
                
                # Handle relative URLs
                if href.startswith('/'):
                    href = f"https://{base_domain}{href}"
                
                # Only include links from the same domain and support-related pages
                if base_domain in href and '/support' in href:
                    sub_pages.add(href)
            
            return list(sub_pages)
        except Exception as e:
            print(f"Error finding sub-pages from {url}: {e}")
            return []

    @staticmethod
    def add_fallback_content():
        """Add fallback content to the collection"""
        collection.add(
            documents=[
                "Angel One offers online trading services.",
                "Trading hours for NSE and BSE are 9:15 AM to 3:30 PM.",
                "You can open a demat account through our website."
            ],
            ids=["doc_1", "doc_2", "doc_3"]
        )