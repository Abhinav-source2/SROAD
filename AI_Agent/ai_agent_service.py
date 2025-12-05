# ai_agent_service.py
# ✅ SROAD Agentic AI Microservice
# FastAPI + Ollama + Athena — cost-safe, debug-friendly

import os
import time
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import boto3
import pandas as pd
import requests

# --------------------------------------------------------
# 🔧 Load environment variables
# --------------------------------------------------------
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
ATHENA_DB = os.getenv("ATHENA_DATABASE", "sroad_analytics")
ATHENA_OUTPUT = os.getenv("ATHENA_OUTPUT_LOCATION")  # required: s3://bucket/prefix/
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

MAX_ROWS = int(os.getenv("MAX_ROWS", "200"))
MAX_BYTES_SCANNED = int(
    os.getenv("MAX_BYTES_SCANNED", str(1024 * 1024 * 1024))
)  # default 1 GB

FORBIDDEN = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT"}

# --------------------------------------------------------
# ✅ Logging
# --------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("sroad-agent")

log.info("Starting SROAD AI Agent service")
log.info("Region: %s | DB: %s | Output: %s", AWS_REGION, ATHENA_DB, ATHENA_OUTPUT)

# --------------------------------------------------------
# ✅ AWS Athena client
# --------------------------------------------------------
athena = boto3.client("athena", region_name=AWS_REGION)

