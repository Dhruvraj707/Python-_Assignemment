#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceClientError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import ValidationError

load_dotenv()
logger = setup_logger("cli")

BANNER = r"""
  ╔══════════════════════════════════════════╗
  ║   Binance Futures Testnet Trading Bot    ║
  ╚══════════════════════════════════════════╝
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance USDT-M Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET (bonus)",
    )
    parser.add_argument(
        "--quantity", required=True, type=float,
        help="Order quantity (base asset)",
    )
    parser.add_argument(
        "--price", type=float, default=None,
        help="Limit price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price", dest="stop_price", type=float, default=None,
        help="Stop price (required for STOP_MARKET orders)",
    )
    parser.add_argument(
        "--api-key", default=None,
        help="Binance API key (overrides BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret", default=None,
        help="Binance API secret (overrides BINANCE_API_SECRET env var)",
    )
    return parser


def main() -> None:
    print(BANNER)

    parser = build_parser()
    args = parser.parse_args()

    # Resolve credentials: CLI flag > env var
    api_key = args.api_key or os.getenv("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        print(
            "  API credentials not found.\n"
            "    Set BINANCE_API_KEY and BINANCE_API_SECRET in a .env file,\n"
            "    or pass --api-key / --api-secret on the command line."
        )
        logger.error("Missing API credentials. Aborting.")
        sys.exit(1)

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        args.symbol, args.side, args.order_type, args.quantity, args.price, args.stop_price,
    )

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

        # Quick connectivity check
        if not client.ping():
            print("  Warning: Could not reach Binance testnet. Proceeding anyway…")
            logger.warning("Ping to testnet failed.")

        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )

    except ValidationError as exc:
        print(f"\n    Validation Error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(2)
    except BinanceClientError as exc:
        logger.error("API error: %s", exc)
        sys.exit(3)
    except ConnectionError as exc:
        logger.error("Network error: %s", exc)
        sys.exit(4)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Unexpected fatal error: %s", exc)
        print(f"\n    Unexpected error: {exc}\n")
        sys.exit(5)


if __name__ == "__main__":
    main()
