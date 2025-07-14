import os
from typing import List, Dict, Any, Optional
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_community.utilities.sql_database import SQLDatabase as CommunitySQLDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
import pandas as pd
import sqlite3
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cache for query results and schema
QUERY_CACHE = {}
SCHEMA_CACHE = None
SCHEMA_TABLES_CACHE = {}
EMBEDDING_MODEL = None
TABLE_VECTOR_STORE = None

def get_db_connection(db_path='quick_commerce.db'):
    """Get SQLite database connection"""
    return sqlite3.connect(db_path)

def get_sql_database(db_path='quick_commerce.db'):
    """Get LangChain SQLDatabase object"""
    db_uri = f"sqlite:///{db_path}"
    return SQLDatabase.from_uri(db_uri)

def get_community_sql_database(db_path='quick_commerce.db'):
    """Get LangChain Community SQLDatabase object"""
    db_uri = f"sqlite:///{db_path}"
    return CommunitySQLDatabase.from_uri(db_uri)

def get_table_info(db_path='quick_commerce.db') -> str:
    """Get database schema information"""
    global SCHEMA_CACHE
    
    if SCHEMA_CACHE is not None:
        return SCHEMA_CACHE
    
    db = get_sql_database(db_path)
    SCHEMA_CACHE = db.get_table_info()
    return SCHEMA_CACHE

def get_table_definitions(db_path='quick_commerce.db') -> Dict[str, str]:
    """Get individual table definitions"""
    global SCHEMA_TABLES_CACHE
    
    if SCHEMA_TABLES_CACHE:
        return SCHEMA_TABLES_CACHE
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    table_definitions = {}
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        definition = f"CREATE TABLE {table_name} (\n"
        col_definitions = []
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] == 1 else ""
            primary_key = "PRIMARY KEY" if col[5] == 1 else ""
            
            col_def = f"  {col_name} {col_type} {not_null} {primary_key}".strip()
            col_definitions.append(col_def)
        
        definition += ",\n".join(col_definitions)
        definition += "\n);"
        
        table_definitions[table_name] = definition
    
    conn.close()
    SCHEMA_TABLES_CACHE = table_definitions
    return table_definitions

def initialize_embeddings_and_vectorstore(db_path='quick_commerce.db'):
    """Initialize embeddings model and vector store for table selection"""
    global EMBEDDING_MODEL, TABLE_VECTOR_STORE
    
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = OpenAIEmbeddings()
    
    if TABLE_VECTOR_STORE is None:
        # Get table definitions
        table_defs = get_table_definitions(db_path)
        
        # Create documents for each table
        documents = []
        for table_name, definition in table_defs.items():
            doc = Document(
                page_content=definition,
                metadata={"table_name": table_name}
            )
            documents.append(doc)
        
        # Create vector store
        TABLE_VECTOR_STORE = FAISS.from_documents(documents, EMBEDDING_MODEL)

def select_relevant_tables(query: str, top_k: int = 3) -> List[str]:
    """Select the most relevant tables for a given query using semantic search"""
    global TABLE_VECTOR_STORE
    
    if TABLE_VECTOR_STORE is None:
        initialize_embeddings_and_vectorstore()
    
    # Search for relevant tables
    results = TABLE_VECTOR_STORE.similarity_search(query, k=top_k)
    
    # Extract table names
    relevant_tables = [doc.metadata["table_name"] for doc in results]
    return relevant_tables

def get_optimized_schema_for_query(query: str, db_path='quick_commerce.db') -> str:
    """Get optimized schema information for a specific query"""
    # Select relevant tables
    relevant_tables = select_relevant_tables(query)
    
    # Get full table definitions
    table_defs = get_table_definitions(db_path)
    
    # Create optimized schema string with only relevant tables
    optimized_schema = ""
    for table in relevant_tables:
        if table in table_defs:
            optimized_schema += table_defs[table] + "\n\n"
    
    return optimized_schema

def execute_query(query: str, db_path='quick_commerce.db') -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame"""
    # Check cache first
    cache_key = hash(query)
    if cache_key in QUERY_CACHE:
        cache_entry = QUERY_CACHE[cache_key]
        # If cache is less than 30 seconds old, use it
        if time.time() - cache_entry["timestamp"] < 30:
            return cache_entry["data"]
    
    conn = get_db_connection(db_path)
    result = pd.read_sql_query(query, conn)
    conn.close()
    
    # Update cache
    QUERY_CACHE[cache_key] = {
        "data": result,
        "timestamp": time.time()
    }
    
    return result

def create_sql_query_agent(db_path='quick_commerce.db', temperature=0):
    """Create a LangChain SQL agent for handling natural language queries"""
    # Get database
    db = get_sql_database(db_path)
    
    # Create LLM
    llm = ChatOpenAI(temperature=temperature, model="gpt-3.5-turbo")
    
    # Create toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    # Create agent with memory
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="openai-tools",
        memory=memory,
        max_iterations=5
    )
    
    return agent_executor

def analyze_query_complexity(query: str) -> Dict[str, Any]:
    """Analyze the complexity of a natural language query"""
    complexity_metrics = {
        "estimated_tables_needed": 0,
        "requires_joins": False,
        "requires_aggregation": False,
        "requires_sorting": False,
        "requires_filtering": False,
        "complexity_score": 0
    }
    
    # Check for indicators of joins
    join_indicators = ["compare", "between", "across", "versus", "vs", "relation", "related"]
    if any(indicator in query.lower() for indicator in join_indicators):
        complexity_metrics["requires_joins"] = True
        complexity_metrics["complexity_score"] += 2
        complexity_metrics["estimated_tables_needed"] += 2
    
    # Check for indicators of aggregation
    agg_indicators = ["average", "total", "sum", "count", "minimum", "maximum", "cheapest", "most expensive", "best"]
    if any(indicator in query.lower() for indicator in agg_indicators):
        complexity_metrics["requires_aggregation"] = True
        complexity_metrics["complexity_score"] += 1
    
    # Check for indicators of sorting
    sort_indicators = ["order", "sort", "cheapest", "best", "highest", "lowest", "top", "bottom"]
    if any(indicator in query.lower() for indicator in sort_indicators):
        complexity_metrics["requires_sorting"] = True
        complexity_metrics["complexity_score"] += 1
    
    # Check for indicators of filtering
    filter_indicators = ["where", "with", "only", "just", "specific", "particular"]
    if any(indicator in query.lower() for indicator in filter_indicators):
        complexity_metrics["requires_filtering"] = True
        complexity_metrics["complexity_score"] += 1
    
    # Estimate tables needed based on entities mentioned
    entities = ["product", "price", "discount", "platform", "category", "brand", "history"]
    for entity in entities:
        if entity in query.lower():
            complexity_metrics["estimated_tables_needed"] += 1
    
    # Ensure at least one table is needed
    if complexity_metrics["estimated_tables_needed"] == 0:
        complexity_metrics["estimated_tables_needed"] = 1
    
    return complexity_metrics

def process_natural_language_query(query: str, db_path='quick_commerce.db'):
    """Process a natural language query and return results"""
    # Analyze query complexity
    complexity = analyze_query_complexity(query)
    
    # Get optimized schema
    optimized_schema = get_optimized_schema_for_query(query, db_path)
    
    # Create agent with the optimized schema
    agent = create_sql_query_agent(db_path)
    
    # Run agent
    try:
        result = agent.invoke({"input": query})
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test the agent
    query = "Which app has the cheapest onions right now?"
    result = process_natural_language_query(query)
    print(result) 