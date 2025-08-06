# PriceWatch Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Basic Usage

#### Start the Dashboard
```bash
streamlit run dashboard_simple.py
```

#### Test the Database
```bash
python3 database.py
```

#### Test Notifications (optional)
```bash
python3 notifier.py --status
```

#### Run the Scheduler
```bash
python3 scheduler.py --mode daily --hour 9
```

## Detailed Setup

### Environment Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
# Email Configuration (for notifications)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com

# Telegram Configuration (for notifications)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### Component Testing

Each component can be tested individually:

#### Database
```bash
python3 database.py
# Creates test database with sample data
```

#### Scraper
```bash
python3 scraper.py
# Tests price extraction patterns
```

#### Scheduler
```bash
python3 scheduler.py --help
# Shows all scheduling options
```

#### Notifications
```bash
python3 notifier.py --test
# Sends test notifications
```

## Usage Patterns

### 1. Manual Price Tracking
```bash
# Start dashboard
streamlit run dashboard_simple.py

# Add products through the web interface
# Manually scrape prices
```

### 2. Automated Tracking
```bash
# Set up products first (via dashboard or database)
# Run scheduler for daily scraping at 9 AM
python3 scheduler.py --mode daily --hour 9 --minute 0
```

### 3. Custom Scheduling
```bash
# Every 6 hours
python3 scheduler.py --mode interval --interval 6

# Custom cron expression (every day at 6 AM and 6 PM)
python3 scheduler.py --mode custom --cron "0 6,18 * * *"
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │◄──►│   Database      │◄──►│    Scraper      │
│   Dashboard     │    │   SQLite        │    │   Playwright    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       ▲                       ▲
        ▼                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │───►│   Save to DB    │◄───│    Notifier     │
│   APScheduler   │    └─────────────────┘    │  Email/Telegram │
└─────────────────┘                           └─────────────────┘
```

## Troubleshooting

### Common Issues

1. **Playwright not found**
   ```bash
   playwright install
   ```

2. **Streamlit not found**
   ```bash
   pip install streamlit
   ```

3. **Permission denied**
   ```bash
   chmod +x *.py
   ```

4. **Database locked**
   - Close any open connections
   - Delete `pricewatch.db` to start fresh

### Dependency Issues

If you encounter missing packages:
```bash
pip install --upgrade -r requirements.txt
```

### Testing Without External Dependencies

The system gracefully handles missing optional dependencies:
- Streamlit: Use database and scraper directly
- Playwright: Manual price entry or mock data
- dotenv: Environment variables can be set manually

## Production Deployment

### Option 1: Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy dashboard

### Option 2: VPS/Server
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip

# Clone and setup
git clone <your-repo>
cd pricewatch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Run components
# Dashboard: streamlit run dashboard_simple.py
# Scheduler: python3 scheduler.py --mode daily
```

### Option 3: Docker (Future Enhancement)
A Docker setup would simplify deployment across different environments.

## Security Notes

- Store credentials in `.env` file (never commit to git)
- Use app passwords for Gmail (not your main password)
- Limit Telegram bot permissions
- Consider using environment variables in production

## Next Steps

1. Add products via the dashboard
2. Configure notifications (optional)
3. Set up automated scraping
4. Monitor price changes
5. Expand with custom CSS selectors for specific sites

## Support

Check the following files for more information:
- `systemDesign.md` - Overall architecture
- `README.md` - Project overview  
- `test_system.py` - Component testing
- Individual `.py` files contain inline documentation