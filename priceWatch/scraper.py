import asyncio
import re
import logging
from typing import Optional, Dict, List
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import time

class PriceScraper:
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Common price selectors for popular sites
        self.price_selectors = {
            'amazon.com': [
                '.a-price-whole',
                '.a-offscreen',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.a-price .a-offscreen'
            ],
            'ebay.com': [
                '.u-flL.condText',
                '.us-pvr-price',
                '#mm-saleDscPrc',
                '.bold'
            ],
            'etsy.com': [
                '.currency-value',
                '.shop2-review-review-header-currency-value'
            ],
            'walmart.com': [
                '[data-testid="price-current"]',
                '.price-current',
                '[itemprop="price"]'
            ],
            'target.com': [
                '[data-test="product-price"]',
                '.h-display-xs'
            ],
            'bestbuy.com': [
                '.pricing-price__range',
                '.sr-only'
            ]
        }
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower().replace('www.', '')
        except:
            return ''
    
    def _get_price_selectors(self, url: str, custom_selector: str = None) -> List[str]:
        """Get appropriate price selectors for the URL"""
        if custom_selector:
            return [custom_selector]
        
        domain = self._get_domain(url)
        
        # Check if we have specific selectors for this domain
        for site, selectors in self.price_selectors.items():
            if site in domain:
                return selectors
        
        # Default generic selectors
        return [
            '.price',
            '[class*="price"]',
            '[id*="price"]',
            '[data-testid*="price"]',
            '.amount',
            '.cost',
            '.value'
        ]
    
    def _clean_price_text(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', price_text.strip())
        
        # Handle different decimal formats
        if ',' in cleaned and '.' in cleaned:
            # Format: 1,234.56
            if cleaned.rindex(',') < cleaned.rindex('.'):
                cleaned = cleaned.replace(',', '')
            # Format: 1.234,56 (European)
            else:
                cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Check if comma is thousands separator or decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Decimal comma: 123,45
                cleaned = cleaned.replace(',', '.')
            else:
                # Thousands separator: 1,234
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    async def _wait_for_page_load(self, page: Page) -> None:
        """Wait for page to fully load"""
        try:
            # Wait for network to be idle
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            
            # Additional wait for dynamic content
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.warning(f"Page load timeout: {e}")
    
    async def scrape_price(self, url: str, css_selector: str = None) -> Dict:
        """Scrape price from a single URL"""
        result = {
            'url': url,
            'price': None,
            'success': False,
            'error': None,
            'timestamp': time.time()
        }
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Navigate to URL
                await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                await self._wait_for_page_load(page)
                
                # Get price selectors to try
                selectors = self._get_price_selectors(url, css_selector)
                
                # Try each selector until we find a price
                price = None
                for selector in selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        
                        for element in elements:
                            text = await element.inner_text()
                            extracted_price = self._clean_price_text(text)
                            
                            if extracted_price and extracted_price > 0:
                                price = extracted_price
                                self.logger.info(f"Found price ${price:.2f} with selector: {selector}")
                                break
                        
                        if price:
                            break
                            
                    except Exception as e:
                        self.logger.debug(f"Selector '{selector}' failed: {e}")
                        continue
                
                # If no price found with selectors, try text analysis
                if not price:
                    price = await self._fallback_price_extraction(page)
                
                if price:
                    result['price'] = price
                    result['success'] = True
                    self.logger.info(f"Successfully scraped price ${price:.2f} from {url}")
                else:
                    result['error'] = "No price found with any selector"
                    self.logger.warning(f"No price found for {url}")
                
                await browser.close()
                
        except Exception as e:
            error_msg = f"Scraping error for {url}: {str(e)}"
            result['error'] = error_msg
            self.logger.error(error_msg)
        
        return result
    
    async def _fallback_price_extraction(self, page: Page) -> Optional[float]:
        """Fallback method to extract price from page text"""
        try:
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and search for price patterns
            text = soup.get_text()
            
            # Common price patterns
            price_patterns = [
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*\$',
                r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*USD'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    price = self._clean_price_text(match)
                    if price and 0.01 <= price <= 999999:  # Reasonable price range
                        return price
            
        except Exception as e:
            self.logger.debug(f"Fallback extraction failed: {e}")
        
        return None
    
    async def scrape_multiple(self, urls: List[str], css_selector: str = None) -> List[Dict]:
        """Scrape prices from multiple URLs concurrently"""
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_price(url, css_selector)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'url': urls[i],
                    'price': None,
                    'success': False,
                    'error': str(result),
                    'timestamp': time.time()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def scrape_sync(self, url: str, css_selector: str = None) -> Dict:
        """Synchronous wrapper for scrape_price"""
        return asyncio.run(self.scrape_price(url, css_selector))
    
    def scrape_multiple_sync(self, urls: List[str], css_selector: str = None) -> List[Dict]:
        """Synchronous wrapper for scrape_multiple"""
        return asyncio.run(self.scrape_multiple(urls, css_selector))

# Convenience functions
def scrape_price(url: str, css_selector: str = None, headless: bool = True) -> Dict:
    """Quick price scraping function"""
    scraper = PriceScraper(headless=headless)
    return scraper.scrape_sync(url, css_selector)

def scrape_multiple_prices(urls: List[str], css_selector: str = None, headless: bool = True) -> List[Dict]:
    """Quick multiple URL scraping function"""
    scraper = PriceScraper(headless=headless)
    return scraper.scrape_multiple_sync(urls, css_selector)

if __name__ == "__main__":
    # Test scraping functionality
    logging.basicConfig(level=logging.INFO)
    
    # Test URLs (use actual product URLs for testing)
    test_urls = [
        "https://example-store.com/product1",  # Replace with actual URLs
        "https://example-store.com/product2"
    ]
    
    scraper = PriceScraper(headless=True)
    
    # Test single URL
    print("Testing single URL scraping...")
    result = scraper.scrape_sync("https://example-store.com/test-product")
    print(f"Result: {result}")
    
    # Test multiple URLs
    print("\nTesting multiple URLs...")
    results = scraper.scrape_multiple_sync(test_urls)
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Price: ${result['price']:.2f}" if result['success'] else f"Error: {result['error']}")
        print("---")