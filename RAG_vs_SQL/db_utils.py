import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Create SQLAlchemy engine
def get_db_engine():
    """Create and return a SQLAlchemy engine for database connection."""
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_string)

# Create a session
def get_db_session():
    """Create and return a SQLAlchemy session."""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Get database schema information
def get_table_info():
    """Get table schema information as a dictionary."""
    engine = get_db_engine()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    table_info = {}
    for table_name, table in metadata.tables.items():
        columns = []
        for column in table.columns:
            column_info = {
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable
            }
            if column.primary_key:
                column_info["primary_key"] = True
            if column.foreign_keys:
                fk = next(iter(column.foreign_keys))
                column_info["foreign_key"] = str(fk.column)
            columns.append(column_info)
        
        table_info[table_name] = columns
    
    return table_info

# Get database schema as a string for LLM context
def get_db_schema_string():
    """Get the database schema as a formatted string for LLM context."""
    table_info = get_table_info()
    schema_str = "Database Schema:\n"
    
    for table_name, columns in table_info.items():
        schema_str += f"\nTable: {table_name}\n"
        for col in columns:
            schema_str += f"  - {col['name']} ({col['type']})"
            if col.get("primary_key"):
                schema_str += " PRIMARY KEY"
            if col.get("foreign_key"):
                schema_str += f" REFERENCES {col['foreign_key']}"
            schema_str += "\n"
    
    return schema_str

# Execute a raw SQL query
def execute_query(query, params=None):
    """Execute a raw SQL query and return results."""
    engine = get_db_engine()
    with engine.connect() as connection:
        if params:
            result = connection.execute(text(query), params)
        else:
            result = connection.execute(text(query))
        
        if result.returns_rows:
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        return None 