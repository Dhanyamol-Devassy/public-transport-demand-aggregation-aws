import pandas as pd

# Load raw CSVs from Kaggle dataset
temp = pd.read_csv("data/weather/raw/temperature.csv")
hum = pd.read_csv("data/weather/raw/humidity.csv")
press = pd.read_csv("data/weather/raw/pressure.csv")
wind = pd.read_csv("data/weather/raw/wind_speed.csv")

# Extract only New York columns
df = pd.DataFrame({
    "datetime": pd.to_datetime(temp["datetime"]),
    "temperature": temp["New York"],
    "humidity": hum["New York"],
    "pressure": press["New York"],
    "wind_speed": wind["New York"]
})

# Add partitioning
df["date"] = df["datetime"].dt.date
df["hour"] = df["datetime"].dt.hour

# Save cleaned dataset
df.to_csv("data/weather/nyc_weather.csv", index=False)
print("NYC weather data saved at data/weather/nyc_weather.csv")
