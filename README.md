<h1 align="center">🚀 SROAD</h1>

<p align="center">
  <b>Streaming Real-time Operations & Anomaly Detection</b><br>
  A production-grade, real-time data engineering platform for e-commerce analytics,
  anomaly detection, and AI-assisted insights.
</p>

<p align="center">
  <img src="assets/architecture.png" alt="SROAD Architecture" width="85%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen">
  <img src="https://img.shields.io/badge/Domain-Data%20Engineering-blue">
  <img src="https://img.shields.io/badge/Cloud-AWS-orange">
  <img src="https://img.shields.io/badge/Streaming-Kafka-black">
  <img src="https://img.shields.io/badge/Visualization-Streamlit-red">
  <img src="https://img.shields.io/badge/IaC-Terraform-purple">
  <img src="https://img.shields.io/badge/AI-LLaMA-lightgrey">
</p>

---

## 🧠 One-Line Explanation
**SROAD monitors e-commerce orders in real time, detects important patterns or anomalies, and visualizes insights instantly through a live dashboard.**

---

## 👶 Explain Like I’m 10
Imagine a smart robot watching every order in an online shop.  
It tells you how much money you’re making and warns you if something strange happens — automatically.

---

## ❓ Why Does This Project Exist? (Problem Statement)

Modern e-commerce businesses generate massive data every second:

- Orders  
- Payments  
- Products  
- Locations  
- Customers  

### 🚨 The Problem
Most small and medium businesses:
- Rely on manual reports  
- Check data hours or days later  
- Miss fraud, spikes, drops, or trends  

By the time problems are noticed, **damage is already done**.

### ❌ If This Problem Is Not Solved
- Revenue drops go unnoticed  
- Fraud is detected too late  
- Marketing decisions become guesswork  
- Businesses lose money and trust  

---

## 💡 The Solution — What I Built

**SROAD** is a fully automated, real-time data pipeline that:

- Streams live orders using **Apache Kafka**
- Stores all data in a cloud **data lake (Amazon S3)**
- Analyzes data using **serverless SQL (Athena)**
- Detects anomalies automatically
- Explains insights using an **AI agent (LLaMA)**
- Visualizes everything in a **live Streamlit dashboard**

### ✨ What Makes SROAD Special
- Combines **real-time + historical data**
- Fully **cloud-native & scalable**
- Zero manual reporting
- AI-assisted explanations
- Infrastructure is **automated & reproducible**

---

## ✨ Key Features

### 🔄 Real-Time Data Streaming
- Orders processed instantly as they happen  
- Example: Sudden sales spike visible within seconds  

### 🗄️ Unified Cloud Data Lake
- Single source of truth in Amazon S3  
- Example: Yesterday’s + today’s sales analyzed together  

### 📊 Serverless Analytics
- SQL queries directly on S3 using Athena  
- Example: “Which state generated the most revenue today?”  

### 🚨 Anomaly Detection
- Flags unusual order patterns  
- Example: ₹1,00,000 transaction flagged instantly  

### 🤖 AI-Assisted Analytics
- Conversational explanations of trends and anomalies  
- Example: “Why did sales spike today?”  

---

## 🧰 Tech Stack & Why It Was Chosen

| Technology | Purpose |
|----------|--------|
| Python | Core language for streaming, analytics, AI |
| Apache Kafka | Real-time data ingestion |
| Amazon S3 | Scalable cloud data lake |
| AWS Glue | Automatic schema discovery |
| Amazon Athena | Serverless SQL analytics |
| Streamlit | Interactive real-time dashboard |
| Docker | Environment consistency |
| Terraform | Infrastructure as Code |
| LLaMA | AI-based insight explanations |

---

## 🏗️ System Architecture (How It Works)

1. Orders arrive from Shopify / synthetic generator  
2. Kafka streams events in real time  
3. Kafka consumers write data to S3  
4. AWS Glue catalogs schemas  
5. Athena runs analytical queries  
6. AI agent interprets anomalies  
7. Streamlit displays live insights  

---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/Abhinav-source2/SROAD.git
cd SROAD
pip install -r requirements.txt
docker-compose up


---

## 📈 Results & Impact

- **Near real-time operational visibility**  
  Orders and revenue metrics are available within seconds instead of hours.

- **Automated anomaly detection**  
  High-value or suspicious transactions are flagged immediately.

- **Zero manual reporting**  
  No spreadsheets or delayed reports — everything updates automatically.

- **Scales with data growth**  
  Designed to handle increasing order volume without re-architecture.

---

## 📚 What I Learned

- Real-time data engineering principles  
- Designing cloud-native architectures  
- Kafka-based streaming pipelines  
- Serverless analytics using AWS Athena  
- Infrastructure automation using Terraform  
- Integrating AI into analytics systems  

---

## 🔮 Future Improvements

- Machine learning–based anomaly detection (LSTM, Isolation Forest)  
- Revenue forecasting and trend prediction  
- CI/CD pipeline automation  
- Kubernetes-based deployment  
- Advanced monitoring and observability  
- RAG-powered AI insights for deeper analytics  

---

## ⭐ Why This Project Is Resume-Worthy

This project demonstrates real-world engineering skills such as:

- End-to-end system design  
- Production-grade data engineering  
- Cloud architecture expertise  
- Streaming + batch data processing  
- Infrastructure automation  
- AI-assisted analytics  

### 🧾 ATS Keywords

`Kafka`, `AWS`, `Data Engineering`, `Streaming`, `Terraform`, `Docker`, `SQL`, `Python`, `AI`

---

## 👤 Authors

- **Abhinav Jajoo**  
- **Chaitanya Aggarwal**
