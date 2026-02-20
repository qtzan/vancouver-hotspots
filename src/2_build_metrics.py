import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://postgres:Icey_Mech0204@localhost:1234/Vancouver_analytics"

def main():
    engine = create_engine(DB_URL)

    df = pd.read_sql(
        "SELECT * FROM crime_monthly_neighbourhood",
        engine
    )

    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
    )

    df = df.sort_values(["neighbourhood","date"])

    df["rolling_3mo"] = (
        df.groupby("neighbourhood")["incident_count"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0,drop=True)
    )

    df["yoy_pct"] = (
        df.groupby("neighbourhood")["incident_count"]
        .pct_change(periods=12)
    )

    df["rank_yoy"] = (
        df.groupby("date")["yoy_pct"]
        .rank(ascending=False)
    )

    df.to_csv("data_processed/neighbourhood_monthly_metrics.csv", index=False)

    print("Metrics built successfully.")
    print("Rows:", len(df))
    print("Neighbourhoods:", df["neighbourhood"].nunique())

if __name__ == "__main__":
    main()