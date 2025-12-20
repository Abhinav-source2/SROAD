<p align="center">
  <img src="assets/architecture.png" alt="SROAD Architecture" width="90%">
</p>

<h1 align="center">SROAD</h1>

<p align="center">
  <b>Streaming Real-time Operations & Anomaly Detection</b>
</p>

<p align="center">
  A cloud-native, real-time data engineering platform for e-commerce analytics,
  anomaly detection, and AI-assisted insights.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Domain-Data%20Engineering-blue">
  <img src="https://img.shields.io/badge/Streaming-Apache%20Kafka-black">
  <img src="https://img.shields.io/badge/Cloud-AWS-orange">
  <img src="https://img.shields.io/badge/Visualization-Streamlit-red">
  <img src="https://img.shields.io/badge/IaC-Terraform-purple">
  <img src="https://img.shields.io/badge/Container-Docker-blue">
</p>

---

## 📌 What Is This Project?

**SROAD** is an end-to-end system that ingests e-commerce order data in real time,
analyzes it instantly in the cloud, detects anomalies, and visualizes insights
through a live dashboard.

**In simple terms:**  
It watches every order as it happens and tells you what’s going on — immediately.

---

## ❓ Why Does This Project Exist? (Problem Statement)

Modern e-commerce businesses generate massive amounts of data every second:

- Orders
- Payments
- Products
- Locations
- Customers

### The Problem
Most small and medium businesses:
- Rely on manual or delayed reports
- Analyze data hours or days later
- Miss fraud, revenue drops, spikes, and trends

By the time issues are discovered, **the damage is already done**.

### If This Problem Is Not Solved
- Revenue drops go unnoticed
- Fraud is detected too late
- Marketing decisions become guesswork
- Businesses lose money and customer trust

---

## 💡 Solution — What I Built

SROAD is a **fully automated, real-time data pipeline** that:

1. Streams live order events using Apache Kafka  
2. Stores both real-time and historical data in Amazon S3  
3. Automatically catalogs data using AWS Glue  
4. Runs serverless SQL analytics with Amazon Athena  
5. Detects anomalies in transaction patterns  
6. Visualizes insights through a Streamlit dashboard  
7. Uses an AI agent (LLaMA-based) to explain anomalies and insights  

This system is **scalable, cloud-native, and production-ready**.

---

## 🏗️ System Architecture (How It Works)

1. **Data Sources**
   - Shopify orders
   - Synthetic order generator

2. **Streaming Layer**
   - Apache Kafka ingests events in real time

3. **Storage Layer**
   - Kafka consumers write data to Amazon S3 (Data Lake)

4. **Analytics Layer**
   - AWS Glue catalogs data schemas
   - Amazon Athena runs SQL queries directly on S3

5. **Intelligence Layer**
   - Rule-based anomaly detection
   - LLaMA-powered AI agent for explanations

6. **Visualization Layer**
   - Streamlit dashboard displays real-time insights

---

## ✨ Key Features

- Real-time data ingestion using Kafka
- Unified cloud data lake (batch + streaming)
- Serverless SQL analytics
- Automatic anomaly detection
- AI-assisted insight explanations
- Interactive real-time dashboard
- Dockerized and reproducible setup
- Infrastructure automated using Terraform

---

## 🧰 Tech Stack & Why It Was Chosen

| Technology | Purpose |
|----------|--------|
| Python | Core language for streaming, analytics, and AI |
| Apache Kafka | Real-time event streaming |
| Amazon S3 | Scalable cloud data lake |
| AWS Glue | Automatic schema detection |
| Amazon Athena | Serverless SQL analytics |
| Streamlit | Interactive dashboard |
| Docker | Environment consistency |
| Terraform | Infrastructure as Code |
| LLaMA (AI Agent) | Conversational analytics & explanations |

---

## 🖼️ Dashboard Overview

The Streamlit dashboard provides:
- Total revenue and order count
- Daily and hourly sales trends
- Top products and categories
- State-wise revenue analysis
- Anomaly previews for suspicious transactions

All visuals update dynamically using live Athena queries.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Abhinav-source2/SROAD.git
cd SROAD
2. Install Dependencies
bash
Copy code
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file:

env
Copy code
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
KAFKA_BROKER=localhost:9092
4. Run Using Docker
bash
Copy code
docker-compose up
▶️ How to Use
Start Kafka and consumers

Stream or generate order data

Data flows automatically to S3

Athena analyzes data

Dashboard updates in real time

AI agent explains anomalies

📈 Results & Impact
Near real-time visibility into sales
Faster anomaly detection
Zero manual reporting
Scales with increasing data volume
Demonstrates production-grade data engineering

📚 What I Learned
Designing real-time streaming systems

Cloud-native data lake architecture

Serverless analytics on AWS

Infrastructure automation using Terraform

Docker-based deployment

AI integration into analytics pipelines

🔮 Future Improvements
ML-based anomaly detection models

Revenue forecasting

CI/CD automation

Kubernetes deployment

Enhanced monitoring and observability

Advanced AI-driven recommendations

⭐ Why This Project Is Resume-Worthy
This project demonstrates:

Real-world data engineering skills

End-to-end system design

Cloud architecture expertise

Streaming data processing

Production-ready engineering mindset

ATS Keywords:
Kafka, AWS, Data Engineering, Streaming, Terraform, Docker, SQL, Python, AI

👤 Authors
Abhinav Jajoo
Chaitanya Aggarwal