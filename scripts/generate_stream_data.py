import json
import time
import random
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
import logging
import socket
from dotenv import load_dotenv
import uuid

load_dotenv()

# ==========================================================
# ✅ CONFIGURATION
# ==========================================================
KAFKA_BROKER = "127.0.0.1:9092"   # Force IPv4 loopback
TOPIC = "synthetic_orders"
fake = Faker("en_IN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("stream-producer")

# ==========================================================
# ✅ FORCE IPv4 CONNECTION (Fixes ::1 / IPv6 issues)
# ==========================================================
socket.getaddrinfo = lambda *args, **kwargs: [
    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 9092))
]

# ==========================================================
# ✅ CONNECT TO KAFKA BROKER
# ==========================================================
def create_producer():
    for attempt in range(5):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=3,
                linger_ms=100,  # minor optimization
            )
            log.info("✅ Connected to Kafka at %s", KAFKA_BROKER)
            return producer
        except Exception as e:
            log.warning("⚠️ Kafka not reachable (attempt %d/5): %s", attempt + 1, e)
            time.sleep(3)
    log.error("❌ Could not connect to Kafka after multiple retries.")
    exit(1)

producer = create_producer()

# ==========================================================
# ✅ PRODUCT CATALOG (Expanded + Realistic)
# ==========================================================
PRODUCTS = [
    {"product_id": "PROD_101", "product_name": "Cotton Hoodie", "category": "Clothing", "price": 1299.0},
    {"product_id": "PROD_102", "product_name": "Slim Fit Jeans", "category": "Clothing", "price": 1599.0},
    {"product_id": "PROD_103", "product_name": "Wireless Earbuds", "category": "Electronics", "price": 2199.0},
    {"product_id": "PROD_104", "product_name": "Smartwatch X3", "category": "Electronics", "price": 3299.0},
    {"product_id": "PROD_105", "product_name": "Yoga Mat Pro", "category": "Fitness", "price": 799.0},
    {"product_id": "PROD_106", "product_name": "Desk Lamp", "category": "Home Decor", "price": 649.0},
    {"product_id": "PROD_107", "product_name": "Bluetooth Speaker", "category": "Electronics", "price": 1799.0},
    {"product_id": "PROD_108", "product_name": "Travel Backpack", "category": "Bags", "price": 1099.0},
    {"product_id": "PROD_109", "product_name": "Running Shoes", "category": "Footwear", "price": 1999.0},
    {"product_id": "PROD_110", "product_name": "Formal Leather Shoes", "category": "Footwear", "price": 2499.0},
    {"product_id": "PROD_111", "product_name": "Ceramic Coffee Mug Set", "category": "Home Essentials", "price": 499.0},
    {"product_id": "PROD_112", "product_name": "Leather Wallet", "category": "Accessories", "price": 599.0},
    {"product_id": "PROD_113", "product_name": "USB-C Power Bank 10,000mAh", "category": "Electronics", "price": 1299.0},
    {"product_id": "PROD_114", "product_name": "Analog Wrist Watch", "category": "Accessories", "price": 1299.0},
    {"product_id": "PROD_115", "product_name": "Casual Linen Shirt", "category": "Clothing", "price": 899.0},
]

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Netbanking", "COD"]
DELIVERY_STATUS = ["fulfilled", "pending", "cancelled"]
STATES = [
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

CHANNELS = ["Mobile App", "Website", "Instagram Store", "WhatsApp Store"]
DEVICES = ["Android", "iPhone", "Desktop", "Tablet"]

# ==========================================================
# ✅ UNIQUE + REALISTIC ORDER GENERATION
# ==========================================================
def generate_order(order_id: int):
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 4)
    base_price = product["price"] + random.uniform(-100, 150)  # slight fluctuation
    subtotal = base_price * quantity

    discount_rate = random.uniform(0.05, 0.25)
    discount = round(subtotal * discount_rate, 2)
    shipping_cost = round(random.uniform(0, 100), 2)
    total = round(subtotal - discount + shipping_cost, 2)

    payment_method = random.choice(PAYMENT_METHODS)
    delivery_status = random.choices(DELIVERY_STATUS, weights=[0.8, 0.15, 0.05])[0]
    state, city = random.choice(STATES)

    # Unique IDs
    unique_order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"
    customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"

    order = {
        "order_id": unique_order_id,
        "customer_id": customer_id,
        "order_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "category": product["category"],
        "quantity": quantity,
        "unit_price": round(base_price, 2),
        "discount": discount,
        "shipping_cost": shipping_cost,
        "total_amount": total,
        "currency": "INR",
        "payment_method": payment_method,
        "payment_status": "paid" if payment_method != "COD" else "pending",
        "delivery_status": delivery_status,
        "city": city,
        "state": state,
        "country": "India",
        "source": "synthetic",
        "channel": random.choice(CHANNELS),
        "device": random.choice(DEVICES),
        "tags": f"{product['category']},{payment_method},{state}",
        "customer_email": fake.email(),
        "customer_phone": fake.phone_number(),
        "customer_address": fake.address().replace("\n", ", "),
    }

    return order

# ==========================================================
# ✅ CONTINUOUS STREAM SIMULATION
# ==========================================================
if __name__ == "__main__":
    log.info("🚀 Starting enhanced synthetic order stream to Kafka topic '%s'...", TOPIC)
    order_counter = 1

    try:
        while True:
            order = generate_order(order_counter)
            producer.send(TOPIC, order)
            log.info("📦 Sent %s (%s | %s | ₹%.2f)",
                     order["order_id"], order["category"], order["state"], order["total_amount"])
            order_counter += 1
            time.sleep(random.uniform(1.0, 3.0))  # simulate real order rate
    except KeyboardInterrupt:
        log.info("🛑 Stream stopped by user.")
    except Exception as e:
        log.error("⚠️ Error during streaming: %s", e)
    finally:
        producer.close()
        log.info("🔚 Kafka producer closed.")
