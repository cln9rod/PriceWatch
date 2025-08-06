import smtplib
import logging
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

class EmailNotifier:
    def __init__(self, 
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 email: str = None,
                 password: str = None):
        """
        Initialize email notifier
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            email: Sender email address
            password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email or os.getenv('EMAIL_ADDRESS') or ''
        self.password = password or os.getenv('EMAIL_PASSWORD') or ''
        self.logger = logging.getLogger(__name__)
        
        if not self.email or not self.password:
            self.logger.warning("Email credentials not provided. Email notifications disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email notification"""
        if not self.enabled:
            self.logger.warning("Email notifier not enabled")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN') or ''
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID') or ''
        self.logger = logging.getLogger(__name__)
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram credentials not provided. Telegram notifications disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a Telegram message"""
        if not self.enabled:
            self.logger.warning("Telegram notifier not enabled")
            return False
        
        try:
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=data, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Telegram message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False

class NotificationManager:
    def __init__(self, 
                 email_config: Dict = None,
                 telegram_config: Dict = None,
                 recipient_email: str = None):
        """
        Initialize notification manager
        
        Args:
            email_config: Email configuration dictionary
            telegram_config: Telegram configuration dictionary  
            recipient_email: Default recipient email address
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize email notifier
        if email_config:
            self.email_notifier = EmailNotifier(**email_config)
        else:
            self.email_notifier = EmailNotifier()
        
        # Initialize Telegram notifier
        if telegram_config:
            self.telegram_notifier = TelegramNotifier(**telegram_config)
        else:
            self.telegram_notifier = TelegramNotifier()
        
        self.recipient_email = recipient_email or os.getenv('RECIPIENT_EMAIL') or ''
        
        # Check if at least one notification method is available
        if not self.email_notifier.enabled and not self.telegram_notifier.enabled:
            self.logger.warning("No notification methods enabled")
    
    def send_price_change_notification(self, change_info: Dict) -> bool:
        """Send notification about price changes"""
        product = change_info['product']
        previous_price = change_info['previous_price']
        current_price = change_info['current_price']
        change_amount = change_info['change_amount']
        change_percentage = change_info['change_percentage']
        timestamp = change_info['timestamp']
        
        # Determine if price increased or decreased
        direction = "INCREASED" if change_amount > 0 else "DECREASED"
        symbol = "UP" if change_amount > 0 else "DOWN"
        
        # Create messages
        subject = f"Price Alert: {product}"
        
        # Plain text message
        plain_message = f"""
Price Alert for {product}

{direction} by ${abs(change_amount):.2f} ({abs(change_percentage):.1f}%)

Previous Price: ${previous_price:.2f}
Current Price: ${current_price:.2f}
Change: ${change_amount:+.2f} ({change_percentage:+.1f}%)

Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
URL: {change_info.get('url', 'N/A')}
"""
        
        # Telegram message (markdown format)
        telegram_message = f"""
*Price Alert*

*{product}*

*{direction}* by ${abs(change_amount):.2f} ({abs(change_percentage):.1f}%)

Previous: ${previous_price:.2f}
Current: ${current_price:.2f}
Change: ${change_amount:+.2f} ({change_percentage:+.1f}%)

Time: {timestamp.strftime('%Y-%m-%d %H:%M')}
"""
        
        # Send notifications
        success_email = False
        success_telegram = False
        
        # Send email
        if self.email_notifier.enabled and self.recipient_email:
            success_email = self.email_notifier.send_email(
                self.recipient_email, subject, plain_message
            )
        
        # Send Telegram message
        if self.telegram_notifier.enabled:
            success_telegram = self.telegram_notifier.send_message(telegram_message)
        
        return success_email or success_telegram
    
    def send_scraping_summary(self, results: Dict) -> bool:
        """Send summary of scraping results"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create summary message
        subject = f"PriceWatch Scraping Summary - {timestamp}"
        
        summary = f"""
Scraping Summary ({timestamp})

