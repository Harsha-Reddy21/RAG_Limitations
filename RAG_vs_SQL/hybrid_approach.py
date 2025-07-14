import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from sql_agent import query_with_sql_agent, direct_sql_query
from rag_system import query_with_rag

load_dotenv()

def classify_query(query):
    """Classify a query as better suited for SQL Agent or RAG."""
    # Create LLM
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(
        """You are a query classifier that determines whether a natural language query is better suited for:
        
        1. SQL Agent: Queries requiring precise calculations, aggregations, exact counts, or structured data operations
        2. RAG (Retrieval Augmented Generation): Queries requiring context understanding, narrative responses, or inference from text
        
        Examples of SQL Agent queries:
        - "How many orders does customer John Doe have?"
        - "What is the average rating of products in Electronics category?"
        - "List all customers with open support tickets"
        
        Examples of RAG queries:
        - "Why did customer Jane Smith contact support recently?"
        - "What kinds of issues are customers having with headphones?"
        - "Summarize John's purchase history and preferences"
        
        For the following query, respond with ONLY "sql" or "rag" (lowercase):
        
        Query: {query}
        
        Classification:"""
    )
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Classify query
    classification = chain.invoke({"query": query}).strip().lower()
    
    # Ensure valid classification
    if classification not in ["sql", "rag"]:
        # Default to SQL if classification is unclear
        classification = "sql"
    
    return classification

def hybrid_query(query):
    """Process a query using the appropriate approach (SQL Agent or RAG)."""
    # Classify the query
    classification = classify_query(query)
    
    # Process with appropriate system
    if classification == "sql":
        result = query_with_sql_agent(query)
        approach = "SQL Agent"
    else:
        result = query_with_rag(query)
        approach = "RAG"
    
    # Add classification to result
    result["classification"] = classification
    result["approach_used"] = approach
    
    return result

def enhanced_hybrid_query(query):
    """Enhanced hybrid approach that uses both systems and combines results."""
    # Get SQL Agent result
    sql_result = direct_sql_query(query)
    
    # If SQL query was successful, use RAG to enhance the response
    if sql_result.get("success", False):
        # Convert SQL results to context
        sql_context = "SQL Query Results:\n"
        if isinstance(sql_result.get("results"), list):
            for i, row in enumerate(sql_result["results"]):
                sql_context += f"Row {i+1}: {row}\n"
        
        # Create LLM
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_template(
            """You are a helpful assistant for an e-commerce customer support team.
            Use the following SQL query results to answer the question.
            If the SQL results don't fully answer the question, indicate what additional information might be needed.
            
            SQL Query: {sql_query}
            
            SQL Results:
            {sql_context}
            
            Question: {question}
            
            Answer:"""
        )
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Generate enhanced response
        enhanced_response = chain.invoke({
            "sql_query": sql_result.get("sql", ""),
            "sql_context": sql_context,
            "question": query
        })
        
        return {
            "query": query,
            "sql_result": sql_result.get("results"),
            "enhanced_response": enhanced_response,
            "approach": "hybrid (SQL + enhancement)",
            "success": True
        }
    else:
        # Fall back to RAG if SQL failed
        rag_result = query_with_rag(query)
        return {
            "query": query,
            "result": rag_result.get("result"),
            "approach": "hybrid (fallback to RAG)",
            "success": rag_result.get("success", False)
        }

# Sample questions for testing
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
    
    print("Simple Hybrid Approach (Classification):")
    result = hybrid_query(query)
    print(f"Classification: {result['classification']}")
    print(f"Result: {result['result']}")
    print()
    
    print("Enhanced Hybrid Approach (SQL + RAG):")
    result = enhanced_hybrid_query(query)
    print(f"Approach: {result['approach']}")
    if "enhanced_response" in result:
        print(f"Enhanced Response: {result['enhanced_response']}")
    else:
        print(f"Result: {result['result']}") 