#!/usr/bin/env python3
"""
Test the SQL agent with sample queries
"""

import os
from dotenv import load_dotenv
from sql_agent import process_natural_language_query, get_db_connection
from database import init_db, get_session, generate_dummy_data

# Load environment variables
load_dotenv()

def test_query(query):
    """Test a natural language query"""
    print(f"\nTesting query: '{query}'")
    print("-" * 50)
    
    result = process_natural_language_query(query)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        if "output" in result:
            print(result["output"])
        else:
            print(result)
    
    print("-" * 50)

def main():
    """Main function"""
    # Check if database exists
    if not os.path.exists('quick_commerce.db'):
        print("Database not found. Initializing...")
        engine = init_db()
        session = get_session(engine)
        generate_dummy_data(session)
        print("Database initialized!")
    
    # Test sample queries
    sample_queries = [
        "Which app has cheapest onions right now?",
        "Show products with 30%+ discount on Blinkit",
        "Compare fruit prices between Zepto and Instamart",
        "Find best deals for grocery items",
        "What's the average price of milk across all platforms?",
        "Which platform has the most products on discount?",
        "List all vegetables that are out of stock"
    ]
    
    for query in sample_queries:
        test_query(query)

if __name__ == "__main__":
    main() 