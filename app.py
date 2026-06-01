from __future__ import annotations

import os
import sys
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── importpath so bot/ resolves correctly ─────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order as bot_place_order
from bot.validators import ValidationError

# ── credentials from .env only ────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
API_KEY    = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

logger = setup_logger("ui")

st.set_page_config(
    page_title="Futures Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── base ── */
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0d1117; color: #e6edf3; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1100px; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

/* ── metric cards ── */
[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: .78rem !important; text-transform: uppercase; letter-spacing: .05em; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; font-size: 1.35rem !important; font-weight: 700 !important; font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stMetricDelta"] { font-size: .78rem !important; }

/* ── inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56,139,253,.15) !important;
}
label { color: #8b949e !important; font-size: .82rem !important; text-transform: uppercase; letter-spacing: .06em; font-weight: 600 !important; }

/* ── buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    transition: all .18s ease !important;
    border: none !important;
    padding: .65rem 1.4rem !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2ea043, #3fb950) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(46,160,67,.4) !important;
}
.sell-btn > button {
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
    color: #fff !important;
}
.sell-btn > button:hover {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(220,38,38,.4) !important;
}

/* ── radio ── */
[data-testid="stRadio"] > div { gap: .5rem; }
[data-testid="stRadio"] label {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    padding: .45rem 1.2rem !important;
    cursor: pointer;
    color: #c9d1d9 !important;
    font-size: .88rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: all .15s;
}
[data-testid="stRadio"] label:hover { border-color: #388bfd !important; color: #e6edf3 !important; }

/* ── divider ── */
hr { border-color: #21262d !important; margin: 1.4rem 0 !important; }

/* ── alerts ── */
[data-testid="stAlert"] { border-radius: 10px !important; border-left-width: 4px !important; }

/* ── expander ── */
[data-testid="stExpander"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #c9d1d9 !important; font-weight: 600 !important; }

/* ── code / log ── */
[data-testid="stCode"] pre {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 10px !important;
    font-size: .78rem !important;
    color: #79c0ff !important;
}

/* ── custom cards ── */
.order-card {
    background: #161b22;
    border: 1px solid #238636;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
    box-shadow: 0 0 24px rgba(35,134,54,.12);
}
.order-card-err {
    background: #161b22;
    border: 1px solid #da3633;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
    box-shadow: 0 0 24px rgba(218,54,51,.12);
}
.card-title {
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 1rem;
}
.orow {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid #21262d;
    font-size: .9rem;
}
.orow:last-child { border-bottom: none; }
.olabel { color: #8b949e; }
.ovalue { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #e6edf3; }
.s-filled { color: #3fb950 !important; }
.s-new    { color: #388bfd !important; }
.s-part   { color: #d29922 !important; }
.s-other  { color: #f85149 !important; }

/* ── history row ── */
.hist-buy  { color: #3fb950; font-weight: 700; }
.hist-sell { color: #f85149; font-weight: 700; }

/* ── page title ── */
.page-header {
    display: flex; align-items: center; gap: .8rem;
    margin-bottom: .2rem;
}
.page-title {
    font-size: 1.8rem; font-weight: 700; color: #e6edf3;
    letter-spacing: -.02em; margin: 0;
}
.page-sub { font-size: .85rem; color: #8b949e; margin-bottom: 1.4rem; }
.env-pill-ok  { display:inline-block; background:#0f2a1a; border:1px solid #238636; color:#3fb950;
                border-radius:20px; padding:3px 14px; font-size:.78rem; font-weight:600; }
.env-pill-bad { display:inline-block; background:#2d0f0e; border:1px solid #da3633; color:#f85149;
                border-radius:20px; padding:3px 14px; font-size:.78rem; font-weight:600; }

/* ── live price badge ── */
.price-badge {
    display: inline-flex; align-items: center; gap: .5rem;
    background: #0d2137; border: 1px solid #1f6feb;
    border-radius: 8px; padding: .45rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem; font-weight: 700; color: #58a6ff;
    margin: .5rem 0 1rem;
}
</style>
""", unsafe_allow_html=True)


if "history" not in st.session_state:
    st.session_state.history: list[dict] = []
if "client" not in st.session_state:
    st.session_state.client = None

@st.cache_resource(show_spinner=False)
def build_client(key: str, secret: str) -> BinanceFuturesClient:
    return BinanceFuturesClient(api_key=key, api_secret=secret)


def get_client() -> BinanceFuturesClient | None:
    if not API_KEY or not API_SECRET:
        return None
    if st.session_state.client is None:
        try:
            st.session_state.client = build_client(API_KEY, API_SECRET)
        except Exception:
            return None
    return st.session_state.client


def fetch_live_price(symbol: str) -> float | None:
    c = get_client()
    if not c:
        return None
    try:
        data = c._get("/fapi/v1/ticker/price", {"symbol": symbol})
        return float(data["price"])
    except Exception:
        return None


def status_css(s: str) -> str:
    return {"FILLED": "s-filled", "NEW": "s-new",
            "PARTIALLY_FILLED": "s-part"}.get(s, "s-other")


def render_order_card(r: dict, is_error: bool = False) -> None:
    status = r.get("status", "UNKNOWN")
    css    = status_css(status)
    klass  = "order-card-err" if is_error else "order-card"
    price_row = (
        f'<div class="orow"><span class="olabel">Limit Price</span>'
        f'<span class="ovalue">{r.get("price")}</span></div>'
        if r.get("price") and r.get("price") not in ("0", "0.00000000") else ""
    )
    stop_row = (
        f'<div class="orow"><span class="olabel">Stop Price</span>'
        f'<span class="ovalue">{r.get("stopPrice")}</span></div>'
        if r.get("stopPrice") and r.get("stopPrice") not in ("0", "0.00000000") else ""
    )
    avg = r.get("avgPrice", "0")
    avg_display = f'${float(avg):,.2f}' if avg and avg != "0" else "—"
    ts = r.get("updateTime", "")
    time_str = datetime.fromtimestamp(ts / 1000).strftime("%H:%M:%S") if ts else "—"

    st.markdown(f"""
    <div class="{klass}">
      <div class="card-title">📄 Order Confirmation</div>
      <div class="orow"><span class="olabel">Order ID</span>
           <span class="ovalue">#{r.get("orderId","—")}</span></div>
      <div class="orow"><span class="olabel">Symbol</span>
           <span class="ovalue">{r.get("symbol","—")}</span></div>
      <div class="orow"><span class="olabel">Side</span>
           <span class="ovalue">{r.get("side","—")}</span></div>
      <div class="orow"><span class="olabel">Type</span>
           <span class="ovalue">{r.get("type","—")}</span></div>
      <div class="orow"><span class="olabel">Status</span>
           <span class="ovalue {css}">{status}</span></div>
      <div class="orow"><span class="olabel">Orig Qty</span>
           <span class="ovalue">{r.get("origQty","—")}</span></div>
      <div class="orow"><span class="olabel">Executed Qty</span>
           <span class="ovalue">{r.get("executedQty","—")}</span></div>
      <div class="orow"><span class="olabel">Avg Fill Price</span>
           <span class="ovalue">{avg_display}</span></div>
      {price_row}{stop_row}
      <div class="orow"><span class="olabel">Time</span>
           <span class="ovalue">{time_str}</span></div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚀 Futures Bot")
    st.markdown("---")

    # env status
    if API_KEY and API_SECRET:
        st.markdown('<span class="env-pill-ok">✓ .env loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="env-pill-bad">✗ .env missing</span>', unsafe_allow_html=True)
        st.warning("Add `BINANCE_API_KEY` and `BINANCE_API_SECRET` to your `.env` file.")

    st.markdown("---")

    # session stats
    total = len(st.session_state.history)
    buys  = sum(1 for o in st.session_state.history if o.get("side") == "BUY")
    sells = total - buys
    st.markdown("**Session Stats**")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Total", total)
    sc2.metric("Buys 🟢", buys)
    sc3.metric("Sells 🔴", sells)

    st.markdown("---")

    # ── log viewer ─────────────────────────────────────────────────────────
    st.markdown("**📋 Log Viewer**")
    log_dir   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    log_files = sorted(
        [f for f in os.listdir(log_dir) if f.endswith(".log")],
        reverse=True,
    ) if os.path.isdir(log_dir) else []

    if not log_files:
        st.caption("Log files appear after your first order.")
    else:
        chosen_log = st.selectbox("File", log_files, label_visibility="collapsed")
        n_lines    = st.slider("Lines", 10, 100, 20, 5)
        with open(os.path.join(log_dir, chosen_log)) as f:
            lines = f.readlines()
        st.code("".join(lines[-n_lines:]), language="log")

    st.markdown("---")
    st.caption("⚠️ Testnet — paper trading only")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — header
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <span style="font-size:2rem">🚀</span>
  <p class="page-title">Binance Futures Testnet</p>
</div>
<p class="page-sub">USDT-M Perpetuals · Place Market, Limit &amp; Stop-Market orders</p>
""", unsafe_allow_html=True)

left, right = st.columns([1.15, 1], gap="large")
with left:
    st.markdown("#### Place Order")

    # symbol + order type
    fc1, fc2 = st.columns(2)
    with fc1:
        symbol = st.text_input("Symbol", value="BTCUSDT",
                               placeholder="BTCUSDT").strip().upper()
    with fc2:
        order_type = st.selectbox("Order Type",
                                  ["MARKET", "LIMIT", "STOP_MARKET"])

    # live price
    if symbol and API_KEY:
        live = fetch_live_price(symbol)
        if live:
            st.markdown(
                f'<div class="price-badge">📡 {symbol} &nbsp; ${live:,.2f}</div>',
                unsafe_allow_html=True,
            )

    # side radio
    st.markdown("**Side**")
    side = st.radio("Side", ["BUY", "SELL"], horizontal=True,
                    label_visibility="collapsed")

    # quantity
    quantity = st.number_input("Quantity", min_value=0.0001, value=0.001,
                               step=0.001, format="%.4f",
                               help="Base asset amount, e.g. 0.001 BTC")

    # conditional price fields
    price, stop_price = None, None
    if order_type == "LIMIT":
        price = st.number_input("Limit Price (USDT)", min_value=0.01,
                                value=round(live, 2) if (symbol and API_KEY and fetch_live_price(symbol)) else 50000.0,
                                step=100.0, format="%.2f")
    if order_type == "STOP_MARKET":
        stop_price = st.number_input("Stop Price (USDT)", min_value=0.01,
                                     value=25000.0, step=100.0, format="%.2f")

    st.markdown("---")

    # ── submit button ─────────────────────────────────────────────────────
    if not (API_KEY and API_SECRET):
        st.error("No credentials found in `.env` — cannot place orders.")
    else:
        btn_label = f"{'🟢  Place BUY' if side == 'BUY' else '🔴  Place SELL'}  {order_type}  Order"
        btn_col = st.columns(1)[0]

        if side == "SELL":
            btn_col.markdown('<div class="sell-btn">', unsafe_allow_html=True)

        clicked = btn_col.button(btn_label, use_container_width=True, type="primary")

        if side == "SELL":
            btn_col.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            client = get_client()
            if not client:
                st.error("Could not initialise client — check your `.env`.")
            else:
                with st.spinner("Submitting order…"):
                    try:
                        # ── calls bot/orders.py exactly like cli.py ──────
                        result_obj = bot_place_order(
                            client     = client,
                            symbol     = symbol,
                            side       = side,
                            order_type = order_type,
                            quantity   = quantity,
                            price      = price,
                            stop_price = stop_price,
                        )
                        raw = result_obj.raw
                        st.session_state.history.insert(0, raw)
                        status = raw.get("status", "UNKNOWN")

                        if status in ("FILLED", "NEW", "PARTIALLY_FILLED"):
                            st.success(f"✅ Order placed! Status: **{status}**")
                        else:
                            st.warning(f"⚠️ Status: **{status}**")

                        render_order_card(raw)

                    except ValidationError as e:
                        logger.error("Validation: %s", e)
                        st.error(f"❌ Validation: {e}")
                    except BinanceClientError as e:
                        logger.error("API error: %s", e)
                        st.error(f"❌ API Error {e.code}: {e.message}")
                    except ConnectionError as e:
                        logger.error("Network: %s", e)
                        st.error(f"❌ Network Error: {e}")
                    except Exception as e:
                        logger.exception("Unexpected: %s", e)
                        st.error(f"❌ Unexpected: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# RIGHT — order preview + history
# ─────────────────────────────────────────────────────────────────────────────
with right:

    # ── live preview card ─────────────────────────────────────────────────
    st.markdown("#### Order Preview")
    p1, p2, p3 = st.columns(3)
    p1.metric("Symbol",   symbol     if symbol    else "—")
    p2.metric("Side",     side)
    p3.metric("Type",     order_type)
    p4, p5, p6 = st.columns(3)
    p4.metric("Quantity", f"{quantity:.4f}")
    p5.metric("Limit $",  f"{price:,.2f}"      if price      else "—")
    p6.metric("Stop $",   f"{stop_price:,.2f}" if stop_price else "—")

    st.markdown("---")

    # ── order history ─────────────────────────────────────────────────────
    st.markdown("#### 🕓 Order History")

    if not st.session_state.history:
        st.markdown(
            '<div style="color:#8b949e;font-size:.88rem;padding:.8rem 0">'
            'No orders placed yet in this session.</div>',
            unsafe_allow_html=True,
        )
    else:
        hcol, _ = st.columns([1, 3])
        with hcol:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        for o in st.session_state.history:
            stat   = o.get("status", "—")
            s_css  = "hist-buy" if o.get("side") == "BUY" else "hist-sell"
            icon   = "🟢" if o.get("side") == "BUY" else "🔴"
            avg    = o.get("avgPrice", "0")
            avg_s  = f"${float(avg):,.2f}" if avg and avg != "0" else "—"
            label  = f"{icon} #{o.get('orderId')}  ·  {o.get('symbol')}  ·  {stat}"

            with st.expander(label, expanded=False):
                hc1, hc2, hc3, hc4 = st.columns(4)
                hc1.metric("Side",     o.get("side", "—"))
                hc2.metric("Type",     o.get("type", "—"))
                hc3.metric("Orig Qty", o.get("origQty", "—"))
                hc4.metric("Exec Qty", o.get("executedQty", "—"))
                hc5, hc6, _, _ = st.columns(4)
                hc5.metric("Avg Price", avg_s)
                hc6.metric("Status",    stat)