Products Scraped: {results['products_scraped']}
Successful: {results['successful']}
Failed: {results['failed']}
Price Changes: {len(results.get('price_changes', []))}
"""
        
        # Add price changes details
        if results.get('price_changes'):
            summary += "\nPrice Changes Detected:\n"
            for change in results['price_changes']:
                direction = "UP" if change['change_amount'] > 0 else "DOWN"
                summary += f"{direction} {change['product']}: ${change['change_amount']:+.2f} ({change['change_percentage']:+.1f}%)\n"
        
        # Add errors if any
        if results.get('errors'):
            summary += f"\nErrors ({len(results['errors'])}):\n"
            for error in results['errors'][:5]:  # Limit to first 5 errors
                summary += f"• {error}\n"
        
        # Telegram message
        telegram_message = f"""
*Scraping Summary*

*Results:*
• Products: {results['products_scraped']}
• Success: {results['successful']}
• Failed: {results['failed']}
• Changes: {len(results.get('price_changes', []))}

Time: {timestamp}
"""
        
        if results.get('price_changes'):
            telegram_message += "\n*Price Changes:*\n"
            for change in results['price_changes']:
                direction = "UP" if change['change_amount'] > 0 else "DOWN"
                telegram_message += f"{direction} *{change['product']}*: ${change['change_amount']:+.2f}\n"
        
        # Send notifications
        success_email = False
        success_telegram = False
        
        # Send email
        if self.email_notifier.enabled and self.recipient_email:
            success_email = self.email_notifier.send_email(
                self.recipient_email, subject, summary
            )
        
        # Send Telegram message
        if self.telegram_notifier.enabled:
            success_telegram = self.telegram_notifier.send_message(telegram_message)
        
        return success_email or success_telegram
    
    def send_test_notification(self) -> Dict:
        """Send test notifications to verify configuration"""
        results = {
            'email': False,
            'telegram': False,
            'timestamp': datetime.now()
        }
        
        test_message = f"""
Test Notification

This is a test message from PriceWatch to verify that notifications are working correctly.

Time: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

If you received this message, your notification system is configured properly!
"""
        
        # Test email
        if self.email_notifier.enabled and self.recipient_email:
            results['email'] = self.email_notifier.send_email(
                self.recipient_email, 
                "PriceWatch Test Notification", 
                test_message
            )
        
        # Test Telegram
        if self.telegram_notifier.enabled:
            telegram_test = f"*PriceWatch Test*\n\n{test_message}"
            results['telegram'] = self.telegram_notifier.send_message(telegram_test)
        
        return results
    
    def get_status(self) -> Dict:
        """Get notification system status"""
        return {
            'email_enabled': self.email_notifier.enabled,
            'telegram_enabled': self.telegram_notifier.enabled,
            'email_configured': bool(self.email_notifier.email and self.email_notifier.password),
            'telegram_configured': bool(self.telegram_notifier.bot_token and self.telegram_notifier.chat_id),
            'recipient_email': self.recipient_email,
            'has_notification_method': self.email_notifier.enabled or self.telegram_notifier.enabled
        }

def main():
    """Test notification functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test PriceWatch Notifications')
    parser.add_argument('--test', action='store_true', help='Send test notifications')
    parser.add_argument('--status', action='store_true', help='Show notification status')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create notification manager
    notifier = NotificationManager()
    
    if args.status:
        status = notifier.get_status()
        print("Notification Status:")
        print(f"Email Enabled: {'Yes' if status['email_enabled'] else 'No'}")
        print(f"Telegram Enabled: {'Yes' if status['telegram_enabled'] else 'No'}")
        print(f"Email Configured: {'Yes' if status['email_configured'] else 'No'}")
        print(f"Telegram Configured: {'Yes' if status['telegram_configured'] else 'No'}")
        print(f"Recipient Email: {status['recipient_email'] or 'Not set'}")
        print(f"Has Notification Method: {'Yes' if status['has_notification_method'] else 'No'}")
    
    if args.test:
        print("Sending test notifications...")
        results = notifier.send_test_notification()
        print(f"Email: {'Sent' if results['email'] else 'Failed'}")
        print(f"Telegram: {'Sent' if results['telegram'] else 'Failed'}")
        
        # Test price change notification
        test_change = {
            'product': 'Test Product',
            'url': 'https://example.com/test',
            'previous_price': 100.00,
            'current_price': 85.00,
            'change_amount': -15.00,
            'change_percentage': -15.0,
            'timestamp': datetime.now()
        }
        
        print("\nSending test price change notification...")
        success = notifier.send_price_change_notification(test_change)
        print(f"Price Change Notification: {'Sent' if success else 'Failed'}")

if __name__ == "__main__":
    main()