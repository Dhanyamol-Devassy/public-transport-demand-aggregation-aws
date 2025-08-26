from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.utils.dates import days_ago
import boto3

# Config
S3_BUCKET_RAW = "transportation-project-raw"
S3_BUCKET_WEATHER = "transportation-project-weather"
S3_BUCKET_PROCESSED = "transportation-project-processed"

ATHENA_DB = "transport_analytics"
ATHENA_OUTPUT = "s3://transportation-projects-athena-results/"

# Local paths (mounted into /opt/airflow/data via docker-compose)
LOCAL_TAXI_PATH = "/opt/airflow/data/raw/yellow_tripdata_2015-01.csv"
LOCAL_WEATHER_PATH = "/opt/airflow/data/weather/nyc_weather.csv"


def upload_to_s3(local_path, bucket, key):
    """Helper function to upload local file into S3."""
    s3 = boto3.client("s3")
    s3.upload_file(local_path, bucket, key)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1

}

with DAG(
    "transport_demand_pipeline",
    default_args=default_args,
    description="ETL pipeline for Taxi Demand + Weather aggregation",
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=["transport", "glue", "athena"],
) as dag:

    # Step 0a: Ingest taxi raw CSV into S3
    ingest_taxi_raw = PythonOperator(
        task_id="ingest_taxi_raw",
        python_callable=upload_to_s3,
        op_kwargs={
            "local_path": LOCAL_TAXI_PATH,
            "bucket": S3_BUCKET_RAW,
            "key": "taxi/raw/yellow_tripdata_2015-01.csv",
        },
    )

    # Step 0b: Ingest weather CSV into S3
    ingest_weather_raw = PythonOperator(
        task_id="ingest_weather_raw",
        python_callable=upload_to_s3,
        op_kwargs={
            "local_path": LOCAL_WEATHER_PATH,
            "bucket": S3_BUCKET_WEATHER,
            "key": "nyc_weather.csv",
        },
    )

    # Step 1: Glue Job - Taxi transform
    taxi_transform = GlueJobOperator(
        task_id="taxi_transform",
        job_name="taxi-transform-job",
        script_args={},
        aws_conn_id="aws_default",
        region_name="us-east-1",
    )

    # Step 2: Glue Job - Taxi + Weather join
    taxi_weather_join = GlueJobOperator(
        task_id="taxi_weather_join",
        job_name="taxi-weather-join-job",
        script_args={},
        aws_conn_id="aws_default",
        region_name="us-east-1",
    )

    # Step 3a: Crawler for hourly aggregates
    crawler_taxi_hourly = GlueCrawlerOperator(
        task_id="crawler_taxi_hourly",
        config={"Name": "taxi-hourly-crawler"},
        aws_conn_id="aws_default",
        region_name="us-east-1",
    )

    # Step 3b: Crawler for taxi + weather joined
    crawler_taxi_weather = GlueCrawlerOperator(
        task_id="crawler_taxi_weather",
        config={"Name": "taxi-weather-joined-crawler"},
        aws_conn_id="aws_default",
        region_name="us-east-1",
    )

    # Step 4: Athena validation query
    validate_joined = AthenaOperator(
        task_id="validate_joined",
        query=f"SELECT COUNT(*) AS total_records FROM {ATHENA_DB}.joined;",
        database=ATHENA_DB,
        output_location=ATHENA_OUTPUT,
        aws_conn_id="aws_default",
    )

    # DAG dependencies
    [ingest_taxi_raw, ingest_weather_raw] >> taxi_transform
    taxi_transform >> taxi_weather_join
    taxi_weather_join >> [crawler_taxi_hourly, crawler_taxi_weather]
    [crawler_taxi_hourly, crawler_taxi_weather] >> validate_joined
