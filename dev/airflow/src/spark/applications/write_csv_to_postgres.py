"""
Downloads the csv file from the URL. Creates a new table in the Postgres server.
Reads the file as a dataframe and inserts each record to the Postgres table. 
"""
import psycopg2
import os
import traceback
import logging
import pandas as pd
import urllib.request
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col, to_timestamp
from pyspark.sql.types import DoubleType

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')


# postgres_host = os.environ.get('postgres_host')
# postgres_database = os.environ.get('postgres_database')
# postgres_user = os.environ.get('postgres_user')
# postgres_password = os.environ.get('postgres_password')
# postgres_port = os.environ.get('postgres_port')
# dest_folder = os.environ.get('dest_folder')

spark = (SparkSession
         .builder
         .getOrCreate()
         )

destination_path = sys.argv[1]
postgres_db = sys.argv[2]
postgres_user = sys.argv[3]
postgres_pwd = sys.argv[4]

# dest_folder = os.environ.get('dest_folder')

# url = "https://raw.githubusercontent.com/dogukannulu/datasets/master/Churn_Modelling.csv"
# destination_path = f'{dest_folder}/churn_modelling.csv' 

th_airport_csv = (
    spark.read
    .format("csv")
    .option("header", True)
    .load(destination_path)
)



if __name__ == '__main__':
    (
        th_airport_csv.write
        .format("jdbc")
        .option("url", postgres_db)
        .option("dbtable", "public.th_airport")
        .option("user", postgres_user)
        .option("password", postgres_pwd)
        .mode("overwrite")
        .save()
    )