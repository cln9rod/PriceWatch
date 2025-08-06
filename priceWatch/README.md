# 🛍️ PriceWatch

A lightweight app that helps e-commerce sellers track competitor prices automatically. Users can paste product URLs, and PriceWatch will scrape, store, and notify them of price changes over time.

---

## 🚀 Features
- 🔗 Add product URLs to track
- 💰 Extract and log current price using Playwright
- 📉 View price history and trend via Streamlit dashboard
- 🕒 Scheduled daily scraping using APScheduler
- 🔔 Notifications via Email or Telegram (optional)

---

## 🧱 Architecture Overview
```
   +-------------+     +-------------+     +-------------+
   |   Streamlit|<--->|   Database  |<--->|   Scraper    |
   |   Dashboard|     |   SQLite    |     | Playwright  |
   +-------------+     +-------------+     +-------------+
         |                    ^                   ^
         v                    |                   |
+------------------+    +--------------+     +----------+
| Scheduler (cron) |--->| Save to DB   |<----| Notifier |
+------------------+    +--------------+     +----------+
```

---

## 🧰 Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python (modular scripts)
- **Scraping:** Playwright
- **Database:** SQLite (can scale to PostgreSQL)
- **Scheduler:** APScheduler
- **Notifications:** SMTP, Telegram Bot API (optional)

---

## 📦 Project Structure
```
pricewatch/
├── dashboard.py      # Streamlit dashboard UI
├── scraper.py        # Web scraping logic
├── database.py       # SQLite setup and helpers
├── scheduler.py      # Periodic scraping jobs
├── notifier.py       # Alert notifications
├── requirements.txt
└── README.md
```

---

## 🛠️ Installation
```bash
git clone https://github.com/yourusername/pricewatch.git
cd pricewatch
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

---

## 🧪 Usage
### Run the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

### Run the background scheduler:
```bash
python scheduler.py
```

---

## 🧠 Customization
- Update the CSS selector in `scraper.py` to match the target product site
- Add Telegram credentials to `notifier.py` to enable alerts
- Expand `dashboard.py` to support multiple URLs and historical charts

---

## 🗺️ Roadmap
- [ ] Multi-user support with login
- [ ] Price charts using Plotly
- [ ] URL management dashboard
- [ ] REST API with FastAPI
- [ ] Cloud deployment on Render or Streamlit Cloud

---

## 📄 License
MIT License © 2025 [Your Name]
