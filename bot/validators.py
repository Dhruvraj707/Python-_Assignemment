from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(Exception):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("Symbol cannot be empty.")
    if not s.isalnum():
        raise ValidationError(f"Symbol '{s}' must be alphanumeric (e.g. BTCUSDT).")
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(f"Side must be one of {VALID_SIDES}, got '{side}'.")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{order_type}'.")
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a positive number, got '{quantity}'.")
    if q <= 0:
        raise ValidationError(f"Quantity must be > 0, got {q}.")
    return q


def validate_price(price: str | float | None, order_type: str) -> float | None:
    if order_type in ("LIMIT", "STOP_MARKET"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a positive number, got '{price}'.")
        if p <= 0:
            raise ValidationError(f"Price must be > 0, got {p}.")
        return p
    return None


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("stopPrice is required for STOP_MARKET orders.")
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"stopPrice must be a positive number, got '{stop_price}'.")
        if sp <= 0:
            raise ValidationError(f"stopPrice must be > 0, got {sp}.")
        return sp
    return None
