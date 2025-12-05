import os
import pandas as pd
import random
import datetime
import boto3
import uuid
from faker import Faker
from dotenv import load_dotenv

load_dotenv()
fake = Faker("en_IN")

# ==========================================================
# ✅ CONFIGURATION
# ==========================================================
BUCKET_NAME = "sroad-data-2"
FOLDER = "batch"
FILE_NAME = "historical_orders.csv"
AWS_REGION = "ap-southeast-2"

AWS_ACCESS_KEY = "REDACTEDYQDU6WWUPBDZALUU"
AWS_SECRET_KEY = "LlusH3HTD4PJt9UCCRUct55SvYZ99PueCEgVTrdM"


if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise EnvironmentError("❌ AWS credentials not set.")

# ==========================================================
# ✅ PRODUCT & LOCATION DATA
# ==========================================================
products = [
    ("Apple iPhone 15 Pro", "Smartphones", "Apple", 1299),
    ("Samsung Galaxy S24 Ultra", "Smartphones", "Samsung", 1199),
    ("HP Pavilion 15", "Laptops", "HP", 899),
    ("Boat Airdopes 441", "Audio", "Boat", 49),
    ("Sony WH-1000XM5", "Audio", "Sony", 399),
    ("Noise ColorFit Pro 5", "Wearables", "Noise", 99),
    ("JBL Flip 6", "Speakers", "JBL", 139),
    ("Dell XPS 13", "Laptops", "Dell", 1099),
    ("Canon EOS 90D", "Cameras", "Canon", 999),
    ("Lenovo ThinkPad X1", "Laptops", "Lenovo", 1299),
    ("Mi Smart Band 8", "Wearables", "Xiaomi", 59),
    ("Asus ROG Strix", "Laptops", "Asus", 1499),
    ("LG OLED 55", "Television", "LG", 1699),
    ("OnePlus Buds Z3", "Audio", "OnePlus", 89),
    ("Apple MacBook Air M3", "Laptops", "Apple", 1599),
]

cities = [
    ("Jaipur", "Rajasthan", "India"),
    ("Delhi", "Delhi", "India"),
    ("Mumbai", "Maharashtra", "India"),
    ("Bangalore", "Karnataka", "India"),
    ("Pune", "Maharashtra", "India"),
    ("Kolkata", "West Bengal", "India"),
    ("Chennai", "Tamil Nadu", "India"),
    ("Ahmedabad", "Gujarat", "India"),
    ("Hyderabad", "Telangana", "India"),
    ("Lucknow", "Uttar Pradesh", "India"),
]

payment_methods = ["UPI", "Credit Card", "Debit Card", "Netbanking", "COD"]

# ==========================================================
# ✅ GENERATE RECORDS (2023 → 28 Oct 2025)
# ==========================================================
records = []
n_records = 90000

used_customer_ids = set()
used_order_ids = set()

start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2025, 12, 5)
total_days = (end_date - start_date).days

for i in range(n_records):
    product = random.choice(products)
    product_title, category, brand, price = product
    qty = random.randint(1, 5)
    discount = random.choice([0, 5, 10, 15, 20])
    subtotal = qty * price
    final = subtotal - (subtotal * discount / 100)

    # Unique IDs
    order_id = f"ORD_{uuid.uuid4().hex[:10].upper()}"
    while order_id in used_order_ids:
        order_id = f"ORD_{uuid.uuid4().hex[:10].upper()}"
    used_order_ids.add(order_id)

    customer_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"
    while customer_id in used_customer_ids:
        customer_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"
    used_customer_ids.add(customer_id)

    # Customer info
    customer_name = fake.name()
    email = f"{customer_id.lower()}@example.com"
    phone = f"+91-{random.randint(6000000000, 9999999999)}"
    city, state, country = random.choice(cities)

    # Random date between 2023-01-01 and 2025-10-28
    random_days = random.randint(0, total_days)
    order_date = start_date + datetime.timedelta(days=random_days)
    delivery_delay = random.randint(2, 10)
    delivery_date = order_date + datetime.timedelta(days=delivery_delay)

    # Status logic
    status = random.choices(
        ["Delivered", "Pending", "Cancelled"],
        weights=[0.8, 0.15, 0.05],
        k=1
    )[0]

    # Rating & returns
    rating = round(random.uniform(3.0, 5.0), 1) if status == "Delivered" else None
    is_returned = random.random() < 0.08 if status == "Delivered" else False

    payment_method = random.choice(payment_methods)
    if payment_method == "COD" and status == "Pending":
        status = "Pending"

    records.append({
        "order_id": order_id,
        "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_id": customer_id,
        "customer_name": customer_name,
        "email": email,
        "phone": phone,
        "product_id": f"PROD_{random.randint(1, len(products))}",
        "product_title": product_title,
        "product_category": category,
        "brand": brand,
        "quantity": qty,
        "unit_price": price,
        "total_amount": subtotal,
        "discount_percent": discount,
        "final_amount": round(final, 2),
        "payment_method": payment_method,
        "currency": "INR",
        "order_status": status,
        "shipping_city": city,
        "shipping_state": state,
        "shipping_country": country,
        "delivery_date": delivery_date.strftime("%Y-%m-%d %H:%M:%S"),
        "is_returned": is_returned,
        "rating": rating
    })

df = pd.DataFrame(records)
df.to_csv(FILE_NAME, index=False)
print(f"📁 Generated {len(df)} records → {FILE_NAME}")

# ==========================================================
# ✅ UPLOAD TO S3
# ==========================================================
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

s3.upload_file(FILE_NAME, BUCKET_NAME, f"{FOLDER}/{FILE_NAME}")
print(f"✅ Uploaded {FILE_NAME} → s3://{BUCKET_NAME}/{FOLDER}/{FILE_NAME}")
