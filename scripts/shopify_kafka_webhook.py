import os
import hmac
import hashlib
import base64
import json
import logging
import time
from flask import Flask, request, abort, jsonify
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaError

# -------------------------------
# CONFIGURATION
# -------------------------------
SHOPIFY_WEBHOOK_SECRET = "5c1326f57ca1397ff07b778ce42d1cdbd48ad1953a09d11c7e2e3ca354d47916"
KAFKA_BROKER = "127.0.0.1:9092"  # ✅ fixed to IPv4
KAFKA_TOPIC = "shopify_orders"
DEBUG_MODE = True  # keep True while testing

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("shopify-webhook")

# -------------------------------
# CONNECT TO KAFKA (with retry)
# -------------------------------
def create_producer():
    for attempt in range(10):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
            )
            log.info("✅ Connected to Kafka at %s", KAFKA_BROKER)
            return producer
        except NoBrokersAvailable:
            log.warning("⚠️ Kafka broker not available yet. Retrying (%d/10)...", attempt + 1)
            time.sleep(3)
    log.error("❌ Could not connect to Kafka. Please ensure it’s running on 127.0.0.1:9092")
    return None

producer = create_producer()

# -------------------------------
# VERIFY SHOPIFY SIGNATURE
# -------------------------------
def verify_webhook(data, hmac_header):
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed_hmac, hmac_header)

# -------------------------------
# HEALTH CHECK ENDPOINT
# -------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    kafka_status = "connected" if producer else "not connected"
    return jsonify({
        "status": "running",
        "kafka": kafka_status,
        "topic": KAFKA_TOPIC
    }), 200

# -------------------------------
# SHOPIFY ORDER WEBHOOK
# -------------------------------
@app.route("/webhook/orders", methods=["POST"])
def orders_webhook():
    data = request.get_data()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

    if not DEBUG_MODE and not verify_webhook(data, hmac_header):
        log.warning("❌ Invalid Shopify signature. Aborting.")
        abort(401)

    order_data = request.get_json(force=True)
    log.info("✅ Webhook received: %s", json.dumps(order_data, indent=2)[:400])

    if producer:
        try:
            producer.send(KAFKA_TOPIC, order_data)
            producer.flush()
            log.info("📦 Sent order to Kafka topic '%s'", KAFKA_TOPIC)
        except KafkaError as e:
            log.error("⚠️ Failed to send to Kafka: %s", e)
    else:
        log.error("🚫 No Kafka producer available.")

    return jsonify({"status": "OK"}), 200

# -------------------------------
# RUN FLASK
# -------------------------------
if __name__ == "__main__":
    log.info("🚀 Starting Flask + Kafka webhook bridge on port 5000...")
    app.run(host="0.0.0.0", port=5000)
