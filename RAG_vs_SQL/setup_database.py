import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# SQL statements to create tables
CREATE_TABLES = """
-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    stock_quantity INTEGER NOT NULL DEFAULT 0
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    shipping_address TEXT
);

-- Order items table (junction table for orders and products)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Support tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    subject VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
"""

# Sample data insertion
INSERT_SAMPLE_DATA = """
-- Insert sample customers
INSERT INTO customers (name, email, phone, address) VALUES
('John Doe', 'john@example.com', '555-123-4567', '123 Main St, Anytown, USA'),
('Jane Smith', 'jane@example.com', '555-234-5678', '456 Oak Ave, Somewhere, USA'),
('Bob Johnson', 'bob@example.com', '555-345-6789', '789 Pine Rd, Nowhere, USA'),
('Alice Brown', 'alice@example.com', '555-456-7890', '321 Maple Dr, Everywhere, USA'),
('Charlie Davis', 'charlie@example.com', '555-567-8901', '654 Birch Ln, Anywhere, USA');

-- Insert sample products
INSERT INTO products (name, description, price, category, stock_quantity) VALUES
('Smartphone X', 'Latest model with advanced features', 999.99, 'Electronics', 50),
('Laptop Pro', 'High-performance laptop for professionals', 1499.99, 'Electronics', 30),
('Wireless Headphones', 'Noise-cancelling wireless headphones', 199.99, 'Electronics', 100),
('Running Shoes', 'Comfortable shoes for runners', 89.99, 'Footwear', 200),
('Coffee Maker', 'Automatic coffee maker with timer', 59.99, 'Kitchen', 75);

-- Insert sample orders
INSERT INTO orders (customer_id, total_amount, status, shipping_address) VALUES
(1, 1199.98, 'delivered', '123 Main St, Anytown, USA'),
(2, 199.99, 'shipped', '456 Oak Ave, Somewhere, USA'),
(3, 1499.99, 'processing', '789 Pine Rd, Nowhere, USA'),
(4, 149.98, 'delivered', '321 Maple Dr, Everywhere, USA'),
(1, 59.99, 'cancelled', '123 Main St, Anytown, USA');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 999.99),
(1, 3, 1, 199.99),
(2, 3, 1, 199.99),
(3, 2, 1, 1499.99),
(4, 4, 1, 89.99),
(4, 5, 1, 59.99),
(5, 5, 1, 59.99);

-- Insert sample reviews
INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES
(1, 1, 5, 'Great smartphone, very fast and excellent camera!'),
(2, 3, 4, 'Good laptop, but battery life could be better'),
(3, 2, 5, 'Amazing sound quality and comfortable to wear'),
(4, 4, 3, 'Decent shoes, but not very durable'),
(5, 1, 4, 'Makes great coffee and easy to use');

-- Insert sample support tickets
INSERT INTO support_tickets (customer_id, subject, description, status) VALUES
(1, 'Order Delay', 'My order #1 is taking longer than expected', 'resolved'),
(2, 'Defective Product', 'The headphones I received have sound issues', 'open'),
(3, 'Refund Request', 'I would like to return my laptop and get a refund', 'in progress'),
(4, 'Account Access', 'I cannot log into my account', 'resolved'),
(5, 'Missing Item', 'My order was missing an item', 'open');
"""

def setup_database():
    """Set up the database with tables and sample data."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute(CREATE_TABLES)
        print("Tables created successfully")
        
        # Insert sample data
        cursor.execute(INSERT_SAMPLE_DATA)
        print("Sample data inserted successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    setup_database() 