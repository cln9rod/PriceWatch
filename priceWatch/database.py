import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Product:
    id: Optional[int]
    url: str
    label: str
    css_selector: str = '.price'
    created_at: Optional[datetime] = None

@dataclass
class PriceEntry:
    id: Optional[int]
    url: str
    price: float
    timestamp: datetime
    product_id: Optional[int] = None

class DatabaseManager:
    def __init__(self, db_path: str = "pricewatch.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create products table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        label TEXT NOT NULL,
                        css_selector TEXT DEFAULT '.price',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create prices table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS prices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        price REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        product_id INTEGER,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prices_url ON prices (url)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices (timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_url ON products (url)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def add_product(self, url: str, label: str, css_selector: str = '.price') -> int:
        """Add a new product to track"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO products (url, label, css_selector)
                    VALUES (?, ?, ?)
                ''', (url, label, css_selector))
                conn.commit()
                product_id = cursor.lastrowid
                self.logger.info(f"Added product: {label} ({url})")
                return product_id or 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding product: {e}")
            raise
    
    def get_products(self) -> List[Product]:
        """Get all tracked products"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
                rows = cursor.fetchall()
                
                products = []
                for row in rows:
                    products.append(Product(
                        id=row['id'],
                        url=row['url'],
                        label=row['label'],
                        css_selector=row['css_selector'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                    ))
                
                return products
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting products: {e}")
            return []
    
    def add_price(self, url: str, price: float) -> int:
        """Add a new price entry"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get product_id if exists
                cursor.execute('SELECT id FROM products WHERE url = ?', (url,))
                product_row = cursor.fetchone()
                product_id = product_row['id'] if product_row else None
                
                # Insert price entry
                cursor.execute('''
                    INSERT INTO prices (url, price, product_id)
                    VALUES (?, ?, ?)
                ''', (url, price, product_id))
                
                conn.commit()
                price_id = cursor.lastrowid
                self.logger.info(f"Added price entry: ${price:.2f} for {url}")
                return price_id or 0
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding price: {e}")
            raise
    
    def get_prices(self, url: str, limit: int = 100) -> List[PriceEntry]:
        """Get price history for a specific URL"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM prices 
                    WHERE url = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (url, limit))
                
                rows = cursor.fetchall()
                prices = []
                for row in rows:
                    prices.append(PriceEntry(
                        id=row['id'],
                        url=row['url'],
                        price=row['price'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        product_id=row['product_id']
                    ))
                
                return prices
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting prices: {e}")
            return []
    
    def get_latest_price(self, url: str) -> Optional[PriceEntry]:
        """Get the most recent price for a URL"""
        prices = self.get_prices(url, limit=1)
        return prices[0] if prices else None
    
    def get_price_change(self, url: str) -> Optional[Dict]:
        """Get price change information (current vs previous)"""
        try:
            prices = self.get_prices(url, limit=2)
            if len(prices) < 2:
                return None
                
            current = prices[0]
            previous = prices[1]
            
            change_amount = current.price - previous.price
            change_percentage = (change_amount / previous.price) * 100
            
            return {
                'current_price': current.price,
                'previous_price': previous.price,
                'change_amount': change_amount,
                'change_percentage': change_percentage,
                'timestamp': current.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating price change: {e}")
            return None
    
    def get_all_urls(self) -> List[str]:
        """Get all tracked URLs"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT url FROM products')
                rows = cursor.fetchall()
                return [row['url'] for row in rows]
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting URLs: {e}")
            return []
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product and its price history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete associated prices first
                cursor.execute('DELETE FROM prices WHERE product_id = ?', (product_id,))
                
                # Delete product
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                
                conn.commit()
                self.logger.info(f"Deleted product ID: {product_id}")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting product: {e}")
            return False
    
    def cleanup_old_prices(self, days: int = 90) -> int:
        """Clean up price entries older than specified days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM prices 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                self.logger.info(f"Cleaned up {deleted_count} old price entries")
                return deleted_count
                
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up old prices: {e}")
            return 0

# Initialize database instance
db = DatabaseManager()

if __name__ == "__main__":
    # Test database functionality
    logging.basicConfig(level=logging.INFO)
    
    # Test adding a product
    product_id = db.add_product(
        "https://example.com/product",
        "Test Product",
        ".price-display"
    )
    
    # Test adding prices
    db.add_price("https://example.com/product", 99.99)
    db.add_price("https://example.com/product", 89.99)
    
    # Test retrieving data
    products = db.get_products()
    print(f"Products: {len(products)}")
    
    prices = db.get_prices("https://example.com/product")
    print(f"Price entries: {len(prices)}")
    
    change = db.get_price_change("https://example.com/product")
    if change:
        print(f"Price change: ${change['change_amount']:.2f} ({change['change_percentage']:.1f}%)")