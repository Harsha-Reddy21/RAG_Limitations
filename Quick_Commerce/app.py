import streamlit as st
import pandas as pd
import time
import threading
import sqlite3
import os
import uuid
from dotenv import load_dotenv
from database import init_db, get_session, generate_dummy_data, update_random_prices
from sql_agent import process_natural_language_query, get_db_connection, execute_query
from rate_limiter import check_rate_limit
import re

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Quick Commerce Deals",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False
if 'update_thread' not in st.session_state:
    st.session_state.update_thread = None
if 'update_running' not in st.session_state:
    st.session_state.update_running = False
if 'client_id' not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())  # Generate unique client ID for rate limiting

def price_updater(session, interval=10):
    """Background thread to update prices periodically"""
    while st.session_state.update_running:
        update_random_prices(session)
        time.sleep(interval)

def initialize_database():
    """Initialize the database with tables and sample data"""
    if not st.session_state.db_initialized:
        with st.spinner("Initializing database..."):
            if not os.path.exists('quick_commerce.db'):
                engine = init_db()
                session = get_session(engine)
                generate_dummy_data(session)
                st.session_state.db_initialized = True
                
                # Start price updater thread
                if not st.session_state.update_running:
                    st.session_state.update_running = True
                    st.session_state.update_thread = threading.Thread(
                        target=price_updater, 
                        args=(session,)
                    )
                    st.session_state.update_thread.daemon = True
                    st.session_state.update_thread.start()
                
                st.success("Database initialized with sample data!")
            else:
                st.session_state.db_initialized = True
                st.success("Database already exists!")

def get_platform_stats():
    """Get statistics about platforms"""
    conn = get_db_connection()
    query = """
    SELECT p.name, 
           COUNT(pp.id) as product_count,
           ROUND(AVG(pp.price), 2) as avg_price,
           ROUND(AVG(pp.discount_percentage), 2) as avg_discount
    FROM platforms p
    JOIN product_platforms pp ON p.id = pp.platform_id
    GROUP BY p.name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_category_stats():
    """Get statistics about categories"""
    conn = get_db_connection()
    query = """
    SELECT c.name, 
           COUNT(p.id) as product_count
    FROM categories c
    JOIN products p ON c.id = p.category_id
    GROUP BY c.name
    ORDER BY product_count DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_top_discounts():
    """Get products with top discounts"""
    conn = get_db_connection()
    query = """
    SELECT p.name as product, 
           pl.name as platform,
           pp.price as original_price,
           pp.discount_percentage,
           pp.discount_price as final_price
    FROM product_platforms pp
    JOIN products p ON pp.product_id = p.id
    JOIN platforms pl ON pp.platform_id = pl.id
    WHERE pp.discount_percentage > 0
    ORDER BY pp.discount_percentage DESC
    LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def display_dashboard():
    """Display the dashboard with key metrics"""
    st.header("Quick Commerce Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Platform Statistics")
        platform_stats = get_platform_stats()
        st.dataframe(platform_stats, use_container_width=True)
        
    with col2:
        st.subheader("Top Categories")
        category_stats = get_category_stats()
        st.dataframe(category_stats, use_container_width=True)
    
    st.subheader("Top Discounts Right Now")
    top_discounts = get_top_discounts()
    st.dataframe(top_discounts, use_container_width=True)

def display_query_interface():
    """Display the natural language query interface"""
    st.header("Ask about Products & Deals")
    
    # Sample queries
    st.markdown("### Sample Queries")
    sample_queries = [
        "Which app has cheapest onions right now?",
        "Show products with 30%+ discount on Blinkit",
        "Compare fruit prices between Zepto and Instamart",
        "Find best deals for grocery items"
    ]
    
    cols = st.columns(len(sample_queries))
    for i, query in enumerate(sample_queries):
        if cols[i].button(query):
            st.session_state.query = query
    
    # Query input
    query = st.text_input("Enter your query:", key="query")
    
    if st.button("Search") and query:
        # Check rate limit
        is_allowed, wait_time = check_rate_limit(st.session_state.client_id)
        
        if not is_allowed:
            st.warning(f"Rate limit exceeded. Please try again in {wait_time:.1f} seconds.")
        else:
            with st.spinner("Processing your query..."):
                # Add to history
                if query not in st.session_state.query_history:
                    st.session_state.query_history.append(query)
                
                # Process query
                result = process_natural_language_query(query)
                
                # Display result
                st.subheader("Results")
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                if "output" in result and isinstance(result["output"], str):
                    st.write(result["output"])
                    
                    # Try to extract any SQL and execute it to show as dataframe
                    sql_pattern = r"```sql\s*(.*?)\s*```"
                    sql_matches = re.findall(sql_pattern, result["output"], re.DOTALL)
                    
                    if sql_matches:
                        sql = sql_matches[0].strip()
                        try:
                            df = execute_query(sql)
                            st.dataframe(df, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not execute extracted SQL: {str(e)}")
                else:
                    st.json(result)

def display_sidebar():
    """Display the sidebar with options"""
    st.sidebar.title("Quick Commerce Deals")
    st.sidebar.image("https://img.icons8.com/color/96/000000/shop.png", width=100)
    
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Query Interface"])
    
    st.sidebar.header("Database")
    if st.sidebar.button("Initialize Database"):
        initialize_database()
    
    if st.session_state.db_initialized and st.sidebar.button("Update Prices"):
        with st.spinner("Updating random prices..."):
            engine = init_db()
            session = get_session(engine)
            update_random_prices(session)
            st.sidebar.success("Prices updated!")
    
    st.sidebar.header("Recent Queries")
    for q in st.session_state.query_history[-5:]:
        if st.sidebar.button(q, key=f"history_{q}"):
            st.session_state.query = q
    
    return page

def main():
    """Main function to run the Streamlit app"""
    # Check if database exists, if not initialize
    if not os.path.exists('quick_commerce.db'):
        initialize_database()
    else:
        st.session_state.db_initialized = True
    
    # Display sidebar and get selected page
    page = display_sidebar()
    
    # Display selected page
    if page == "Dashboard":
        display_dashboard()
    else:
        display_query_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("Quick Commerce Deals - Price Comparison Platform")

if __name__ == "__main__":
    main() 