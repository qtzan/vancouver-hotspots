import pandas as pd

METRICS_PATH = "data_processed/neighbourhood_monthly_metrics_complete.csv"
FORECAST_PATH = "data_processed/neighbourhood_forecasts_6mo.csv"
OUT_PATH = "data_processed/neighbourhood_metrics_plus_forecast.csv"

def main():
    m = pd.read_csv(METRICS_PATH)
    f = pd.read_csv(FORECAST_PATH)

    m["date"] = pd.to_datetime(m["date"])
    f["date"] = pd.to_datetime(f["date"])

    # Keep only needed columns for Tableau
    m = m[["neighbourhood", "date", "incident_count", "rolling_3mo", "yoy_pct", "rank_yoy"]]

    # Add forecast columns for historical rows as NA
    m["forecast"] = pd.NA
    m["lower_95"] = pd.NA
    m["upper_95"] = pd.NA

    # For forecast rows, incident_count is NA (future), but forecast is filled
    f["incident_count"] = pd.NA
    f["rolling_3mo"] = pd.NA
    f["yoy_pct"] = pd.NA
    f["rank_yoy"] = pd.NA

    combined = pd.concat([m, f], ignore_index=True).sort_values(["neighbourhood", "date"])

    combined.to_csv(OUT_PATH, index=False)

    print("✅ Tableau file written:", OUT_PATH)
    print("Rows:", len(combined))

if __name__ == "__main__":
    main()