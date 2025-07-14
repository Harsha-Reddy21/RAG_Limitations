
    # Performance Benchmark Report: RAG vs SQL Agent
    
    ## Summary Statistics
    
    | Metric | SQL Agent | Direct SQL | RAG |
    |--------|-----------|------------|-----|
    | Average Response Time (s) | 48.75 | 4.21 | 7.80 |
    | Success Rate (%) | 100.0 | 100.0 | 100.0 |
    | Fastest Approach Count | 0 | 10 | 0 |
    
    ## Detailed Results
    
    ### Question 1: How many orders does customer John Doe have?

- SQL Agent: 22.23s, Success: True
- Direct SQL: 2.01s, Success: True
- RAG: 8.89s, Success: True

### Question 2: What is the average rating of products in the Electronics category?

- SQL Agent: 34.03s, Success: True
- Direct SQL: 4.72s, Success: True
- RAG: 6.30s, Success: True

### Question 3: Which customer has the most open support tickets?

- SQL Agent: 54.12s, Success: True
- Direct SQL: 4.69s, Success: True
- RAG: 6.91s, Success: True

### Question 4: What are the top 3 most expensive products?

- SQL Agent: 50.62s, Success: True
- Direct SQL: 3.95s, Success: True
- RAG: 9.89s, Success: True

### Question 5: How many orders were delivered in the last month?

- SQL Agent: 50.30s, Success: True
- Direct SQL: 5.48s, Success: True
- RAG: 6.51s, Success: True

### Question 6: What is the total revenue from all orders?

- SQL Agent: 54.50s, Success: True
- Direct SQL: 4.25s, Success: True
- RAG: 9.88s, Success: True

### Question 7: Which product has received the highest rating?

- SQL Agent: 56.16s, Success: True
- Direct SQL: 5.24s, Success: True
- RAG: 6.21s, Success: True

### Question 8: How many customers have made more than one order?

- SQL Agent: 57.99s, Success: True
- Direct SQL: 4.78s, Success: True
- RAG: 7.81s, Success: True

### Question 9: What is the status of the support ticket for Jane Smith?

- SQL Agent: 56.03s, Success: True
- Direct SQL: 3.28s, Success: True
- RAG: 6.88s, Success: True

### Question 10: Which products are currently out of stock?

- SQL Agent: 51.52s, Success: True
- Direct SQL: 3.72s, Success: True
- RAG: 8.72s, Success: True

