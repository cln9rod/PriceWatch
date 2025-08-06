# 🧠 PriceWatch – System Design (Part 1: Overview)

## 🎯 Goal
Build a lightweight, scalable web app that:
- Allows users to add competitor product URLs
- Periodically scrapes and stores price data
- Alerts users when prices change
- Displays price history in a simple dashboard

## 🗺️ System Overview
**Architecture Style:** Modular monolith (MVP) → Microservices (scale)

### 🧩 Core Components
1. **Frontend (UI)** – Streamlit for initial MVP
2. **Scraper** – Playwright-powered headless browser scraper
3. **Database** – SQLite (MVP) → PostgreSQL (scalable)
4. **Scheduler** – APScheduler to run periodic scraping
5. **Notifier** – Email/Telegram alerts
6. **(Optional) API Layer** – FastAPI if REST endpoints are needed later

### 🏗️ High-Level Diagram (Text Representation)
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

# 📦 Part 2: Components in Detail

## 1. 🎛️ Frontend – Streamlit
**Role:** User interface for adding URLs and viewing price history

### Responsibilities:
- Input form to add a new product URL
- Button to trigger manual scrape
- Table or chart to view historical prices
- Flash messages for latest price

### Benefits:
- Fast development
- Lightweight & interactive

### Drawbacks:
- Not suited for multi-user auth or real-time data

➡️ Future Upgrade: React + FastAPI UI

---

## 2. 🕷️ Scraper – Playwright
**Role:** Extract current price from a product page

### Responsibilities:
- Load product page in a headless browser
- Use a CSS selector to extract the price
- Handle JavaScript rendering (e.g., SPAs like Amazon)

### Benefits:
- Reliable and compatible with most modern sites

### Drawbacks:
- Resource-intensive
- Slower than simple requests/BeautifulSoup

➡️ Future Upgrade: Rotate proxies / headless containers for scale

---

# 🗃️ Part 3: Database – SQLite (MVP)

## 🧱 Purpose:
Store product URLs, scraped prices, and timestamps.

### Tables:
- **products** (optional, for future expansion):
  - id
  - url
  - label

- **prices**:
  - id
  - url
  - price
  - timestamp

### Benefits:
- Easy setup, no server needed
- Great for MVP/local usage

### Drawbacks:
- Not optimized for heavy concurrent writes
- Not cloud-native

➡️ Future Upgrade: PostgreSQL + SQLAlchemy + Cloud hosting

---

# ⏰ Part 4: Scheduler – APScheduler

## 🔁 Purpose:
Trigger scraping jobs automatically on a time interval.

### How It Works:
- Load list of tracked URLs from the DB
- Run scraper for each one
- Save results back to DB
- (Optional) Trigger notification if price changed

### Benefits:
- Python-native, simple to implement
- Can run as a separate service or integrated process

### Drawbacks:
- Needs proper logging & error handling

➡️ Future Upgrade: Celery + Redis for distributed task queues

---

# 🔔 Part 5: Notifier – Alerts via Email/Telegram

## 📢 Purpose:
Alert users when price changes significantly.

### Channels:
- **Email (SMTP)**
  - Use Gmail, Mailgun, or SMTP server
- **Telegram Bot API**
  - Setup bot → send message to chat ID

### Alert Logic:
- Compare new price with last stored price
- If delta > threshold → send alert

### Benefits:
- Immediate feedback for users
- Low cost to operate

➡️ Future Upgrade: Push notifications, Slack, Webhooks

---

# 🌐 Part 6: (Optional) API & Deployment

## FastAPI (Optional API Layer)
**Use case:** Expose REST API to allow external apps or frontend clients to:
- Add/remove URLs
- Trigger scrape manually
- Retrieve price history as JSON

## Deployment Options
- **MVP**: Streamlit Cloud (free hosting)
- **Backend**: Render, Railway, Fly.io for cron/scheduler & scraper
- **Database**: SQLite (local), PostgreSQL on Supabase or Neon
- **Custom domain**: Vercel + Framer for landing page

---

✅ This breakdown keeps each part modular, beginner-friendly, and ready to scale gradually.
