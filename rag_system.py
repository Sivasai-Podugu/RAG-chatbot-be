from typing import Dict
from config import collection, model, documents_data
from document_processor import DocumentProcessor
import uuid

class RAGSystem:
    def __init__(self):
        # Initialize the complete context variable
        self.complete_context = ""
        # Dictionary to store conversation history: {conversation_id: [messages]}
        self.conversations = {}
        # Load knowledge base and context during initialization
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self):
        """Initialize the knowledge base by scraping and processing documents"""
        # Only initialize if the collection is empty
        if collection.count() == 0:
            print("Collection is empty. Scraping and processing documents...")
            DocumentProcessor.scrape_and_process_documents()
            print(f"Documents processed. Collection count: {collection.count()}")
        
        # Load all documents into the complete context
        self.load_complete_context()
    
    def load_complete_context(self):
        """Load all documents from the collection into the complete context"""
        try:
            # Get all documents from the collection
            results = collection.query(
                query_texts=["all"],  # Just a placeholder query
                n_results=collection.count()  # Get all documents
            )
            
            if results and results['documents'] and results['documents'][0]:
                # Join all documents into a single string
                self.complete_context = " ".join(results['documents'][0])
                print(f"Loaded {len(results['documents'][0])} documents into complete context")
            else:
                print("No documents found in collection")
        except Exception as e:
            print(f"Error loading complete context: {e}")
    
    def get_or_create_conversation(self, conversation_id=None):
        """Get an existing conversation or create a new one"""
        if conversation_id and conversation_id in self.conversations:
            return conversation_id, self.conversations[conversation_id]
        
        # Create a new conversation ID
        new_id = str(uuid.uuid4())
        self.conversations[new_id] = []
        return new_id, self.conversations[new_id]

    def clear_conversations(self, conversation_ids):
        """Clear multiple conversation histories"""
        results = {}
        for conversation_id in conversation_ids:
            if conversation_id in self.conversations:
                self.conversations[conversation_id] = []
                results[conversation_id] = True
            else:
                results[conversation_id] = False
        return results

    def answer_question(self, query: str, conversation_id=None) -> Dict:
        """Generate an answer using document data, webpage data, and conversation history"""
        try:
            # Get or create conversation history
            conv_id, conversation = self.get_or_create_conversation(conversation_id)
            
            # Add the user's question to the conversation history
            conversation.append({"role": "user", "content": query})
            
            # Check if we have any data to work with
            if not documents_data and not self.complete_context:
                answer = "I'm sorry, but I don't have enough information to answer your question about Angel One's services. Is there something else I can help you with?"
                conversation.append({"role": "assistant", "content": answer})
                return {"answer": answer, "conversation_id": conv_id}
            
            # Format conversation history for the prompt
            conversation_text = ""
            if conversation:
                conversation_text = "\n\nPrevious conversation:\n"
                for msg in conversation[:-1]:  # Exclude the current question
                    conversation_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            # Prepare the prompt with both data sources and conversation history
            prompt = f"""You are Angel, a friendly and helpful customer support assistant for Angel One, a trading and investment platform. 
            You should respond in a conversational, helpful tone as if you're chatting with a customer.
            
            Use the following knowledge sources to inform your answers, but respond naturally like a human customer service agent would.
            Don't mention that you're using "knowledge sources" or "information provided" - just incorporate the knowledge naturally.
            
            Document data: {documents_data}
            
            Webpage data: {self.complete_context}
            {conversation_text}
            
            Additionally, you have access to the Angel One support webpage: https://www.angelone.in/support
            
            Important guidelines:
            - First check if the answer is in the document data, then check webpage data
            - If you can't find the answer in any of the provided sources, clearly state that you don't have that specific information
            - Be concise and friendly in your responses
            - Use a conversational tone with occasional friendly phrases like "I'd be happy to help with that" or "Great question!"
            - If you're not 100% sure about something, say "Based on what I understand..." rather than "I don't know"
            - Personalize your responses by occasionally referring to the user's question
            - Offer to provide more information or help with related questions
            - Never make up information - if you truly don't know, say "I don't have that specific information right now, but I'd be happy to help you find out"
            - When appropriate, mention that users can find more details on the Angel One support page: https://www.angelone.in/support
            - NEVER include invalid URLs like 'https://www.angelone.in/support.\n\nIs' - always use the correct URL: https://www.angelone.in/support
            - When referring to the support page, use the exact URL: https://www.angelone.in/support (without any trailing periods or characters)
            - For questions about processes (like account creation, trading, etc.), always provide detailed step-by-step instructions with numbered steps
            - When explaining multi-step processes, include all necessary details like document requirements, verification steps, and timeframes
            - If the user is asking about creating an account, provide comprehensive steps from visiting the website to first login
            - Always mention important requirements like Aadhaar-mobile linking, document needs, and processing times
            - Format your responses with clear paragraph breaks and numbered steps for better readability
            - You are a customer support assistant for Angel One, so you should only answer questions related to Angel One's services and financial trading
            - If the user asks about topics unrelated to Angel One or financial trading (like sports, entertainment, politics, etc.), politely explain that you're an Angel One assistant and can only help with questions about Angel One's services and financial trading
            - IMPORTANT: If the user's question refers to previous messages in the conversation, make sure to use that context in your answer
            
            Customer question: {query}"""
            
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            # Add the assistant's response to the conversation history
            conversation.append({"role": "assistant", "content": answer})
            
            return {"answer": answer, "conversation_id": conv_id}
            
        except Exception as e:
            print(f"Error occurred while generating answer: {e}")
            error_msg = "I'm sorry, I encountered an error while processing your question. Please try again or contact our support team for assistance."
            
            # Add error response to conversation if it exists
            if conversation_id in self.conversations:
                self.conversations[conversation_id].append({"role": "assistant", "content": error_msg})
            
            return {"answer": error_msg, "conversation_id": conv_id if 'conv_id' in locals() else str(uuid.uuid4())}