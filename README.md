# 🤖 Telegram Career Coach Bot

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.7-blue)
![Claude AI](https://img.shields.io/badge/Claude-AI-orange?logo=anthropic)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-integrated-green?logo=googlesheets)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple)

A production-ready Telegram bot for a career coaching business. Built as a portfolio demo showcasing modern bot development skills.

**Live demo:** [@automsg1bot](https://t.me/automsg1bot)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📋 **Services & Pricing** | Formatted info pages with inline navigation |
| 📅 **Booking Form** | 3-step FSM dialog with progress indicator & cancel |
| 📊 **Google Sheets** | Bookings auto-saved to spreadsheet in real time |
| 🔔 **Owner Notifications** | Instant Telegram alert on every new booking |
| 💬 **AI Career Assistant** | Claude-powered Q&A with context-aware answers |
| 🛡 **Protection Layer** | Rate limiting, flood control, prompt injection guard |
| 📈 **Admin Stats** | `/stats` command shows bookings, AI queries, users |

---

## 🏗 Architecture

```
telegram-demo-bot/
├── main.py                 # Entry point — bot + middleware setup
├── config.py               # Environment variables
├── keyboards.py            # All keyboards in one place
├── handlers/
│   ├── start.py            # /start command
│   ├── info.py             # Services & prices pages
│   ├── booking.py          # FSM booking flow (3 steps)
│   ├── ai_chat.py          # Claude AI responses
│   └── commands.py         # /help, /stats, /cancel
└── services/
    ├── sheets.py            # Google Sheets integration
    ├── notifications.py     # Owner Telegram alerts
    └── guard.py             # Rate limiting & content filtering
```

---

## 🔒 Protection Layer (`services/guard.py`)

- **Rate limiting** — 5 AI questions per user per day
- **Flood control** — max 1 message per 2 seconds
- **Content filter** — blocks messages < 5 or > 500 characters
- **Repeat filter** — ignores identical consecutive messages
- **Prompt injection guard** — detects jailbreak attempts

---

## 🚀 Tech Stack

- **Python 3.11** — core language
- **aiogram 3.7** — async Telegram Bot API framework
- **Anthropic Claude** — AI responses (claude-haiku-4-5)
- **gspread + google-auth** — Google Sheets integration
- **python-dotenv** — environment variable management
- **Railway.app** — cloud deployment

---

## ⚙️ Setup

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/telegram-demo-bot.git
cd telegram-demo-bot
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:
```
BOT_TOKEN=          # from @BotFather
ANTHROPIC_API_KEY=  # from console.anthropic.com
OWNER_CHAT_ID=      # your Telegram ID (from @userinfobot)
GOOGLE_SHEET_ID=    # from your Google Sheet URL
```

### 3. Google Sheets setup (optional)

1. [Google Cloud Console](https://console.cloud.google.com) → New Project
2. Enable **Google Sheets API**
3. Create **Service Account** → download `credentials.json`
4. Place `credentials.json` in project root
5. Share your Sheet with the `client_email` from `credentials.json`

> Without `credentials.json`, bookings are logged to console — bot won't crash.

### 4. Run

```bash
python main.py
```

---

## ☁️ Deploy to Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables in Railway dashboard
4. Upload `credentials.json` as a file or encode to base64
5. Railway detects `Procfile` and starts the bot automatically

---

## 📱 Bot Flow

```
/start
  └── Welcome + Main Menu keyboard
        ├── 📋 Services  →  Coaching packages
        ├── 💰 Prices    →  Price list
        ├── 📅 Book Now  →  Step 1/3: Name
        │                   Step 2/3: Request
        │                   Step 3/3: Contact
        │                   → Confirm → Sheets + Notify owner
        └── 💬 Ask AI   →  Question → Claude API → Answer
```

---

Built by Andrey · [Upwork Profile](https://www.upwork.com)
