import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import signal
import sys
import os
import asyncio

# Import local modules
from database import DatabaseManager, Product
from scraper import PriceScraper
from notifier import NotificationManager

class PriceScheduler:
    def __init__(self, 
                 db_path: str = "pricewatch.db",
                 headless: bool = True,
                 enable_notifications: bool = True,
                 notification_threshold: float = 5.0):
        """
        Initialize the price scheduler
        
        Args:
            db_path: Path to SQLite database
            headless: Run browser in headless mode
            enable_notifications: Enable price change notifications
            notification_threshold: Minimum price change % to trigger notification
        """
        self.db = DatabaseManager(db_path)
        self.scraper = PriceScraper(headless=headless)
        self.notification_manager = NotificationManager() if enable_notifications else None
        self.notification_threshold = notification_threshold
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Setup scheduler
        self.scheduler = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_scrapes': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'notifications_sent': 0,
            'last_run': None,
            'start_time': None
        }
    
    def setup_scheduler(self, scheduler_type: str = "background") -> None:
        """Setup the APScheduler instance"""
        if scheduler_type.lower() == "blocking":
            self.scheduler = BlockingScheduler()
        else:
            self.scheduler = BackgroundScheduler()
        
        # Configure job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        self.scheduler.configure(job_defaults=job_defaults)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def scrape_all_products(self) -> dict:
        """Scrape prices for all tracked products"""
        start_time = datetime.now()
        self.logger.info("Starting scheduled price scraping...")
        
        # Get all products
        products = self.db.get_products()
        if not products:
            self.logger.warning("No products to scrape")
            return {
                'success': True,
                'message': 'No products to scrape',
                'products_scraped': 0,
                'successful': 0,
                'failed': 0
            }
        
        results = {
            'products_scraped': len(products),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'price_changes': []
        }
        
        # Scrape each product
        for product in products:
            try:
                self.logger.info(f"Scraping {product.label} ({product.url})")
                
                # Get previous price for comparison
                previous_price_entry = self.db.get_latest_price(product.url)
                previous_price = previous_price_entry.price if previous_price_entry else None
                
                # Scrape current price
                scrape_result = self.scraper.scrape_sync(product.url, product.css_selector)
                
                if scrape_result['success']:
                    current_price = scrape_result['price']
                    
                    # Save to database
                    self.db.add_price(product.url, current_price)
                    results['successful'] += 1
                    
                    self.logger.info(f"Successfully scraped ${current_price:.2f} for {product.label}")
                    
                    # Check for significant price changes
                    if previous_price is not None:
                        price_change = ((current_price - previous_price) / previous_price) * 100
                        
                        if abs(price_change) >= self.notification_threshold:
                            change_info = {
                                'product': product.label,
                                'url': product.url,
                                'previous_price': previous_price,
                                'current_price': current_price,
                                'change_amount': current_price - previous_price,
                                'change_percentage': price_change,
                                'timestamp': datetime.now()
                            }
                            
                            results['price_changes'].append(change_info)
                            
                            # Send notification
                            if self.notification_manager:
                                try:
                                    self.notification_manager.send_price_change_notification(change_info)
                                    self.stats['notifications_sent'] += 1
                                except Exception as e:
                                    self.logger.error(f"Failed to send notification: {e}")
                
                else:
                    results['failed'] += 1
                    error_msg = f"Failed to scrape {product.label}: {scrape_result.get('error', 'Unknown error')}"
                    results['errors'].append(error_msg)
                    self.logger.error(error_msg)
                
                # Update stats
                self.stats['total_scrapes'] += 1
                if scrape_result['success']:
                    self.stats['successful_scrapes'] += 1
                else:
                    self.stats['failed_scrapes'] += 1
                
                # Small delay between scrapes to be respectful
                time.sleep(2)
                
            except Exception as e:
                results['failed'] += 1
                error_msg = f"Exception scraping {product.label}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
        
        # Update stats
        self.stats['last_run'] = datetime.now()
        
        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Scraping completed in {duration:.1f}s - Success: {results['successful']}, Failed: {results['failed']}")
        
        # Send summary notification if there were price changes
        if results['price_changes'] and self.notification_manager:
            try:
                self.notification_manager.send_scraping_summary(results)
            except Exception as e:
                self.logger.error(f"Failed to send summary notification: {e}")
        
        return results
    
    def add_daily_job(self, hour: int = 9, minute: int = 0) -> None:
        """Add a daily scraping job"""
        if not self.scheduler:
            raise ValueError("Scheduler not initialized. Call setup_scheduler() first.")
        
        trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            func=self.scrape_all_products,
            trigger=trigger,
            id='daily_scrape',
            name=f'Daily price scraping at {hour:02d}:{minute:02d}',
            replace_existing=True
        )
        
        self.logger.info(f"Added daily scraping job at {hour:02d}:{minute:02d}")
    
    def add_interval_job(self, hours: int = 6) -> None:
        """Add an interval-based scraping job"""
        if not self.scheduler:
            raise ValueError("Scheduler not initialized. Call setup_scheduler() first.")
        
        trigger = IntervalTrigger(hours=hours)
        
        self.scheduler.add_job(
            func=self.scrape_all_products,
            trigger=trigger,
            id='interval_scrape',
            name=f'Interval scraping every {hours} hours',
            replace_existing=True
        )
        
        self.logger.info(f"Added interval scraping job every {hours} hours")
    
    def add_custom_job(self, cron_expression: str, job_id: str = "custom_scrape") -> None:
        """Add a custom cron-based scraping job"""
        if not self.scheduler:
            raise ValueError("Scheduler not initialized. Call setup_scheduler() first.")
        
        trigger = CronTrigger.from_crontab(cron_expression)
        
        self.scheduler.add_job(
            func=self.scrape_all_products,
            trigger=trigger,
            id=job_id,
            name=f'Custom scraping: {cron_expression}',
            replace_existing=True
        )
        
        self.logger.info(f"Added custom scraping job: {cron_expression}")
    
    def start(self, scheduler_type: str = "blocking") -> None:
        """Start the scheduler"""
        if not self.scheduler:
            self.setup_scheduler(scheduler_type)
        
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        jobs = self.scheduler.get_jobs()
        if not jobs:
            self.logger.warning("No jobs scheduled. Add jobs before starting.")
            return
        
        self.stats['start_time'] = datetime.now()
        self.is_running = True
        
        self.logger.info(f"Starting scheduler with {len(jobs)} job(s)...")
        for job in jobs:
            self.logger.info(f"  - {job.name} (next run: {job.next_run_time})")
        
        try:
            self.scheduler.start()
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            self.is_running = False
            raise
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler and self.is_running:
            self.logger.info("Stopping scheduler...")
            self.scheduler.shutdown()
            self.is_running = False
        else:
            self.logger.info("Scheduler is not running")
    
    def get_stats(self) -> dict:
        """Get scheduler statistics"""
        stats = self.stats.copy()
        
        if stats['start_time']:
            stats['uptime_seconds'] = (datetime.now() - stats['start_time']).total_seconds()
            stats['uptime_formatted'] = str(datetime.now() - stats['start_time'])
        
        if stats['total_scrapes'] > 0:
            stats['success_rate'] = (stats['successful_scrapes'] / stats['total_scrapes']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def get_job_status(self) -> List[dict]:
        """Get status of all scheduled jobs"""
        if not self.scheduler:
            return []
        
        jobs = self.scheduler.get_jobs()
        job_status = []
        
        for job in jobs:
            job_status.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        
        return job_status

def main():
    """Main function to run the scheduler as a standalone service"""
    import argparse
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='PriceWatch Scheduler Service')
    parser.add_argument('--mode', choices=['daily', 'interval', 'custom'], 
                       default='daily', help='Scheduling mode')
    parser.add_argument('--hour', type=int, default=9, 
                       help='Hour for daily mode (0-23)')
    parser.add_argument('--minute', type=int, default=0, 
                       help='Minute for daily mode (0-59)')
    parser.add_argument('--interval', type=int, default=6, 
                       help='Interval in hours for interval mode')
    parser.add_argument('--cron', type=str, 
                       help='Cron expression for custom mode (e.g., "0 */6 * * *")')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode')
    parser.add_argument('--no-notifications', action='store_true',
                       help='Disable notifications')
    parser.add_argument('--threshold', type=float, default=5.0,
                       help='Price change threshold for notifications (%)')
    parser.add_argument('--db-path', type=str, default='pricewatch.db',
                       help='Path to SQLite database')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create scheduler instance
    scheduler = PriceScheduler(
        db_path=args.db_path,
        headless=args.headless,
        enable_notifications=not args.no_notifications,
        notification_threshold=args.threshold
    )
    
    # Add job based on mode
    try:
        if args.mode == 'daily':
            scheduler.add_daily_job(args.hour, args.minute)
        elif args.mode == 'interval':
            scheduler.add_interval_job(args.interval)
        elif args.mode == 'custom':
            if not args.cron:
                parser.error("--cron is required for custom mode")
            scheduler.add_custom_job(args.cron)
        
        # Start scheduler
        print(f"=€ PriceWatch Scheduler starting in {args.mode} mode...")
        print("Press Ctrl+C to stop")
        
        scheduler.start()
        
    except KeyboardInterrupt:
        print("\nù  Scheduler stopped by user")
    except Exception as e:
        print(f"L Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()