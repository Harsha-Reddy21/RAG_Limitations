#!/usr/bin/env python3
"""
Initialize the database with tables and sample data
"""

from database import init_db, get_session, generate_dummy_data

def main():
    """Initialize the database"""
    print("Initializing database...")
    engine = init_db()
    session = get_session(engine)
    
    print("Generating sample data...")
    generate_dummy_data(session)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    main() 