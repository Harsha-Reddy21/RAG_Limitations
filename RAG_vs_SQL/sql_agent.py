import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from db_utils import get_db_schema_string, execute_query

load_dotenv()

def create_db_connection_string():
    """Create database connection string from environment variables."""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ecommerce")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def initialize_sql_agent():
    """Initialize and return a SQL agent using LangChain."""
    # Create LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    
    # Create SQLDatabase connection
    db_uri = create_db_connection_string()
    db = SQLDatabase.from_uri(db_uri)
    
    # Create SQL toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    # Create SQL agent
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        top_k=10,
        handle_parsing_errors=True
    )
    
    return agent_executor

def query_with_sql_agent(query):
    """Query the database using the SQL agent."""
    agent = initialize_sql_agent()
    
    # Add context about the database schema to help the agent
    schema_context = get_db_schema_string()
    full_query = f"""
    You are a helpful assistant for an e-commerce customer support team.
    Use the following database schema information to help answer the question:
    
    {schema_context}
    
    Question: {query}
    """
    
    # Execute the agent
    try:
        result = agent.invoke({"input": full_query})
        return {
            "query": query,
            "result": result["output"],
            "success": True
        }
    except Exception as e:
        return {
            "query": query,
            "result": f"Error: {str(e)}",
            "success": False
        }

def direct_sql_query(query_text):
    """Generate and execute SQL directly using LLM without agent framework."""
    # Create LLM
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    
    # Get database schema
    schema = get_db_schema_string()
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(
        """You are an expert SQL query generator.
        Given the following database schema and a question, generate a SQL query that answers the question.
        Return ONLY the SQL query, nothing else.
        
        Database Schema:
        {schema}
        
        Question: {question}
        
        SQL Query:"""
    )
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Generate SQL query
    try:
        sql_query = chain.invoke({"schema": schema, "question": query_text})
        
        # Execute the generated SQL query
        results = execute_query(sql_query)
        
        return {
            "query": query_text,
            "sql": sql_query,
            "results": results,
            "success": True
        }
    except Exception as e:
        return {
            "query": query_text,
            "error": str(e),
            "success": False
        }

# Sample questions for benchmarking
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
    result = query_with_sql_agent(query)
    print(result) 