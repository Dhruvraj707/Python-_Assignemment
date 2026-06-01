# Binance Futures Testnet Trading Bot

A Python CLI application that places **Market**, **Limit**, and **Stop-Market** orders on the **Binance USDT-M Futures Testnet**. Built with a clean client/logic/CLI separation, structured logging, and robust input validation.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, HTTP, error handling)
│   ├── orders.py          # Order placement logic + OrderResult model
│   ├── validators.py      # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py  # Dual-handler logger (file DEBUG + console INFO)
├── logs/
│   ├── market_order_sample.log
│   └── limit_order_sample.log
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Credential template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com) and log in (GitHub auth works).
2. Go to **Account → API Management** → Generate a new API key.
3. Copy your **API Key** and **API Secret**.

### 2. Install Dependencies

```bash
# Python 3.8+ required
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Edit .env and paste your API key and secret
```

`.env` file:
```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Alternatively**, pass credentials directly via CLI flags (see examples below).

---

## How to Run

```
python cli.py --symbol SYMBOL --side BUY|SELL --type ORDER_TYPE --quantity QTY [--price PRICE] [--stop-price STOP]
```

### Arguments

| Argument  | Description |

| `--symbol`  | Trading pair, e.g. `BTCUSDT` |
| `--side`  | `BUY` or `SELL` |
| `--type`  | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity`  | Order quantity (base asset) |
| `--price` | (For LIMIT)  Limit price |
| `--stop-price` | (For STOP_MARKET)  Stop trigger price |
| `--api-key` | (Optional)  Overrides `.env` |
| `--api-secret`| Optional | Overrides `.env` |

---

## Usage Examples

### Market Order (BUY)
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Output:**
```
----------------------------------------------------
  ORDER REQUEST SUMMARY
----------------------------------------------------
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
----------------------------------------------------

====================================================
  ORDER RESPONSE
====================================================
  Order ID      : 3278491023
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Orig Qty      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 67432.10
====================================================
  ✅  Order submitted successfully!
====================================================
```

---

### Limit Order (SELL)
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

---

### Stop-Market Order (Bonus order type)
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 65000
```

---

### Passing Credentials Inline (no .env needed)
```bash
python cli.py \
  --symbol ETHUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01 \
  --api-key YOUR_KEY \
  --api-secret YOUR_SECRET
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log` automatically.

- **Console**: INFO level (clean, human-readable)
- **File**: DEBUG level (full request/response detail for auditing)

Log format:
```
2025-06-01 10:15:43 | INFO     | client | Placing BUY MARKET order | symbol=BTCUSDT qty=0.001 ...
2025-06-01 10:15:44 | INFO     | client | Order placed successfully: orderId=3278491023 status=FILLED
```

Sample logs from actual testnet runs are in the `logs/` folder.

---

## Error Handling

| Scenario | Behavior |
|---|---|
| Missing/invalid symbol | `ValidationError` with clear message |
| Wrong side/order type | Rejected before API call |
| Price missing for LIMIT | Rejected before API call |
| Binance API error (e.g. insufficient margin) | Prints error code + message, logs full detail |
| Network failure | Prints connectivity message, exits cleanly |
| Missing credentials | Prints setup instructions, exits |

---

## Requirements

```
requests>=2.31.0
python-dotenv>=1.0.0
```

Python 3.8+
