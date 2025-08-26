from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import hour, dayofweek, to_date

glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session

input_path = "s3://transportation-project-raw/taxi/raw/"
output_path = "s3://transportation-project-processed/taxi/hourly/"

df = spark.read.csv(input_path, header=True, inferSchema=True)

df = df.withColumn("date", to_date("tpep_pickup_datetime")) \
       .withColumn("hour", hour("tpep_pickup_datetime")) \
       .withColumn("dayofweek", dayofweek("tpep_pickup_datetime"))

agg_df = df.groupBy("date", "hour", "dayofweek") \
           .agg({"fare_amount": "avg", "trip_distance": "avg", "*": "count"}) \
           .withColumnRenamed("count(1)", "trip_count") \
           .withColumnRenamed("avg(fare_amount)", "avg_fare") \
           .withColumnRenamed("avg(trip_distance)", "avg_distance")

agg_df.write.mode("overwrite").parquet(output_path)
