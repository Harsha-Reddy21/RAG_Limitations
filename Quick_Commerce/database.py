import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from faker import Faker
import random

# Create SQLAlchemy Base
Base = declarative_base()

# Define Models
class Platform(Base):
    __tablename__ = 'platforms'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    logo_url = Column(String(255))
    delivery_time_min = Column(Integer)
    delivery_time_max = Column(Integer)
    delivery_fee = Column(Float)
    min_order_value = Column(Float)
    
    # Relationships
    products = relationship("ProductPlatform", back_populates="platform")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category")
    parent = relationship("Category", remote_side=[id])

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    brand = Column(String(50))
    image_url = Column(String(255))
    category_id = Column(Integer, ForeignKey('categories.id'))
    base_unit = Column(String(20))  # e.g., kg, piece, dozen
    
    # Relationships
    category = relationship("Category", back_populates="products")
    platform_listings = relationship("ProductPlatform", back_populates="product")

class ProductPlatform(Base):
    __tablename__ = 'product_platforms'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0)
    discount_price = Column(Float)
    stock_available = Column(Boolean, default=True)
    quantity_available = Column(Integer)
    unit_size = Column(String(20))  # e.g., 500g, 1kg, 6 pieces
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="platform_listings")
    platform = relationship("Platform", back_populates="products")

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_platform_id = Column(Integer, ForeignKey('product_platforms.id'))
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float)
    discount_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    product_platform = relationship("ProductPlatform")

class UserSearch(Base):
    __tablename__ = 'user_searches'
    
    id = Column(Integer, primary_key=True)
    query = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    results_count = Column(Integer)

def init_db(db_path='quick_commerce.db'):
    """Initialize the database with tables"""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Create a session for database operations"""
    Session = sessionmaker(bind=engine)
    return Session()

def generate_dummy_data(session):
    """Generate dummy data for testing"""
    fake = Faker()
    
    # Create platforms
    platforms = [
        {"name": "Blinkit", "delivery_time_min": 10, "delivery_time_max": 20, "delivery_fee": 20, "min_order_value": 99},
        {"name": "Zepto", "delivery_time_min": 8, "delivery_time_max": 15, "delivery_fee": 25, "min_order_value": 149},
        {"name": "Instamart", "delivery_time_min": 15, "delivery_time_max": 30, "delivery_fee": 15, "min_order_value": 199},
        {"name": "BigBasket Now", "delivery_time_min": 20, "delivery_time_max": 40, "delivery_fee": 30, "min_order_value": 249}
    ]
    
    for p_data in platforms:
        platform = Platform(**p_data)
        session.add(platform)
    
    # Create categories
    main_categories = ["Fruits & Vegetables", "Dairy & Breakfast", "Snacks & Munchies", 
                      "Bakery & Biscuits", "Beverages", "Household", "Personal Care"]
    
    category_objects = {}
    
    for cat_name in main_categories:
        category = Category(name=cat_name)
        session.add(category)
        session.flush()
        category_objects[cat_name] = category
        
        # Add subcategories
        if cat_name == "Fruits & Vegetables":
            subcats = ["Fresh Fruits", "Fresh Vegetables", "Herbs & Seasonings"]
        elif cat_name == "Dairy & Breakfast":
            subcats = ["Milk", "Bread", "Eggs", "Cheese", "Butter"]
        else:
            subcats = [f"{cat_name} Subcat {i}" for i in range(1, 4)]
            
        for subcat in subcats:
            sub_category = Category(name=subcat, parent_id=category.id)
            session.add(sub_category)
            session.flush()
            category_objects[subcat] = sub_category
    
    # Create products
    products = {
        "Fresh Fruits": ["Apple", "Banana", "Orange", "Grapes", "Watermelon", "Mango"],
        "Fresh Vegetables": ["Onion", "Potato", "Tomato", "Cucumber", "Carrot", "Capsicum"],
        "Milk": ["Full Cream Milk", "Toned Milk", "Double Toned Milk", "Almond Milk"],
        "Bread": ["Brown Bread", "White Bread", "Multigrain Bread", "Garlic Bread"],
        "Snacks & Munchies Subcat 1": ["Potato Chips", "Nachos", "Popcorn", "Trail Mix"]
    }
    
    product_objects = []
    
    for category_name, product_list in products.items():
        category = category_objects.get(category_name)
        if not category:
            continue
            
        for product_name in product_list:
            product = Product(
                name=product_name,
                description=fake.text(max_nb_chars=100),
                brand=fake.company(),
                image_url=f"https://example.com/images/{product_name.lower().replace(' ', '_')}.jpg",
                category_id=category.id,
                base_unit="kg" if category_name in ["Fresh Fruits", "Fresh Vegetables"] else "piece"
            )
            session.add(product)
            product_objects.append(product)
    
    session.commit()
    
    # Create product platform entries with pricing
    platforms = session.query(Platform).all()
    products = session.query(Product).all()
    
    for product in products:
        for platform in platforms:
            base_price = round(random.uniform(20, 500), 2)
            discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30])
            discount_price = round(base_price * (1 - discount_pct/100), 2) if discount_pct > 0 else None
            
            product_platform = ProductPlatform(
                product_id=product.id,
                platform_id=platform.id,
                price=base_price,
                discount_percentage=discount_pct,
                discount_price=discount_price,
                stock_available=random.choice([True, True, True, False]),
                quantity_available=random.randint(0, 100) if random.random() > 0.1 else 0,
                unit_size=f"{random.choice(['250g', '500g', '1kg', '2kg'])}" if product.base_unit == "kg" else 
                          f"{random.choice([1, 6, 12])} {product.base_unit}s",
                last_updated=datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 72))
            )
            session.add(product_platform)
            
            # Add some price history
            for days_ago in range(1, 8):
                hist_price = round(base_price * random.uniform(0.9, 1.1), 2)
                hist_discount = random.choice([0, 0, 0, 5, 10, 15, 20])
                hist_discount_price = round(hist_price * (1 - hist_discount/100), 2) if hist_discount > 0 else None
                
                price_history = PriceHistory(
                    product_platform_id=product_platform.id,
                    price=hist_price,
                    discount_percentage=hist_discount,
                    discount_price=hist_discount_price,
                    timestamp=datetime.datetime.now() - datetime.timedelta(days=days_ago)
                )
                session.add(price_history)
    
    session.commit()

def update_random_prices(session):
    """Update random product prices to simulate real-time updates"""
    product_platforms = session.query(ProductPlatform).order_by(
        ProductPlatform.last_updated).limit(10).all()
    
    for pp in product_platforms:
        # Record old price in history
        price_history = PriceHistory(
            product_platform_id=pp.id,
            price=pp.price,
            discount_percentage=pp.discount_percentage,
            discount_price=pp.discount_price
        )
        session.add(price_history)
        
        # Update price (randomly up or down by up to 10%)
        price_change = random.uniform(-0.1, 0.1)
        pp.price = round(pp.price * (1 + price_change), 2)
        
        # Update discount
        pp.discount_percentage = random.choice([0, 0, 5, 10, 15, 20, 25, 30])
        if pp.discount_percentage > 0:
            pp.discount_price = round(pp.price * (1 - pp.discount_percentage/100), 2)
        else:
            pp.discount_price = None
        
        # Update stock
        pp.stock_available = random.choice([True, True, True, False])
        pp.quantity_available = random.randint(0, 100) if pp.stock_available else 0
        pp.last_updated = datetime.datetime.utcnow()
    
    session.commit()

if __name__ == "__main__":
    engine = init_db()
    session = get_session(engine)
    generate_dummy_data(session)
    print("Database initialized with dummy data!") 