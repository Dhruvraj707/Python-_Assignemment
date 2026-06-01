# Binance Futures Testnet Trading Bot

Place Market, Limit, and Stop-Market orders on Binance USDT-M Futures Testnet — via a web UI or the command line.

---

## Quick Start (3 steps)

**Step 1 — Get your testnet API keys**

1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com) and log in (GitHub login works)
2. Click **Account → API Management → Generate Key**
3. Copy your API Key and Secret

**Step 2 — Add keys to `.env`**

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
BINANCE_API_KEY=paste_your_key_here
BINANCE_API_SECRET=paste_your_secret_here
```

**Step 3 — Install and run**

```bash
pip install -r requirements.txt
```

Launch the web UI:
```bash
streamlit run app.py
```

Or use the command line:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

---

## Order Examples

**Market order**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Limit order**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

**Stop-Market order**
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
```

---

## Project Structure

```
trading_bot/
├── app.py              ← Streamlit web UI
├── cli.py              ← Command-line interface
├── bot/
│   ├── client.py       ← Talks to Binance API
│   ├── orders.py       ← Places and validates orders
│   ├── validators.py   ← Input checks
│   └── logging_config.py
├── logs/               ← Auto-created, stores all logs
├── .env.example        ← Copy this to .env
└── requirements.txt
```

---

## Logs

Every order is logged automatically to `logs/trading_bot_YYYYMMDD.log`.
You can view logs live inside the web UI sidebar.

---

## Notes
- Python 3.8+ required
