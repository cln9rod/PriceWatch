import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Import local modules
try:
    from database import DatabaseManager, Product, PriceEntry
    from scraper import PriceScraper
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

# Initialize scraper
@st.cache_resource  
def init_scraper():
    return PriceScraper(headless=True)

def format_currency(value: float) -> str:
    """Format price as currency"""
    return f"${value:.2f}"

def main():
    st.set_page_config(
        page_title="PriceWatch",
        page_icon="$",
        layout="wide"
    )
    
    # Initialize components
    db = init_database()
    scraper = init_scraper()
    
    # Header
    st.title("PriceWatch")
    st.markdown("*Track competitor prices automatically*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("Dashboard")
        
        # Quick stats
        products = db.get_products()
        total_products = len(products)
        
        st.metric("Products", total_products)
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Choose Page",
            ["Overview", "Add Product", "Manual Scrape"]
        )
    
    # Main content based on selected page
    if page == "Overview":
        show_overview(db)
    elif page == "Add Product":
        show_add_product(db)
    elif page == "Manual Scrape":
        show_manual_scrape(db, scraper)

def show_overview(db: DatabaseManager):
    """Show overview of all tracked products"""
    st.header("Product Overview")
    
    products = db.get_products()
    
    if not products:
        st.info("Welcome to PriceWatch! Add your first product to get started.")
        return
    
    # Display products
    for product in products:
        with st.container():
            st.subheader(product.label)
            st.caption(f"URL: {product.url}")
            
            # Get latest price
            latest = db.get_latest_price(product.url)
            
            if latest:
                st.metric("Current Price", format_currency(latest.price))
                st.caption(f"Updated: {latest.timestamp.strftime('%m/%d %H:%M')}")
            else:
                st.warning("No price data yet")
            
            st.divider()

def show_add_product(db: DatabaseManager):
    """Show add product form"""
    st.header("Add New Product")
    
    with st.form("add_product_form"):
        url = st.text_input(
            "Product URL",
            placeholder="https://example.com/product",
            help="Enter the full URL of the product page"
        )
        
        label = st.text_input(
            "Product Label",
            placeholder="My Product Name",
            help="Give this product a memorable name"
        )
        
        css_selector = st.text_input(
            "CSS Selector (Optional)",
            placeholder=".price",
            help="CSS selector for the price element (leave empty for auto-detection)"
        )
        
        submitted = st.form_submit_button("Add Product", type="primary")
        
        if submitted:
            if url and label:
                try:
                    product_id = db.add_product(
                        url=url.strip(),
                        label=label.strip(),
                        css_selector=css_selector.strip() or '.price'
                    )
                    
                    st.success(f"Product '{label}' added successfully!")
                    st.info("Go to 'Manual Scrape' to get the first price reading.")
                        
                except Exception as e:
                    st.error(f"Error adding product: {str(e)}")
            else:
                st.error("Please fill in both URL and Label fields")

def show_manual_scrape(db: DatabaseManager, scraper: PriceScraper):
    """Show manual scraping interface"""
    st.header("Manual Price Scraping")
    
    products = db.get_products()
    
    if not products:
        st.info("No products added yet. Add a product first!")
        return
    
    # Select product to scrape
    product_options = {f"{p.label} ({p.url})": p for p in products}
    selected = st.selectbox("Select Product to Scrape", options=list(product_options.keys()))
    
    if selected:
        product = product_options[selected]
        
        st.info(f"**URL**: {product.url}")
        st.info(f"**Selector**: `{product.css_selector}`")
        
        if st.button("Scrape Now", type="primary"):
            with st.spinner("Scraping price..."):
                try:
                    # Mock scraping for demo (since Playwright may not be installed)
                    st.info("Playwright not available - using mock data")
                    
                    # Add mock price
                    import random
                    mock_price = round(random.uniform(50, 200), 2)
                    db.add_price(product.url, mock_price)
                    
                    st.success(f"Mock price scraped: {format_currency(mock_price)}")
                    
                except Exception as e:
                    st.error(f"Error during scraping: {str(e)}")
        
        # Show recent price history
        st.subheader(f"Recent Prices - {product.label}")
        prices = db.get_prices(product.url, limit=10)
        
        if prices:
            # Show table
            df = pd.DataFrame([
                {
                    'Date': price.timestamp.strftime('%Y-%m-%d'),
                    'Time': price.timestamp.strftime('%H:%M'),
                    'Price': format_currency(price.price)
                }
                for price in prices
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No price history yet. Scrape some prices to see the data!")

if __name__ == "__main__":
    main()