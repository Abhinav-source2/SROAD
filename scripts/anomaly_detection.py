import boto3
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# ================================
#  CONFIG
# ================================
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
ATHENA_DB = os.getenv("ATHENA_DATABASE", "sroad_analytics")
ATHENA_OUTPUT = os.getenv("ATHENA_OUTPUT_LOCATION", "s3://sroad-athena-results-2/")

athena = boto3.client("athena", region_name=AWS_REGION)

# ================================
#  Athena Helper
# ================================
def run_athena(sql: str) -> pd.DataFrame:
    """Runs Athena query and returns DataFrame."""
    res = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DB},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    qid = res["QueryExecutionId"]

    # Polling
    while True:
        status = athena.get_query_execution(QueryExecutionId=qid)["QueryExecution"]["Status"]["State"]
        if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break

    if status != "SUCCEEDED":
        raise Exception("Athena query failed")

    result = athena.get_query_results(QueryExecutionId=qid)
    cols = [c["Label"] for c in result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]
    rows = [
        [d.get("VarCharValue") for d in r["Data"]]
        for r in result["ResultSet"]["Rows"][1:]
    ]

    df = pd.DataFrame(rows, columns=cols)

    # Convert numeric columns
    for c in df.columns:
        try: df[c] = pd.to_numeric(df[c])
        except: pass

    return df

# ================================
#  Anomaly Detection
# ================================
def detect_anomalies(series: pd.Series):
    """Z-score anomaly detection."""
    series = series.dropna().astype(float)
    if len(series) < 3:
        return []

    mean = series.mean()
    std = series.std() or 1
    z = (series - mean) / std
    anomalies = z[abs(z) > 2.5].index.tolist()

    return anomalies

# ================================
#  MAIN EXECUTION
# ================================
def main():
    print("🔥 Running daily anomaly detection...")

    # Last 7 days revenue
    sql = """
        SELECT date(order_date_parsed) AS day,
               SUM(total_amount) AS revenue
        FROM unified_orders
        WHERE order_date_parsed >= date(now() - interval '7' day)
        GROUP BY 1
        ORDER BY 1;
    """

    df = run_athena(sql)

    if df.empty:
        print("⚠ No data returned.")
        return

    df["revenue"] = pd.to_numeric(df["revenue"])

    anomalies = detect_anomalies(df["revenue"])

    output = {
        "timestamp": str(datetime.utcnow()),
        "data": df.to_dict(orient="records"),
        "anomalies": anomalies,
    }

    # Save output to local folder inside container
    os.makedirs("/app/output", exist_ok=True)
    with open("/app/output/anomalies.json", "w") as f:
        json.dump(output, f, indent=4)

    print("✅ Anomaly detection completed.")
    print("📁 Saved to /app/output/anomalies.json")

if __name__ == "__main__":
    main()
