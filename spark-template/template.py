#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import argparse
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

################# Basic configs ################

SHUFFLE_PARTITIONS = 200
DEFAULT_PARALLELISM = 200
BROADCAST_TIMEOUT = 36000

ROOT_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

input_table = ''

output_table = ''

output_folder = ROOT_PATH + 'result/'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

OUTPUT_COLUMNS = [
  'query',
  'pv'
]
###############################################

################ Custom configs ###############

###############################################

################ I/O functions ################

def load_data(spark, table_name):
    sqlRead = """
    SELECT
        sq_query AS query
        ,query_pv AS pv
    FROM {}
    """.format(table_name)
    logging.info("Start loading data")
    df = spark.sql(sqlRead)\
         .dropna()
    return df

def load_key_word(spark, file_path):
    schema = StructType([
        StructField("word", StringType())
    ])
    df = spark.read.csv(file_path, schema=schema, sep='\t', header=True) \
                .dropna() \
                .dropDuplicates()
    return df

def clear_table(spark, table_name):
    sql = """
    truncate table {}
    """
    spark.sql(sql.format(table_name))
    return

###############################################

############### Custom functions ##############

###############################################

################ Main function ################

def process(args):
    spark = SparkSession.builder \
        .enableHiveSupport() \
        .config('hive.exec.dynamic.partition', 'true') \
        .config('hive.exec.dynamic.partition.mode', 'nonstrict') \
        .config('spark.io.compression.codec', 'lz4') \
        .config('spark.sql.shuffle.partitions', SHUFFLE_PARTITIONS) \
        .config('spark.default.parallelism', DEFAULT_PARALLELISM) \
        .config('spark.sql.broadcastTimeout', BROADCAST_TIMEOUT) \
        .getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')

    ### Read table
    df = load_data(spark, input_table)

    ### Write to hive table
    clear_table(spark, output_table)
    df.select(OUTPUT_COLUMNS).write.mode('append').insertInto(output_table)

    ### Write to local folder
    df.select(OUTPUT_COLUMNS).toPandas().to_csv(output_folder+'a.csv', sep = '\t', header = False, index = False, encoding = 'utf-8')

    logging.info("Stopping spark session..")
    spark.stop()
    return
###############################################

def main():
    parser = argparse.ArgumentParser(description='Test.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()
    process(args)
    return 0

if __name__ == '__main__':
    sys.exit(main())
