import os
import json
import logging
import boto3
import time
from kafka import KafkaConsumer
from datetime import datetime
from dotenv import load_dotenv
import socket

# ==========================================================
# 🔧 LOAD ENV VARIABLES
# ==========================================================
load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
TOPICS = [t.strip() for t in os.getenv("KAFKA_TOPICS", "shopify_orders,synthetic_orders").split(",")]
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "s3_consumer_group")
AUTO_OFFSET_RESET = os.getenv("AUTO_OFFSET_RESET", "latest")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 30))

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
AWS_ACCESS_KEY = os.getenv("REDACTED") or os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_REDACTED") or os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "sroad-data-2")


S3_FOLDER_MAP = {
    "shopify_orders": os.getenv("S3_FOLDER_SHOPIFY", "orders"),
    "synthetic_orders": os.getenv("S3_FOLDER_SYNTHETIC", "stream")
}

# ==========================================================
# 🧾 LOGGING SETUP
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("KafkaS3Consumer")

# ==========================================================
# 🌐 FORCE IPv4 CONNECTION (Fix IPv6 Kafka issue)
# ==========================================================
orig_getaddrinfo = socket.getaddrinfo
def ipv4_only_getaddrinfo(*args, **kwargs):
    results = orig_getaddrinfo(*args, **kwargs)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    return ipv4 or results
socket.getaddrinfo = ipv4_only_getaddrinfo

# ==========================================================
# ☁️ INIT S3 CONNECTION
# ==========================================================
try:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    log.info("✅ Connected to AWS S3 bucket '%s' in region %s", BUCKET_NAME, AWS_REGION)
except Exception as e:
    log.exception("❌ Could not connect to AWS S3: %s", e)
    exit(1)

# ==========================================================
# 🔗 CONNECT TO KAFKA BROKER
# ==========================================================
consumer = None
for attempt in range(8):
    try:
        consumer = KafkaConsumer(
            *TOPICS,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset=AUTO_OFFSET_RESET,
            enable_auto_commit=True,
            group_id=GROUP_ID,
            consumer_timeout_ms=2000
        )
        log.info("✅ Connected to Kafka broker %s (topics=%s)", KAFKA_BROKER, TOPICS)
        break
    except Exception as e:
        log.warning("⚠️ Kafka connection failed (attempt %d/8): %s", attempt + 1, e)
        time.sleep(2)

if not consumer:
    log.error("❌ Could not connect to Kafka after multiple retries.")
    exit(1)

# ==========================================================
# 🗂️ UPLOAD CLEAN JSON LINES TO S3 (Athena-friendly)
# ==========================================================
def upload_batch_to_s3(topic, batch):
    """Upload clean line-delimited JSON files to S3 (1 record per line)."""
    if not batch:
        return

    folder = S3_FOLDER_MAP.get(topic, "stream")
    filename = f"{topic}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.json"
    s3_key = f"{folder}/{filename}"

    try:
        # Convert batch to JSON Lines format (newline-delimited JSON)
        json_lines = "\n".join(json.dumps(record, ensure_ascii=False) for record in batch)

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json_lines.encode("utf-8")
        )

        log.info("📤 Uploaded %d records → s3://%s/%s", len(batch), BUCKET_NAME, s3_key)

    except Exception as e:
        log.exception("❌ Upload to S3 failed: %s", e)

# ==========================================================
# 🔁 MAIN CONSUMER LOOP
# ==========================================================
buffers = {t: [] for t in TOPICS}
log.info("🚀 Kafka → S3 consumer started (topics=%s, batch=%d)", TOPICS, BATCH_SIZE)

try:
    while True:
        for msg in consumer:
            try:
                topic = msg.topic
                value = msg.value
                if not isinstance(value, dict):
                    continue  # skip malformed messages

                # Add metadata
                value["_meta"] = {
                    "kafka_topic": topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "ingested_at": datetime.utcnow().isoformat()
                }

                buffers[topic].append(value)

                # When batch ready → upload
                if len(buffers[topic]) >= BATCH_SIZE:
                    upload_batch_to_s3(topic, buffers[topic])
                    buffers[topic] = []

            except Exception as e:
                log.warning("⚠️ Error processing message: %s", e)

        # Flush leftovers every loop
        for t, buf in list(buffers.items()):
            if buf:
                upload_batch_to_s3(t, buf)
                buffers[t] = []

except KeyboardInterrupt:
    log.info("🛑 Graceful shutdown...")
    for t, buf in buffers.items():
        if buf:
            upload_batch_to_s3(t, buf)
    consumer.close()
    log.info("✅ Consumer closed successfully.")
