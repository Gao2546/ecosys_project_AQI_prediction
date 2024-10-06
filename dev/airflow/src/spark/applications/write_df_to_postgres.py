import os
import sys
import logging
import psycopg2
import traceback
from create_df_and_modify import create_base_df, create_creditscore_df, create_exited_age_correlation, create_exited_salary_correlation

import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import SparkContext

# postgres_host = os.environ.get('postgres_host')
# postgres_database = os.environ.get('postgres_database')
# postgres_user = os.environ.get('postgres_user')
# postgres_password = os.environ.get('postgres_password')
# postgres_port = os.environ.get('postgres_port')

spark = (SparkSession
         .builder
         .getOrCreate()
         )
sc = spark.sparkContext
log4jLogger = sc._jvm.org.apache.log4j

LOGGER = log4jLogger.LogManager.getLogger(__name__)


LOGGER.info("Running Application")

# postgres_host = sys.argv[1]
# postgres_database = sys.argv[2]
# postgres_port = sys.argv[3]
# postgres_user = sys.argv[4]
# postgres_password = sys.argv[5]

postgres_db = sys.argv[1]
postgres_user = sys.argv[2]
postgres_pwd = sys.argv[3]

th_airport = (
    spark.read
    .format("jdbc")
    .option("url", postgres_db)
    .option("dbtable", "public.th_airport")
    .option("user", postgres_user)
    .option("password", postgres_pwd)
    .load()
)

th_airport_df = th_airport.alias("m")
th_airport_df_result = (
    th_airport_df
    .limit(10)
)
numbers = 1
for dd in th_airport_df_result.head(10):
    LOGGER.info(f"row N = {numbers} data = {dd}")
    numbers += 1

if __name__ == '__main__':
    th_airport_df_result.coalesce(1).write.format("csv").mode("overwrite").save(
    "/usr/local/spark/assets/data/output_postgres", header=True)