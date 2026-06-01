from __future__ import annotations

from typing import Any

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logger("orders")


class OrderResult:
    """Structured wrapper for a Binance order response."""

    def __init__(self, raw: dict[str, Any]):
        self.raw = raw
        self.order_id: int = raw.get("orderId", -1)
        self.symbol: str = raw.get("symbol", "")
        self.status: str = raw.get("status", "")
        self.side: str = raw.get("side", "")
        self.order_type: str = raw.get("type", "")
        self.orig_qty: str = raw.get("origQty", "0")
        self.executed_qty: str = raw.get("executedQty", "0")
        self.avg_price: str = raw.get("avgPrice", "0")
        self.price: str = raw.get("price", "0")

    def print_summary(self) -> None:
        print("\n" + "=" * 52)
        print("  ORDER RESPONSE")
        print("=" * 52)
        print(f"  Order ID      : {self.order_id}")
        print(f"  Symbol        : {self.symbol}")
        print(f"  Side          : {self.side}")
        print(f"  Type          : {self.order_type}")
        print(f"  Status        : {self.status}")
        print(f"  Orig Qty      : {self.orig_qty}")
        print(f"  Executed Qty  : {self.executed_qty}")
        print(f"  Avg Price     : {self.avg_price}")
        if self.price and self.price != "0":
            print(f"  Limit Price   : {self.price}")
        print("=" * 52)
        if self.status in ("FILLED", "PARTIALLY_FILLED", "NEW"):
            print("  ✅  Order submitted successfully!")
        else:
            print(f"  ⚠️  Order status: {self.status}")
        print("=" * 52 + "\n")


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float | str,
    price: float | str | None = None,
    stop_price: float | str | None = None,
) -> OrderResult:
    """Validate inputs, print a request summary, then place an order."""

    # --- Validate ---
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    # --- Print request summary ---
    print("\n" + "-" * 52)
    print("  ORDER REQUEST SUMMARY")
    print("-" * 52)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price:
        print(f"  Price      : {price}")
    if stop_price:
        print(f"  Stop Price : {stop_price}")
    print("-" * 52 + "\n")

    logger.debug(
        "Order request | symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    try:
        raw = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except BinanceClientError as exc:
        logger.error("API error placing order: %s", exc)
        print(f"\n  ❌  API Error {exc.code}: {exc.message}\n")
        raise
    except ConnectionError as exc:
        logger.error("Network failure placing order: %s", exc)
        print(f"\n  ❌  Network Error: {exc}\n")
        raise
    except Exception as exc:
        logger.exception("Unexpected error placing order: %s", exc)
        print(f"\n  ❌  Unexpected error: {exc}\n")
        raise

    result = OrderResult(raw)
    result.print_summary()
    return result
