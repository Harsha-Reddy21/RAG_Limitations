# Quick Commerce Deals

A price comparison platform for quick commerce apps (Blinkit, Zepto, Instamart, BigBasket Now, etc.) that tracks real-time pricing, discounts, and availability across multiple platforms for thousands of products using natural language queries.

## Features

- **Natural Language Queries**: Ask questions like "Which app has cheapest onions right now?" using LangChain
- **Real-time Price Tracking**: Simulated real-time price updates across platforms
- **Intelligent Table Selection**: Uses semantic search with FAISS and OpenAI embeddings
- **Performance Optimization**: Includes caching strategies and query optimization
- **Interactive Dashboard**: Streamlit-based UI with platform statistics and top discounts

## Technical Implementation

- **Database Design**: Comprehensive schema for products, prices, discounts, availability, and platform data
- **LangChain Integration**: Uses LangChain for natural language processing and SQL agent
- **Semantic Indexing**: Intelligent table selection from multiple tables
- **Query Planning**: Optimal join path determination and query complexity analysis
- **Streamlit Web Interface**: Interactive UI for querying and data visualization
- **Rate Limiting**: Basic security with configurable request limits

## Quick Start

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```
   python run.py
   ```
   or
   ```
   streamlit run app.py
   ```
5. Open your browser and navigate to http://localhost:8501

## Sample Queries

- "Which app has cheapest onions right now?"
- "Show products with 30%+ discount on Blinkit"
- "Compare fruit prices between Zepto and Instamart"
- "Find best deals for grocery items"
- "What's the average price of milk across all platforms?"
- "Which platform has the most products on discount?"

## Project Structure

- `app.py`: Main Streamlit application with UI components
- `database.py`: Database schema and data generation functions
- `sql_agent.py`: LangChain SQL agent for natural language processing
- `rate_limiter.py`: Token bucket algorithm for basic security
- `run.py`: Helper script to run the application
- `init_db.py`: Script to initialize the database with sample data
- `test_sql_agent.py`: Test script for the SQL agent
- `ARCHITECTURE.md`: Detailed system architecture documentation
- `requirements.txt`: Project dependencies

## Architecture

The system follows a layered architecture:

1. **Presentation Layer**: Streamlit web interface
2. **Application Layer**: LangChain integration, query processing
3. **Data Access Layer**: Database interaction, caching
4. **Data Storage Layer**: SQLite database

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Database Schema

- **platforms**: Information about quick commerce platforms
- **categories**: Product categories and subcategories
- **products**: Product information
- **product_platforms**: Product listings with pricing and availability
- **price_history**: Historical price data
- **user_searches**: Log of user queries

## Future Enhancements

- User authentication and personalized recommendations
- Price history visualization and trend analysis
- Integration with actual quick commerce APIs
- Advanced analytics and price prediction
- Mobile app development 