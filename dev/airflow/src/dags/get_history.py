from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
from datetime import timedelta
import os

# Define a function to count users from Postgres
def count_users_from_postgres(**kwargs):
    # Establish connection to the Postgres database
    pg_hook = PostgresHook(postgres_conn_id='postgres_conn')
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    
    # Query to count users
    # cursor.execute("SELECT COUNT(*) FROM users;")
    cursor.execute("SELECT COUNT(*) FROM users WHERE status = %s;", (1,))
    user_count = cursor.fetchone()[0]
    
    # Store the count in a file (could be another storage like Redis or another DB)
    with open('/usr/local/airflow/trans/user_count.txt', 'w') as f:
        f.write(str(user_count))

    cursor.close()
    connection.close()

# Define DAG
default_args = {
    'start_date': datetime(2024, 10, 6),  # adjust start date
    'catchup': False
}

dag = DAG(
    'count_users_dag',
    default_args=default_args,
    schedule_interval=timedelta(seconds=30),  # Set the interval to every 30 seconds
    catchup=False
)

# Define the task
count_users_task = PythonOperator(
    task_id='count_users',
    python_callable=count_users_from_postgres,
    provide_context=True,
    dag=dag
)

count_users_task
