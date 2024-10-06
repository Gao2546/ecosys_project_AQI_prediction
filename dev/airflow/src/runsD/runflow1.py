import requests
import json

# Airflow Webserver URL (replace with your actual Airflow URL and port)
airflow_url = "http://localhost:8085/api/v1/dags/{dag_id}/dagRuns"
dag_id = "demo"  # Replace with your actual DAG ID

# Optional: Pass configuration parameters to the DAG run
spark_master = "spark://spark:7077"
data = {
    "conf": {
        "spark.master":spark_master
    }
}

# Airflow authentication (if needed)
username = "airflow"
password = "airflow"

# Trigger the DAG using a POST request
response = requests.post(
    airflow_url.format(dag_id=dag_id),
    headers={"Content-Type": "application/json"},
    data=json.dumps(data),
    auth=(username, password)
)

# Check the response
if response.status_code == 200:
    print("DAG triggered successfully!")
else:
    print(f"Failed to trigger DAG: {response.text}")
