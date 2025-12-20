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

<br>

## 🧠 One-Line Explanation
SROAD monitors e-commerce orders in real time, detects anomalies or important patterns,
and visualizes insights instantly through a live dashboard.

<br>

## 👶 Explain Like I’m 10
Imagine a smart robot watching every order in an online shop.
It tells you how much money you’re making and warns you if something strange happens — automatically.

<br>

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

<br>

## 💡 The Solution — What I Built

SROAD is a fully automated, real-time data pipeline that:
- Streams live orders using **Apache Kafka**
- Stores data in a cloud data lake (**Amazon S3**)
- Analyzes data using **serverless SQL (Amazon Athena)**
- Detects anomalies automatically
- Explains insights using an **AI agent (LLaMA)**
- Visualizes everything in a **live Streamlit dashboard**

<br>

## 🏗️ System Architecture (How It Works)

1. Orders arrive from Shopify or a synthetic generator  
2. Kafka streams events in real time  
3. Kafka consumers write data to Amazon S3  
4. AWS Glue catalogs schemas  
5. Athena runs analytical queries  
6. AI agent interprets anomalies  
7. Streamlit displays live insights  

<br>

## ⚙️ Installation & Setup

### Step 1: Clone the repository
```bash
git clone https://github.com/Abhinav-source2/SROAD.git
cd SROAD
````

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the system

```bash
docker-compose up
```

<br>

## 📈 Results & Impact

* **Near real-time operational visibility**
  Orders and revenue metrics are available within seconds instead of hours.

* **Automated anomaly detection**
  High-value or suspicious transactions are flagged immediately.

* **Zero manual reporting**
  No spreadsheets or delayed reports — everything updates automatically.

* **Scales with data growth**
  Designed to handle increasing order volume without re-architecture.

<br>

## 📚 What I Learned

* Real-time data engineering
* Cloud-native architectures
* Kafka-based streaming pipelines
* Serverless analytics on AWS
* Infrastructure automation
* AI integration into analytics systems

<br>

## 🔮 Future Improvements

* ML-based anomaly detection (LSTM, Isolation Forest)
* Revenue forecasting
* CI/CD automation
* Kubernetes deployment
* Advanced observability
* RAG-powered AI insights

<br>

## ⭐ Why This Project Is Resume-Worthy

This project demonstrates:

* End-to-end system design
* Production-grade data engineering
* Cloud architecture expertise
* Streaming + batch processing
* Infrastructure automation
* AI-assisted analytics

### 🧾 ATS Keywords

Kafka, AWS, Data Engineering, Streaming, Terraform, Docker, SQL, Python, AI

<br>

## 👤 Authors

**Abhinav Jajoo**
**Chaitanya Aggarwal**



I’m done fixing — this is the **final answer**.
```
