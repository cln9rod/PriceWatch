import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import asyncio
from typing import List, Dict

# Import local modules
from database import DatabaseManager, Product, PriceEntry
from scraper import PriceScraper

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

def format_percentage(value: float) -> str:
    """Format percentage with color"""
    color = "green" if value < 0 else "red" if value > 0 else "gray"
    symbol = "=É" if value < 0 else "=È" if value > 0 else "–"
    return f":{color}[{symbol} {value:.1f}%]"

def create_price_chart(prices: List[PriceEntry], title: str) -> go.Figure:
    """Create price history chart"""
    if not prices:
        return go.Figure().add_annotation(
            text="No price data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pd.DataFrame([
        {
            'timestamp': price.timestamp,
            'price': price.price,
            'date_str': price.timestamp.strftime('%Y-%m-%d %H:%M')
        }
        for price in reversed(prices)  # Reverse to get chronological order
    ])
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['price'],
        mode='lines+markers',
        name='Price',
        line=dict(width=2, color='#1f77b4'),
        marker=dict(size=6),
        hovertemplate='<b>%{text}</b><br>Price: $%{y:.2f}<extra></extra>',
        text=df['date_str']
    ))
    
    # Styling
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        showlegend=False,
        height=400
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="=Í PriceWatch",
        page_icon="=Í",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize components
    db = init_database()
    scraper = init_scraper()
    
    # Header
    st.title("=Í PriceWatch")
    st.markdown("*Track competitor prices automatically*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("=Ê Dashboard")
        
        # Quick stats
        products = db.get_products()
        total_products = len(products)
        
        if total_products > 0:
            # Get latest prices for all products
            latest_prices = []
            for product in products:
                latest = db.get_latest_price(product.url)
                if latest:
                    latest_prices.append(latest.price)
            
            avg_price = sum(latest_prices) / len(latest_prices) if latest_prices else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Products", total_products)
            with col2:
                st.metric("Avg Price", format_currency(avg_price))
        
        st.divider()
        
        # Navigation
        page = st.selectbox(
            "Choose Page",
            ["=Ë Overview", "• Add Product", "= Manual Scrape", "=È Analytics"]
        )
    
    # Main content based on selected page
    if page == "=Ë Overview":
        show_overview(db)
    elif page == "• Add Product":
        show_add_product(db)
    elif page == "= Manual Scrape":
        show_manual_scrape(db, scraper)
    elif page == "=È Analytics":
        show_analytics(db)

def show_overview(db: DatabaseManager):
    """Show overview of all tracked products"""
    st.header("=Ë Product Overview")
    
    products = db.get_products()
    
    if not products:
        st.info("=K Welcome to PriceWatch! Add your first product to get started.")
        if st.button("• Add Product"):
            st.rerun()
        return
    
    # Display products in a grid
    cols = st.columns(2)
    
    for i, product in enumerate(products):
        col = cols[i % 2]
        
        with col:
            with st.container():
                st.subheader(product.label)
                st.caption(f"= {product.url}")
                
                # Get latest price and change
                latest = db.get_latest_price(product.url)
                change = db.get_price_change(product.url)
                
                if latest:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.metric(
                            "Current Price",
                            format_currency(latest.price),
                            delta=f"{change['change_amount']:.2f}" if change else None
                        )
                    
                    with col2:
                        if change:
                            st.markdown(format_percentage(change['change_percentage']))
                        
                        st.caption(f"Updated: {latest.timestamp.strftime('%m/%d %H:%M')}")
                    
                    # Mini chart
                    prices = db.get_prices(product.url, limit=10)
                    if len(prices) > 1:
                        fig = create_price_chart(prices, f"{product.label} - Last 10 Updates")
                        fig.update_layout(height=200, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("No price data yet")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"=Ê View Details", key=f"details_{product.id}"):
                        st.session_state[f"show_details_{product.id}"] = True
                
                with col2:
                    if st.button(f"=Ñ Delete", key=f"delete_{product.id}", type="secondary"):
                        if db.delete_product(product.id):
                            st.success("Product deleted!")
                            st.rerun()
                
                # Show detailed view if requested
                if st.session_state.get(f"show_details_{product.id}", False):
                    with st.expander(f"=Ê Detailed View - {product.label}", expanded=True):
                        prices = db.get_prices(product.url, limit=30)
                        if prices:
                            fig = create_price_chart(prices, f"{product.label} - Price History")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Price history table
                            df = pd.DataFrame([
                                {
                                    'Date': price.timestamp.strftime('%Y-%m-%d %H:%M'),
                                    'Price': format_currency(price.price)
                                }
                                for price in prices[:10]  # Show last 10
                            ])
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No price history available")
                        
                        if st.button("L Close", key=f"close_{product.id}"):
                            st.session_state[f"show_details_{product.id}"] = False
                            st.rerun()
                
                st.divider()

def show_add_product(db: DatabaseManager):
    """Show add product form"""
    st.header("• Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            url = st.text_input(
                "= Product URL",
                placeholder="https://example.com/product",
                help="Enter the full URL of the product page"
            )
            
            label = st.text_input(
                "<÷ Product Label",
                placeholder="My Product Name",
                help="Give this product a memorable name"
            )
        
        with col2:
            css_selector = st.text_input(
                "<¯ CSS Selector (Optional)",
                placeholder=".price",
                help="CSS selector for the price element (leave empty for auto-detection)"
            )
        
        submitted = st.form_submit_button("• Add Product", type="primary")
        
        if submitted:
            if url and label:
                try:
                    product_id = db.add_product(
                        url=url.strip(),
                        label=label.strip(),
                        css_selector=css_selector.strip() or '.price'
                    )
                    
                    st.success(f" Product '{label}' added successfully!")
                    st.info("=¡ Go to 'Manual Scrape' to get the first price reading.")
                    
                    # Clear form
                    if st.button("= Add Another Product"):
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"L Error adding product: {str(e)}")
            else:
                st.error("L Please fill in both URL and Label fields")

