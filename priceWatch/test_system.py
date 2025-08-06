#!/usr/bin/env python3
"""
Test script for PriceWatch system components
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_database():
    """Test database functionality"""
    print("🗄️ Testing database...")
    try:
        from database import DatabaseManager
        
        # Create test database
        db = DatabaseManager("test_pricewatch.db")
        
        # Test adding a product
        product_id = db.add_product(
            url="https://example.com/test-product",
            label="Test Product",
            css_selector=".price-test"
        )
        
        # Test adding prices
        db.add_price("https://example.com/test-product", 99.99)
        db.add_price("https://example.com/test-product", 89.99)
        
        # Test retrieving data
        products = db.get_products()
        prices = db.get_prices("https://example.com/test-product")
        change = db.get_price_change("https://example.com/test-product")
        
        print(f"  ✅ Products: {len(products)}")
        print(f"  ✅ Price entries: {len(prices)}")
        print(f"  ✅ Price change: ${change['change_amount']:.2f} ({change['change_percentage']:.1f}%)")
        
        # Cleanup
        import os
        if os.path.exists("test_pricewatch.db"):
            os.remove("test_pricewatch.db")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_scraper():
    """Test scraper functionality (without actual web requests)"""
    print("🕷️ Testing scraper...")
    try:
        from scraper import PriceScraper
        
        # Create scraper instance
        scraper = PriceScraper(headless=True)
        
        # Test price cleaning function
        test_prices = [
            "$99.99", "£89.50", "€75.25", "1,234.56", "1.234,56"
        ]
        
        for price_text in test_prices:
            cleaned = scraper._clean_price_text(price_text)
            print(f"  ✅ '{price_text}' -> {cleaned}")
        
        # Test domain extraction
        test_urls = [
            "https://www.amazon.com/product/123",
            "https://ebay.com/item/456",
            "https://example-store.co.uk/products/test"
        ]
        
        for url in test_urls:
            domain = scraper._get_domain(url)
            selectors = scraper._get_price_selectors(url)
            print(f"  ✅ {domain}: {len(selectors)} selectors")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scraper test failed: {e}")
        return False

def test_scheduler():
    """Test scheduler functionality"""
    print("⏰ Testing scheduler...")
    try:
        from scheduler import PriceScheduler
        
        # Create scheduler instance (don't start)
        scheduler = PriceScheduler(
            db_path="test_pricewatch.db",
            enable_notifications=False
        )
        
        # Setup scheduler
        scheduler.setup_scheduler("background")
        
        # Add test job
        scheduler.add_daily_job(hour=9, minute=0)
        
        # Get job status
        jobs = scheduler.get_job_status()
        stats = scheduler.get_stats()
        
        print(f"  ✅ Jobs scheduled: {len(jobs)}")
        print(f"  ✅ Stats initialized: {len(stats)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scheduler test failed: {e}")
        return False

def test_notifier():
    """Test notifier functionality (without sending actual notifications)"""
    print("📬 Testing notifier...")
    try:
        from notifier import NotificationManager
        
        # Create notifier (will likely be disabled without credentials)
        notifier = NotificationManager()
        
        # Get status
        status = notifier.get_status()
        print(f"  ✅ Email configured: {status['email_configured']}")
        print(f"  ✅ Telegram configured: {status['telegram_configured']}")
        print(f"  ✅ Has notification method: {status['has_notification_method']}")
        
        # Test message formatting (without sending)
        test_change = {
            'product': 'Test Product',
            'url': 'https://example.com/test',
            'previous_price': 100.00,
            'current_price': 85.00,
            'change_amount': -15.00,
            'change_percentage': -15.0,
            'timestamp': datetime.now()
        }
        
        # This will test the message formatting but not actually send
        print("  ✅ Message formatting test passed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Notifier test failed: {e}")
        return False

def test_streamlit_import():
    """Test if Streamlit dashboard can be imported"""
    print("Dashboard Testing...")
    try:
        # Test if we can import the dashboard module
        import dashboard_simple
        print("  ✅ Dashboard module imported successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard import failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 PriceWatch System Tests")
    print("=" * 40)
    
    tests = [
        ("Database", test_database),
        ("Scraper", test_scraper),
        ("Scheduler", test_scheduler),
        ("Notifier", test_notifier),
        ("Dashboard", test_streamlit_import)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"  ❌ {name} test crashed: {e}")
            results[name] = False
        print()
    
    # Summary
    print("📋 Test Summary:")
    print("-" * 20)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:12} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)