# --------------------------------------------------------
# ✅ FastAPI App
# --------------------------------------------------------
app = FastAPI(title="SROAD Agentic AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# ✅ Request/Response Models
# --------------------------------------------------------
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    sql: str
    rows: int
    sample: List[Dict[str, Any]]
    explanation: str


# --------------------------------------------------------
# ✅ LLM Caller — Ollama
# --------------------------------------------------------
def call_llm(prompt: str) -> str:
    """Call Ollama once (non-streaming) and return plain text."""
    try:
        url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        log.debug("Calling LLM at %s", url)
        r = requests.post(url, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()

        # Typical Ollama response has 'response'
        if isinstance(data, dict) and isinstance(data.get("response"), str):
            text = data["response"]
        else:
            # Fallback: best-effort stringify
            text = json.dumps(data)

        text = text.strip()
        if not text:
            raise RuntimeError("Empty response from LLM")

        return text

    except Exception as e:
        log.exception("LLM call failed")
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")


# --------------------------------------------------------
# ✅ Generate SQL using LLM
# --------------------------------------------------------
def sql_from_question(question: str) -> str:
    """Turn natural language into a safe Athena SELECT query."""

    prompt = f"""
You are a SQL generator for AWS Athena (Presto).
Return ONLY a SELECT query against table {ATHENA_DB}.unified_orders.

Available columns:
order_id, order_timestamp, order_date_parsed, total_amount,
payment_method, category, quantity, unit_price,
city, state, channel, source

Rules:
- ALWAYS wrap order_timestamp or order_date_parsed in date() before filtering or grouping.
    Example: date(order_date_parsed)
- For date ranges, ALWAYS use:
    date(order_date_parsed) BETWEEN DATE 'YYYY-MM-DD' AND DATE 'YYYY-MM-DD'
- NEVER compare timestamp directly to strings.
- NEVER use NOW(), CURRENT_DATE(), INTERVAL, TIMESTAMPDIFF.
- ALWAYS include ORDER BY when asking for top/bottom results.
- ALWAYS append LIMIT {MAX_ROWS}.
- Output SQL only — no explanation.

User question:
\"\"\"{question}\"\"\"
"""

    raw = call_llm(prompt)
    log.info("LLM raw SQL candidate: %s", raw.replace("\n", " "))

    # Try to extract from first WITH or SELECT
    upper = raw.upper()
    start_idx: Optional[int] = None
    for token in ("WITH", "SELECT"):
        if token in upper:
            start_idx = upper.index(token)
            break

    sql = raw[start_idx:] if start_idx is not None else raw

    # Remove everything after first semicolon, if any
    sql = sql.split(";")[0].strip()

    # Basic safety check
    upper_sql = sql.upper()
    for word in FORBIDDEN:
        if word in upper_sql:
            log.error("Blocked unsafe SQL: %s", sql)
            raise HTTPException(
                status_code=400, detail=f"Blocked unsafe SQL keyword: {word}"
            )

    if "LIMIT" not in upper_sql:
        sql += f" LIMIT {MAX_ROWS}"

    log.info("Final generated SQL: %s", sql)
    return sql


# --------------------------------------------------------
# ✅ Athena runner
# --------------------------------------------------------
def run_athena(sql: str) -> pd.DataFrame:
    """Run SQL on Athena and return a DataFrame. Raises HTTPException on error."""

    if not ATHENA_OUTPUT:
        raise HTTPException(
            status_code=500,
            detail="Missing ATHENA_OUTPUT_LOCATION in environment (.env).",
        )

    try:
        start_resp = athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": ATHENA_DB},
            ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
        )
        qid = start_resp["QueryExecutionId"]
        log.info("Athena query started: %s", qid)
    except Exception as e:
        log.exception("Failed to start Athena query")
        raise HTTPException(status_code=500, detail=f"Failed to start Athena query: {e}")

    # Poll until finished
    while True:
        exe = athena.get_query_execution(QueryExecutionId=qid)
        status = exe["QueryExecution"]["Status"]["State"]
        if status in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(0.5)

    if status != "SUCCEEDED":
        reason = exe["QueryExecution"]["Status"].get("StateChangeReason", "")
        log.error("Athena failed: %s | reason: %s", status, reason)
        raise HTTPException(
            status_code=500,
            detail=f"Athena query failed: {status} {reason}",
        )

    # Cost guard
    scanned = exe["QueryExecution"].get("Statistics", {}).get("DataScannedInBytes", 0)
    log.info("Athena scanned %d bytes", scanned)
    if scanned and scanned > MAX_BYTES_SCANNED:
        raise HTTPException(
            status_code=400,
            detail=f"Query would scan {scanned} bytes, above MAX_BYTES_SCANNED={MAX_BYTES_SCANNED}",
        )

    # Fetch results
    try:
        results = athena.get_query_results(QueryExecutionId=qid, MaxResults=1000)
    except Exception as e:
        log.exception("Failed to fetch Athena results")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {e}")

    rows = results["ResultSet"]["Rows"]
    if not rows:
        return pd.DataFrame()

    # First row is header
    header = [c.get("VarCharValue") for c in rows[0]["Data"]]
    data_rows = []
    for row in rows[1:]:
        data_rows.append([c.get("VarCharValue") for c in row["Data"]])

    df = pd.DataFrame(data_rows, columns=header)

    # Try casting numeric columns
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            # leave as string
            pass

    return df


# --------------------------------------------------------
# ✅ Explain results using LLM
# --------------------------------------------------------
def explain_answer(question: str, sample: List[Dict[str, Any]]) -> str:
    prompt = f"""
User asked: "{question}"

Here are a few sample rows from the result (JSON):
{json.dumps(sample, indent=2)}

Explain the business insight in 3 sentences.
Do NOT mention SQL or database internals. Focus on revenue, customers, products, or regions.
"""

    try:
        return call_llm(prompt)
    except HTTPException as e:
        # If LLM fails, return a simple fallback message
        return f"(Explanation unavailable due to LLM error: {e.detail})"


# --------------------------------------------------------
# ✅ Main /ask endpoint
# --------------------------------------------------------
@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    log.info("Incoming question: %s", req.question)

    # 1) Generate SQL
    sql = sql_from_question(req.question)

    # 2) Execute Athena
    df = run_athena(sql)

    # 3) Take sample
    sample = df.head(10).to_dict(orient="records") if not df.empty else []

    # 4) Explain
    explanation = explain_answer(req.question, sample)

    return AskResponse(sql=sql, rows=len(df), sample=sample, explanation=explanation)


# --------------------------------------------------------
# ✅ Health check
# --------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "region": AWS_REGION,
        "database": ATHENA_DB,
        "output": ATHENA_OUTPUT,
        "llm_model": OLLAMA_MODEL,
    }
