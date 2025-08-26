from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import to_date, hour
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
# Paths
taxi_path = "s3://transportation-project-processed/taxi/hourly/"
weather_path = "s3://transportation-project-weather/nyc_weather.csv"
output_path = "s3://transportation-project-processed/taxi/joined/"
# Load taxi parquet
taxi_df = spark.read.parquet(taxi_path)
# Explicitly select only needed taxi columns
taxi_df = taxi_df.select("date", "hour", "dayofweek", "trip_count", "avg_fare", "avg_distance")
# Load weather CSV
weather_df = spark.read.csv(weather_path, header=True, inferSchema=True)
# Add derived fields
weather_df = weather_df.withColumn("weather_date", to_date("datetime")) \
                       .withColumn("weather_hour", hour("datetime"))
# Select only required weather columns (rename for clarity)
weather_df = weather_df.select(
    "weather_date",
    "weather_hour",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed"
)
# Perform join on both date and hour
joined_df = taxi_df.join(
    weather_df,
    (taxi_df.date == weather_df.weather_date) & (taxi_df.hour == weather_df.weather_hour),
    how="inner"
)
# Drop duplicate join keys from weather
joined_df = joined_df.drop("weather_date", "weather_hour")
# Write result safely
joined_df.write.mode("overwrite").parquet(output_path)
