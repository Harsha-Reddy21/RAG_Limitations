import os
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.document import Document

from db_utils import get_db_schema_string, execute_query, get_table_info

load_dotenv()

def create_document_from_db():
    """Create documents from database tables for RAG indexing."""
    # Get all data from database tables
    tables = ["customers", "orders", "products", "reviews", "support_tickets", "order_items"]
    documents = []
    
    for table in tables:
        query = f"SELECT * FROM {table}"
        results = execute_query(query)
        
        if results:
            # Convert each row to a document
            for row in results:
                # Convert row to string representation
                content = f"Table: {table}\n"
                for key, value in row.items():
                    content += f"{key}: {value}\n"
                
                # Create document
                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": table,
                            "row_id": row.get("customer_id") or row.get("order_id") or row.get("product_id") or row.get("review_id") or row.get("ticket_id") or row.get("order_item_id")
                        }
                    )
                )
    
    return documents

def create_vector_store():
    """Create and return a vector store from database content."""
    # Get documents
    documents = create_document_from_db()
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    # Split documents
    splits = text_splitter.split_documents(documents)
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vector_store

def initialize_rag_system():
    """Initialize and return a RAG system using LangChain."""
    # Create LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    
    # Create or load vector store
    vector_store = create_vector_store()
    
    # Create retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    
    # Get database schema
    schema = get_db_schema_string()
    
    # Create prompt template
    template = """You are a helpful assistant for an e-commerce customer support team.
    Use the following database schema information and retrieved context to answer the question.
    
    Database Schema:
    {schema}
    
    Retrieved context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Create RAG chain
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough(), "schema": lambda _: schema}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def query_with_rag(query):
    """Query the database using the RAG system."""
    rag_chain = initialize_rag_system()
    
    # Execute the RAG chain
    try:
        start_time = time.time()
        result = rag_chain.invoke(query)
        end_time = time.time()
        
        return {
            "query": query,
            "result": result,
            "time_taken": end_time - start_time,
            "success": True
        }
    except Exception as e:
        return {
            "query": query,
            "result": f"Error: {str(e)}",
            "success": False
        }

# Sample questions for benchmarking (same as SQL agent)
SAMPLE_QUESTIONS = [
    "How many orders does customer John Doe have?",
    "What is the average rating of products in the Electronics category?",
    "Which customer has the most open support tickets?",
    "What are the top 3 most expensive products?",
    "How many orders were delivered in the last month?",
    "What is the total revenue from all orders?",
    "Which product has received the highest rating?",
    "How many customers have made more than one order?",
    "What is the status of the support ticket for Jane Smith?",
    "Which products are currently out of stock?"
]

if __name__ == "__main__":
    # Example usage
    query = "How many orders does customer John Doe have?"
    result = query_with_rag(query)
    print(result) 