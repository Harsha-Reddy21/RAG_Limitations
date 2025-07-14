#!/usr/bin/env python3
"""
Run the Quick Commerce Deals application
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import streamlit
        import langchain
        import openai
        import pandas
        import sqlalchemy
        import dotenv
        import faker
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all required dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists with API key"""
    if not os.path.exists('.env'):
        print("Warning: .env file not found.")
        print("Creating .env file from .env.example...")
        
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as example_file:
                with open('.env', 'w') as env_file:
                    env_file.write(example_file.read())
            
            print(".env file created. Please edit it to add your OpenAI API key.")
        else:
            print("Error: .env.example file not found.")
            print("Please create a .env file with your OpenAI API key:")
            print("OPENAI_API_KEY=your_api_key_here")
        
        return False
    return True

def initialize_database():
    """Initialize the database if it doesn't exist"""
    if not os.path.exists('quick_commerce.db'):
        print("Database not found. Initializing...")
        try:
            from database import init_db, get_session, generate_dummy_data
            engine = init_db()
            session = get_session(engine)
            generate_dummy_data(session)
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    return True

def run_app():
    """Run the Streamlit app"""
    print("Starting Quick Commerce Deals app...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    """Main function"""
    print("Quick Commerce Deals")
    print("===================")
    
    if not check_dependencies():
        return
    
    if not check_env_file():
        return
    
    if not initialize_database():
        return
    
    run_app()

if __name__ == "__main__":
    main() 