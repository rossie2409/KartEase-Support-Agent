

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.csv"


def get_order_status(order_id):
    """Return order details or a clear message if the order is missing."""

    if not order_id or not order_id.strip():
        return "Please provide an order ID."

    if not ORDERS_FILE.exists():
        return "Order database file was not found."

    with ORDERS_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            if (
                row.get("order_id", "").strip().lower()
                == order_id.strip().lower()
            ):
                return row

    return f"No order found with ID: {order_id}"


def lookup_order(order_id):
    """Compatibility wrapper for the existing support agent."""
    return get_order_status(order_id)


if __name__ == "__main__":
    order_id = input("Enter an order ID: ").strip()
    result = get_order_status(order_id)

    if isinstance(result, dict):
        print("\nOrder details:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(result)
