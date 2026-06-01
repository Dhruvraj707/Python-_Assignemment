from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("client")


class BinanceClientError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceFuturesClient:
    """Thin wrapper around the Binance USDT-M Futures REST API."""

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _get(self, path: str, params: dict | None = None, signed: bool = False) -> Any:
        params = params or {}
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params = self._sign(params)
        url = BASE_URL + path
        logger.debug("GET %s params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error on GET %s: %s", url, exc)
            raise ConnectionError(f"Cannot reach Binance testnet: {exc}") from exc
        return self._handle(resp)

    def _post(self, path: str, params: dict) -> Any:
        params["timestamp"] = int(time.time() * 1000)
        params = self._sign(params)
        url = BASE_URL + path
        logger.debug(
            "POST %s params=%s",
            url,
            {k: v for k, v in params.items() if k != "signature"},
        )
        try:
            resp = self.session.post(url, params=params, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error on POST %s: %s", url, exc)
            raise ConnectionError(f"Cannot reach Binance testnet: {exc}") from exc
        return self._handle(resp)

    @staticmethod
    def _handle(resp: requests.Response) -> Any:
        logger.debug("Response %s: %s", resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except ValueError:
            resp.raise_for_status()
            raise
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceClientError(data["code"], data.get("msg", "unknown"))
        resp.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ping(self) -> bool:
        """Return True if the testnet is reachable."""
        try:
            self._get("/fapi/v1/ping")
            return True
        except Exception:
            return False

    def get_exchange_info(self) -> dict:
        return self._get("/fapi/v1/exchangeInfo")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force
        if order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("stopPrice is required for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
            side,
            order_type,
            symbol,
            quantity,
            price,
            stop_price,
        )
        result = self._post("/fapi/v1/order", params)
        logger.info("Order placed successfully: orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result
