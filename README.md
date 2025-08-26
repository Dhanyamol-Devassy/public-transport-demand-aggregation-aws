# 🚖 Public Transport Demand Aggregation (Taxi + Weather)

[![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.9.2-blue)](https://airflow.apache.org/)  
[![AWS Glue](https://img.shields.io/badge/AWS-Glue-orange)](https://aws.amazon.com/glue/)  
[![Amazon Athena](https://img.shields.io/badge/AWS-Athena-green)](https://aws.amazon.com/athena/)  
[![Amazon QuickSight](https://img.shields.io/badge/AWS-QuickSight-yellow)](https://aws.amazon.com/quicksight/)  

This project demonstrates an **end-to-end ETL pipeline** for aggregating **NYC Taxi data with weather data** to analyze demand patterns.  
The workflow is fully **orchestrated with Apache Airflow**, using **AWS Glue for ETL**, **Athena for SQL analytics**, and **QuickSight for visualization**.  

---

### Key Components:
1. **Amazon S3** – storage for raw taxi & weather data, processed hourly aggregates, and Athena query results.  
2. **AWS Glue Jobs** – ETL transformation of taxi trips, and enrichment with weather data.  
3. **AWS Glue Crawlers** – automatic schema discovery of processed datasets.  
4. **Amazon Athena** – SQL queries on the curated datasets.  
5. **Amazon QuickSight** – dashboards for business insights.  
6. **Apache Airflow (Dockerized)** – workflow orchestration of ingestion, ETL, schema discovery, and validation queries.  

---

## 📂 Project Structure
```
public-transport-demand/
│── dags/
│   └── transport_demand_pipeline.py       # Airflow DAG for orchestration
│── etl/
│   ├── spark_transform.py                 # Glue job: transform taxi data
│   └── spark_join_weather.py              # Glue job: join taxi + weather
│── data/
│   ├── raw/                               # sample taxi CSV (not full dataset)
│   └── weather/                           # sample weather CSV
│── docs/
│   ├── Transport_Demand_Aggregation_Report.docx
│   └── architecture_diagram.png
│── docker-compose.yml                     # Airflow environment
│── requirements.txt                       # Python dependencies
│── README.md
```

---

## 📊 Dataset Sources
- **NYC Taxi Trip Data** (Kaggle, Jan 2015 sample)  
  🔗 https://www.kaggle.com/datasets/elemento/nyc-yellow-taxi-trip-data  
- **Historical NYC Weather Data** (NOAA / Kaggle)  
  🔗 https://www.kaggle.com/datasets/selfishgene/historical-hourly-weather-data  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Dhanyamol-Devassy/public-transport-demand-aggregation-aws.git
cd public-transport-demand
```

### 2️⃣ Start Airflow with Docker
```bash
docker compose up -d
```
Access the Airflow UI → http://localhost:8081  

### 3️⃣ Configure AWS
Ensure AWS credentials are available inside the container:    
- Set `AWS_ACCESS_KEY_ID`,`AWS_SECRET_ACCESS_KEY` and fernet-key in docker-compose.yml  

### 4️⃣ Run the Pipeline
- Trigger DAG: `transport_demand_pipeline`  
- Steps executed:  
  1. Ingest taxi & weather data into S3  
  2. Run Glue job to transform taxi trips (hourly aggregation)  
  3. Run Glue job to join taxi trips with weather data  
  4. Crawl processed S3 folders with Glue Crawlers  
  5. Run Athena validation query  

---

## 🔍 Sample Athena Queries
```sql
-- 1. Trips per Hour
SELECT hour, SUM(trip_count) AS total_trips
FROM transport_analytics.taxi_weather_joined
GROUP BY hour
ORDER BY hour;

-- 2. Trips vs Temperature Bands
SELECT CASE
         WHEN temperature < 278 THEN 'Cold'
         WHEN temperature BETWEEN 278 AND 293 THEN 'Mild'
         ELSE 'Hot'
       END AS temp_band,
       SUM(trip_count) AS trips
FROM transport_analytics.taxi_weather_joined
GROUP BY temp_band;

-- 3. Avg Fare vs Temperature
SELECT ROUND(temperature, 0) AS temp, AVG(avg_fare) AS avg_fare
FROM transport_analytics.taxi_weather_joined
GROUP BY ROUND(temperature, 0)
ORDER BY temp;
```

---

## 📈 QuickSight Dashboards
1. Trips by Hour (Line Chart)  
2. Trips by Day of Week (Bar Chart)  
3. Trips vs Temperature Band (Bar/Funnel)  
4. Trips vs Humidity (Line)  
5. Trips vs Pressure (Line)  
6. Avg Fare vs Temperature (Bar)  
7. Heatmap: Hour × Temperature Band  

---

## 💡 Insights & Findings
- Peak demand occurs during **rush hours (7–9 AM, 5–7 PM)**.  
- **Cold weather (< 5°C)** shows higher trip counts → taxis replace walking.  
- **Humidity spikes** correlate with fewer trips (likely rainy days).  
- Average fares are slightly **higher in cold conditions**.  
- Pressure has minimal direct impact, but combined with humidity indicates storms.  

---

## 💵 Cost Optimizations Implemented
- Used **S3 lifecycle policies** to move old data to **Glacier**.  
- Crawlers scheduled **on-demand**, not continuous.  
- Athena queries optimized with **partitions** on `date` and `hour`.  
- Glue jobs tuned with **smaller DPU configs** for batch ETL.  
- QuickSight dataset imported into **SPICE** to reduce repeated Athena costs.  

---

## 📘 Documentation
- 📄 [Project Report (DOCX)](docs/Transport_Demand_Aggregation_Report.docx)   

---

## ✨ Future Enhancements
- Add **event data** (sports, concerts) for demand forecasting.  
- Migrate Athena results into **Redshift** for advanced BI.  
- Automate with **CI/CD pipelines** (GitHub Actions).  
- Extend to **real-time streaming** with **Kinesis + Lambda**.  

---

## 👨‍💻 Author
**Dhanyamol Devassy**  
 