def show_manual_scrape(db: DatabaseManager, scraper: PriceScraper):
    """Show manual scraping interface"""
    st.header("= Manual Price Scraping")
    
    products = db.get_products()
    
    if not products:
        st.info("=æ No products added yet. Add a product first!")
        return
    
    # Select product to scrape
    product_options = {f"{p.label} ({p.url})": p for p in products}
    selected = st.selectbox("=æ Select Product to Scrape", options=list(product_options.keys()))
    
    if selected:
        product = product_options[selected]
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info(f"**URL**: {product.url}")
            st.info(f"**Selector**: `{product.css_selector}`")
        
        with col2:
            if st.button("= Scrape Now", type="primary"):
                with st.spinner("=w Scraping price..."):
                    try:
                        # Run scraping
                        result = scraper.scrape_sync(product.url, product.css_selector)
                        
                        if result['success']:
                            # Save to database
                            db.add_price(product.url, result['price'])
                            
                            st.success(f" Price scraped successfully: {format_currency(result['price'])}")
                            
                            # Show price change if available
                            change = db.get_price_change(product.url)
                            if change:
                                if change['change_amount'] != 0:
                                    delta_str = f"${abs(change['change_amount']):.2f}"
                                    direction = "decreased" if change['change_amount'] < 0 else "increased"
                                    st.info(f"=° Price {direction} by {delta_str} ({change['change_percentage']:.1f}%)")
                        else:
                            st.error(f"L Scraping failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"L Error during scraping: {str(e)}")
        
        with col3:
            if st.button("= Test Selector"):
                st.info(">ê Testing CSS selector...")
                # This could be expanded to test selector without saving
        
        # Show recent price history for this product
        st.subheader(f"=Ê Recent Prices - {product.label}")
        prices = db.get_prices(product.url, limit=10)
        
        if prices:
            # Create chart
            fig = create_price_chart(prices, f"{product.label} - Recent Price History")
            st.plotly_chart(fig, use_container_width=True)
            
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
            st.info("=È No price history yet. Scrape some prices to see the chart!")
    
    # Bulk scraping section
    st.divider()
    st.subheader("= Bulk Scraping")
    st.markdown("Scrape prices for all products at once:")
    
    if st.button("=€ Scrape All Products", type="secondary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        urls = [p.url for p in products]
        total = len(urls)
        
        for i, product in enumerate(products):
            status_text.text(f"Scraping {product.label}...")
            progress_bar.progress((i + 1) / total)
            
            try:
                result = scraper.scrape_sync(product.url, product.css_selector)
                if result['success']:
                    db.add_price(product.url, result['price'])
                    
            except Exception as e:
                logger.error(f"Bulk scrape error for {product.url}: {e}")
        
        status_text.text(" Bulk scraping completed!")
        st.success(f"Scraped prices for {total} products")

def show_analytics(db: DatabaseManager):
    """Show analytics and insights"""
    st.header("=È Analytics")
    
    products = db.get_products()
    if not products:
        st.info("=Ê Add products and collect some price data to see analytics!")
        return
    
    # Time range selector
    time_range = st.selectbox(
        "=Å Time Range",
        ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
    )
    
    days_map = {
        "Last 7 days": 7,
        "Last 30 days": 30, 
        "Last 90 days": 90,
        "All time": None
    }
    
    days = days_map[time_range]
    
    # Collect analytics data
    analytics_data = []
    
    for product in products:
        prices = db.get_prices(product.url, limit=1000)  # Get more data for analytics
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            prices = [p for p in prices if p.timestamp >= cutoff_date]
        
        if prices:
            current_price = prices[0].price
            min_price = min(p.price for p in prices)
            max_price = max(p.price for p in prices)
            avg_price = sum(p.price for p in prices) / len(prices)
            
            analytics_data.append({
                'Product': product.label,
                'Current': current_price,
                'Min': min_price,
                'Max': max_price,
                'Avg': avg_price,
                'Volatility': ((max_price - min_price) / avg_price) * 100,
                'Data Points': len(prices)
            })
    
    if analytics_data:
        df = pd.DataFrame(analytics_data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Products Tracked", len(analytics_data))
        
        with col2:
            total_data_points = df['Data Points'].sum()
            st.metric("Total Data Points", total_data_points)
        
        with col3:
            avg_current = df['Current'].mean()
            st.metric("Avg Current Price", format_currency(avg_current))
        
        with col4:
            avg_volatility = df['Volatility'].mean()
            st.metric("Avg Volatility", f"{avg_volatility:.1f}%")
        
        # Analytics table
        st.subheader("=Ê Product Analytics")
        
        # Format the dataframe for display
        display_df = df.copy()
        for col in ['Current', 'Min', 'Max', 'Avg']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}")
        display_df['Volatility'] = display_df['Volatility'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_df, use_container_width=True)
        
        # Volatility chart
        st.subheader("=È Price Volatility Comparison")
        fig = px.bar(
            df,
            x='Product',
            y='Volatility',
            title='Price Volatility by Product (%)',
            color='Volatility',
            color_continuous_scale='RdYlBu_r'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("=Ê No analytics data available for the selected time range.")

if __name__ == "__main__":
    main()