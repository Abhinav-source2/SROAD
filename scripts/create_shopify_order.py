#!/usr/bin/env python3
"""
shopify_order_simulator_s3.py

- Creates synthetic orders via Shopify Admin API (orders.json)
- For each created order, uploads one JSON file to S3:
  s3://<S3_BUCKET>/orders/year=YYYY/month=MM/day=DD/<order_id>.json
- Also appends a local audit file orders_data.jsonl (one JSON per line)
- Uses retries and simple exponential backoff for resiliency.
"""

import os
import time
import json
import random
import logging
import uuid
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

import boto3
from botocore.exceptions import ClientError

# Load .env if present
load_dotenv()

# -------------------------
# Config (prefer env vars)
# -------------------------
STORE_BASE = os.getenv("SHOPIFY_STORE_BASE", "").rstrip("/")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "")

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "sroad-data-2")


if not STORE_BASE or not ACCESS_TOKEN:
    raise SystemExit("Please set SHOPIFY_STORE_BASE and SHOPIFY_ACCESS_TOKEN in env or .env")

# -------------------------
# HTTP & AWS clients
# -------------------------
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

s3_client = boto3.client("s3", region_name=AWS_REGION)

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    filename="shopify_orders.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# -------------------------
# Product catalog + metadata
# -------------------------
PRODUCTS = [
    # Clothing
    {"title": "Cotton Hoodie", "category": "Clothing", "price": 1199.0},
    {"title": "Slim Fit Denim Jeans", "category": "Clothing", "price": 1499.0},
    {"title": "Graphic T-Shirt", "category": "Clothing", "price": 499.0},
    {"title": "Casual Linen Shirt", "category": "Clothing", "price": 899.0},

    # Electronics
    {"title": "Wireless Earbuds", "category": "Electronics", "price": 2199.0},
    {"title": "Bluetooth Speaker", "category": "Electronics", "price": 1799.0},
    {"title": "Smartwatch X3", "category": "Electronics", "price": 3499.0},
    {"title": "USB-C Power Bank 10,000mAh", "category": "Electronics", "price": 1299.0},

    # Home & Lifestyle
    {"title": "Desk Lamp", "category": "Home Decor", "price": 699.0},
    {"title": "Aroma Diffuser", "category": "Home Decor", "price": 999.0},
    {"title": "Yoga Mat Pro", "category": "Fitness", "price": 799.0},
    {"title": "Ceramic Coffee Mug Set", "category": "Home Essentials", "price": 499.0},

    # Accessories
    {"title": "Laptop Stand", "category": "Accessories", "price": 899.0},
    {"title": "Leather Wallet", "category": "Accessories", "price": 599.0},
    {"title": "Analog Wrist Watch", "category": "Accessories", "price": 1299.0},

    # Footwear
    {"title": "Running Shoes", "category": "Footwear", "price": 1999.0},
    {"title": "Casual Sneakers", "category": "Footwear", "price": 1799.0},
    {"title": "Formal Leather Shoes", "category": "Footwear", "price": 2499.0},

    # Bags
    {"title": "Travel Backpack", "category": "Bags", "price": 1299.0},
    {"title": "Laptop Messenger Bag", "category": "Bags", "price": 1099.0},
]

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Netbanking", "COD"]
STATES_CITIES = [
    ("Rajasthan", "Jaipur"),
    ("Maharashtra", "Mumbai"),
    ("Delhi", "New Delhi"),
    ("Karnataka", "Bangalore"),
    ("West Bengal", "Kolkata"),
    ("Tamil Nadu", "Chennai"),
    ("Gujarat", "Ahmedabad"),
    ("Telangana", "Hyderabad"),
    ("Punjab", "Ludhiana"),
    ("Kerala", "Kochi"),
]

LOCAL_AUDIT_FILE = "orders_data.jsonl"

# -------------------------
# Utilities
# -------------------------
def random_customer():
    cust_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
    email = f"{cust_id.lower()}@example.com"
    return cust_id, email

def random_order_id():
    return f"ORD-{uuid.uuid4().hex[:10].upper()}"

def generate_order_payload():
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 3)
    payment_method = random.choice(PAYMENT_METHODS)
    state, city = random.choice(STATES_CITIES)
    cust_id, email = random_customer()

    subtotal = product["price"] * quantity
    discount = round(random.uniform(0.05, 0.25) * subtotal, 2)
    total = round(subtotal - discount, 2)

    # Shopify expects line_items to have variant ids in prod setups but title+price works for dev store
    order_payload = {
        "order": {
            # We include a client-side ID in "note_attributes" to help dedupe if needed
            "note_attributes": [{"name": "sim_id", "value": random_order_id()}],
            "email": email,
            "financial_status": "paid" if payment_method != "COD" else "pending",
            "fulfillment_status": random.choice(["fulfilled", "pending"]),
            "send_receipt": False,
            "send_fulfillment_receipt": False,
            "tags": f"{product['category']},{payment_method},{state}",
            "note": f"Auto-generated synthetic order for {product['title']}",
            "line_items": [
                {
                    "title": product["title"],
                    "price": str(product["price"]),
                    "quantity": quantity
                }
            ],
            "shipping_address": {
                "first_name": "Test",
                "last_name": "Buyer",
                "address1": f"{random.randint(10, 999)} Market Road",
                "city": city,
                "province": state,
                "country": "India",
                "zip": str(random.randint(100000, 999999))
            },
            "total_price": str(total),
            "subtotal_price": str(subtotal),
            "total_discounts": str(discount),
            "currency": "INR"
        }
    }
    return order_payload

