# RAG vs SQL Agent Comparison

This project compares two approaches for enabling natural language querying of a PostgreSQL database for an e-commerce customer support system:

1. **RAG (Retrieval-Augmented Generation)**: Converts database records into documents, creates embeddings, and uses vector similarity search to retrieve relevant context for answering queries.

2. **SQL Agent**: Uses LLM to translate natural language queries directly into SQL, executes the SQL against the database, and formats the results into natural language responses.

## Project Structure

```
├── .env.example           # Example environment variables
├── benchmark.py           # Benchmarking script for comparing approaches
├── db_utils.py            # Database utility functions
├── hybrid_approach.py     # Hybrid implementation combining RAG and SQL Agent
├── rag_system.py          # RAG implementation
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── setup_database.py      # Script to set up database with sample data
└── sql_agent.py           # SQL Agent implementation
```

## Setup Instructions

1. **Clone the repository**

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```
   cp .env.example .env
   ```
   Edit the `.env` file to add your OpenAI API key and database credentials.

4. **Set up the database**
   ```
   python setup_database.py
   ```
   This will create the necessary tables and populate them with sample data.

## Usage

### SQL Agent

```python
from sql_agent import query_with_sql_agent

result = query_with_sql_agent("How many orders does customer John Doe have?")
print(result["result"])
```

### RAG System

```python
from rag_system import query_with_rag

result = query_with_rag("How many orders does customer John Doe have?")
print(result["result"])
```

### Hybrid Approach

```python
from hybrid_approach import hybrid_query, enhanced_hybrid_query

# Simple classification-based hybrid approach
result = hybrid_query("How many orders does customer John Doe have?")
print(result["result"])

# Enhanced hybrid approach that combines SQL and RAG
result = enhanced_hybrid_query("How many orders does customer John Doe have?")
print(result.get("enhanced_response", result.get("result")))
```

## Running Benchmarks

To compare the performance of both approaches:

```
python benchmark.py
```

This will run a series of sample queries through both systems and generate a benchmark report.

## Key Findings

- **SQL Agent** excels at precise numerical queries, aggregations, and structured data operations.
- **RAG** excels at contextual understanding, narrative responses, and handling imprecise queries.
- A **hybrid approach** combining both methods provides the most comprehensive solution.

## Sample Questions

1. "How many orders does customer John Doe have?"
2. "What is the average rating of products in the Electronics category?"
3. "Which customer has the most open support tickets?"
4. "What are the top 3 most expensive products?"
5. "How many orders were delivered in the last month?"
6. "What is the total revenue from all orders?"
7. "Which product has received the highest rating?"
8. "How many customers have made more than one order?"
9. "What is the status of the support ticket for Jane Smith?"
10. "Which products are currently out of stock?" 