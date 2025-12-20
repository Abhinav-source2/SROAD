🚀 SROAD
Streaming Real-time Operations & Anomaly Detection
<p align="center"> <img src="https://raw.githubusercontent.com/Abhinav-source2/SROAD/main/assets/sroad-architecture.png" alt="SROAD Architecture" width="85%"> </p> <p align="center"> <b>A production-grade, real-time data engineering platform for e-commerce analytics, anomaly detection, and AI-assisted insights.</b> </p> <p align="center"> <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen"/> <img src="https://img.shields.io/badge/Domain-Data%20Engineering-blue"/> <img src="https://img.shields.io/badge/Cloud-AWS-orange"/> <img src="https://img.shields.io/badge/Streaming-Kafka-black"/> <img src="https://img.shields.io/badge/Visualization-Streamlit-red"/> <img src="https://img.shields.io/badge/IaC-Terraform-purple"/> <img src="https://img.shields.io/badge/AI-LLaMA-lightgrey"/> </p>
🧠 One-Line Explanation

SROAD is a system that watches e-commerce orders in real time, finds important patterns or problems, and shows them instantly on a live dashboard.

👶 Explain Like I’m 10

Imagine a smart robot that watches every order in an online shop as soon as it happens, tells you how much money you’re making, and warns you if something strange happens — all automatically.

❓ Why Does This Project Exist? (Problem Statement)

Modern e-commerce businesses generate huge amounts of data every second:

orders

payments

locations

products

customers

🚨 The Problem

Most small and medium businesses:

rely on manual reports

check data hours or days later

miss fraud, spikes, drops, or trends

By the time they notice a problem, damage is already done.

❌ If This Problem Is Not Solved

Revenue drops go unnoticed

Fraud is detected too late

Marketing decisions are guesswork

Businesses lose money and trust

💡 The Solution — What I Built

SROAD is a fully automated, real-time data pipeline that:

Streams live orders using Kafka

Stores everything in a cloud data lake (S3)

Analyzes data instantly using serverless SQL (Athena)

Detects anomalies automatically

Explains insights using AI

Visualizes everything in a live dashboard

✨ What makes SROAD special

Combines real-time + historical data

Fully cloud-native & scalable

Zero manual reporting

AI-assisted explanations (LLaMA)

Infrastructure is automated & reproducible

✨ Key Features (With Real-Life Examples)
🔄 Real-Time Data Streaming

What: Orders are processed instantly as they happen

Why: No waiting for end-of-day reports

Example: A sudden sales spike appears on the dashboard within seconds

🗄️ Unified Cloud Data Lake

What: All data stored in Amazon S3

Why: One source of truth

Example: Yesterday’s and today’s sales analyzed together

📊 Serverless Analytics (SQL on S3)

What: Run SQL directly on raw data

Why: No database servers to manage

Example: “Which state generated the most revenue today?”

🚨 Anomaly Detection

What: Identifies unusually large orders or spikes

Why: Detect fraud or system issues early

Example: ₹1,00,000 order flagged instantly

🤖 AI-Assisted Analytics (LLaMA)

What: Conversational analytics & explanations

Why: Non-technical users can understand insights

Example: “Why did sales spike today?” → AI explains

📈 Interactive Dashboard

What: Live Streamlit dashboard

Why: Insights at a glance

Example: Real-time graphs updating automatically

🧰 Tech Stack (With Reasoning)
🐍 Python

Why Python? Simple, powerful, industry-standard

Solved: Streaming, AWS integration, analytics

Beginner View: Easy to read and write

🔥 Apache Kafka

What: Real-time event streaming platform

Why Kafka? Fast, fault-tolerant, scalable

Solved: Live order ingestion

☁️ Amazon S3

What: Cloud object storage

Why S3? Cheap, scalable, durable

Solved: Central data lake

📚 AWS Glue

What: Data catalog & schema manager

Why Glue? Automatic schema discovery

Solved: No manual table creation

🔍 Amazon Athena

What: Serverless SQL engine

Why Athena? Query data without databases

Solved: Fast analytics

📊 Streamlit

What: Python dashboard framework

Why Streamlit? Fast UI development

Solved: Live visualization

🐳 Docker

What: Containerization

Why Docker? Same behavior everywhere

Solved: Environment issues

🏗️ Terraform

What: Infrastructure as Code

Why Terraform? Reproducible cloud setup

Solved: Manual AWS setup errors

🧠 LLaMA AI Agent

What: Large Language Model

Why LLaMA? Explain anomalies in natural language

Solved: Human-friendly analytics

🏗️ System Architecture (Step-by-Step Flow)

Orders arrive from Shopify / synthetic generator

Kafka streams events in real time

Kafka consumer writes data to S3

AWS Glue detects schema

Athena runs SQL analytics

AI Agent interprets results

Streamlit shows live dashboard

🖼️ Visual Walkthrough
🔧 Architecture Diagram

Shows end-to-end data flow from ingestion → analytics → dashboard.

📊 Dashboard View

Displays:

Revenue trends

Top categories

State-wise sales

Anomalies

Behind the scenes, Athena queries S3 and updates graphs live.

⚙️ Installation & Setup (Beginner Friendly)
1️⃣ Clone Repository
git clone https://github.com/Abhinav-source2/SROAD.git
cd SROAD


➡️ Downloads the project to your system

2️⃣ Install Dependencies
pip install -r requirements.txt


➡️ Installs required Python libraries

3️⃣ Configure Environment

Create a .env file:

AWS_ACCESS_KEY_ID=****
AWS_SECRET_ACCESS_KEY=****
KAFKA_BROKER=localhost:9092


➡️ Stores secrets securely

4️⃣ Run with Docker
docker-compose up


➡️ Starts Kafka, consumers, dashboard, AI agent

▶️ How to Use the Project

Start the pipeline

Generate or stream orders

Open Streamlit dashboard

Watch real-time insights

Ask AI questions

🎯 Expected Output

Live graphs

Anomaly alerts

AI explanations

📈 Results & Impact

⏱️ Instant insights (seconds instead of hours)

🤖 Automated anomaly detection

📊 Zero manual reporting

☁️ Scales with data growth

💼 Why companies care:
Faster decisions = more revenue + less risk

📚 What I Learned

Real-time data engineering

Cloud-native architecture

Kafka streaming pipelines

Serverless analytics

Infrastructure as Code

AI integration

Production-grade system design

🔮 Future Improvements

ML-based anomaly detection (LSTM, Isolation Forest)

Forecasting & prediction

CI/CD pipelines

Kubernetes deployment

Advanced observability

RAG-based AI analytics

👥 Who Should Use This?

🎓 Students learning data engineering

👨‍💻 Developers building pipelines

🏢 E-commerce companies

👔 Recruiters evaluating real projects

⭐ Why This Project Is Resume-Worthy
✅ Skills Demonstrated

Data Engineering

Cloud Architecture

Kafka Streaming

AWS (S3, Glue, Athena)

Docker & Terraform

AI Integration

System Design

🧾 ATS Keywords

Kafka, AWS, Data Lake, Streaming, Terraform, Docker, SQL, Python, AI, Anomaly Detection

🧠 Engineering Depth

This project proves I can:

Design real-world systems

Handle scale

Automate infrastructure

Think like a production engineer

👨‍💻 Authors

Abhinav Jajoo
Chaitanya Aggarwal