# -------------------------
# Networking helpers with retries
# -------------------------
def post_with_retries(url, headers, json_payload, max_retries=3, base_delay=1.0):
    attempt = 0
    while attempt < max_retries:
        try:
            resp = requests.post(url, headers=headers, json=json_payload, timeout=15)
            return resp
        except requests.RequestException as e:
            attempt += 1
            wait = base_delay * (2 ** (attempt - 1))
            logging.warning("Request error (attempt %d/%d): %s — sleeping %.1fs", attempt, max_retries, e, wait)
            time.sleep(wait)
    raise RuntimeError("Failed to POST after retries")

def s3_put_json(bucket, key, data, max_retries=3):
    body = json.dumps(data, default=str)
    attempt = 0
    while attempt < max_retries:
        try:
            s3_client.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))
            return True
        except ClientError as e:
            attempt += 1
            wait = 1.0 * (2 ** (attempt - 1))
            logging.warning("S3 put_object error (attempt %d/%d): %s — sleeping %.1fs", attempt, max_retries, e, wait)
            time.sleep(wait)
    logging.error("Failed to upload to S3 after %d attempts: s3://%s/%s", max_retries, bucket, key)
    return False

# -------------------------
# Core functions
# -------------------------
def save_local_audit(order_obj):
    """Append one JSON line to local orders_data.jsonl for audit"""
    try:
        with open(LOCAL_AUDIT_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(order_obj, default=str) + "\n")
    except Exception as e:
        logging.exception("Failed to write local audit file: %s", e)

def upload_order_to_s3_by_order(order_obj):
    """
    Upload single order JSON to S3 with partitioned key:
    orders/year=YYYY/month=MM/day=DD/<order_id>.json
    """
    # prefer Shopify's created_at if present
    created_at = order_obj.get("created_at")
    if created_at:
        try:
            # attempt to parse created_at into datetime
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc)
        except Exception:
            dt = datetime.utcnow()
    else:
        dt = datetime.utcnow()

    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")

    # prefer numeric Shopify ID if present
    order_id = order_obj.get("id")
    if not order_id:
        # fallback to note_attributes sim_id or generate uuid
        sim_id = None
        for na in order_obj.get("note_attributes", []):
            if na.get("name") == "sim_id":
                sim_id = na.get("value")
        order_id = sim_id or f"ORD-{uuid.uuid4().hex[:12].upper()}"

    key = f"orders/year={year}/month={month}/day={day}/{order_id}.json"
    ok = s3_put_json(S3_BUCKET, key, order_obj)
    if ok:
        logging.info("Uploaded to s3://%s/%s", S3_BUCKET, key)
    return ok

def create_order_and_store():
    payload = generate_order_payload()
    url = f"{STORE_BASE}/orders.json"

    try:
        resp = post_with_retries(url, HEADERS, payload, max_retries=4)
    except Exception as e:
        logging.exception("Failed to POST order to Shopify: %s", e)
        return False

    if resp is None:
        logging.error("No response from Shopify")
        return False

    try:
        if resp.status_code in (200, 201):
            data = resp.json()
            # Shopify returns top-level 'order' object
            order_obj = data.get("order") if isinstance(data, dict) else data
            if not isinstance(order_obj, dict):
                logging.error("Unexpected Shopify response payload structure: %s", type(data))
                return False

            # local audit
            save_local_audit(order_obj)

            # upload to s3 (one file per order)
            uploaded = upload_order_to_s3_by_order(order_obj)
            if uploaded:
                logging.info("✅ Created & uploaded order %s", order_obj.get("id", "unknown"))
            else:
                logging.warning("Order created but failed S3 upload, will keep local record.")
            return True
        else:
            logging.error("Shopify API returned status %d: %s", resp.status_code, resp.text)
            return False
    except ValueError as e:
        logging.exception("Failed to parse Shopify JSON response: %s", e)
        return False

# -------------------------
# Main loop
# -------------------------
def main_loop(min_wait=45, max_wait=150):
    logging.info("🚀 Shopify Order Simulator (S3) started. Bucket=%s", S3_BUCKET)
    while True:
        try:
            ok = create_order_and_store()
            # Use a shorter wait if failed to avoid flooding
            wait_time = random.randint(min_wait, max_wait) if ok else 10
            logging.info("⏳ Sleeping %d seconds before next order", wait_time)
            time.sleep(wait_time)
        except KeyboardInterrupt:
            logging.info("🛑 Stopped by user")
            break
        except Exception as e:
            logging.exception("Unhandled exception in main loop: %s", e)
            time.sleep(10)

if __name__ == "__main__":
    main_loop()
