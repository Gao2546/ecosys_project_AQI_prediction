import os
import sys
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator 
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_folder)

# from write_csv_to_postgres import write_csv_to_postgres_main
# from write_df_to_postgres import write_df_to_postgres_main

spark_conn = os.environ.get("spark_default", "spark_default")
spark_master = "spark://spark:7077"
postgres_driver_jar = "/usr/local/spark/assets/jars/postgresql-42.2.6.jar"

# movies_file = "/usr/local/spark/assets/data/movies.csv"
# ratings_file = "/usr/local/spark/assets/data/ratings.csv"
th_airports = "/usr/local/spark/assets/data/th-airports.csv"
postgres_db = "jdbc:postgresql://postgres:5432/airflow"
postgres_user = "airflow"
postgres_pwd = "airflow"

# start_date = datetime(2024, 9, 13, 12, 10)
start_date = datetime.now()
now = datetime.now()

# default_args = {
#     "owner": "airflow",
#     'start_date': start_date,
#     'retries': 1,
#     'retry_delay': timedelta(seconds=5)
# }

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG('csv_extract_airflow_docker', default_args=default_args, schedule_interval=timedelta(1))

start = DummyOperator(task_id="start", dag=dag)

write_csv_to_postgres = SparkSubmitOperator(
    task_id='write_csv_to_postgres',
    # python_callable=write_csv_to_postgres_main,
    application="/usr/local/spark/applications/write_csv_to_postgres.py",
    retries=1,
    # retry_delay=timedelta(seconds=15),
    name="write-postgres",
    conn_id=spark_conn,
    verbose=1,
    conf={"spark.master": spark_master},
    application_args=[th_airports, postgres_db, postgres_user, postgres_pwd],
    jars=postgres_driver_jar,
    driver_class_path=postgres_driver_jar,
    dag=dag
)

write_df_to_postgres = SparkSubmitOperator(
    task_id='write_df_to_postgres',
    # python_callable=write_df_to_postgres_main,
    application="/usr/local/spark/applications/write_df_to_postgres.py",
    retries=1,
    # retry_delay=timedelta(seconds=15),
    name="read-postgres",
    conn_id=spark_conn,
    verbose=1,
    conf={"spark.master": spark_master},
    application_args=[postgres_db, postgres_user, postgres_pwd],
    jars=postgres_driver_jar,
    driver_class_path=postgres_driver_jar,
    dag=dag
)

end = DummyOperator(task_id="end", dag=dag)

start >> write_csv_to_postgres >> write_df_to_postgres >> end

# with DAG('csv_extract_airflow_docker', default_args=default_args, schedule_interval=timedelta(1), catchup=False) as dag:

#     write_csv_to_postgres = PythonOperator(
#         task_id='write_csv_to_postgres',
#         python_callable=write_csv_to_postgres_main,
#         retries=1,
#         retry_delay=timedelta(seconds=15))

#     write_df_to_postgres = PythonOperator(
#         task_id='write_df_to_postgres',
#         python_callable=write_df_to_postgres_main,
#         retries=1,
#         retry_delay=timedelta(seconds=15))
    
#     write_csv_to_postgres >> write_df_to_postgres 