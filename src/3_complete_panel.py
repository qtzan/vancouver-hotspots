import pandas as pd
import numpy as np


def main():
    df = pd.read_csv("data_processed/neighbourhood_monthly_metrics.csv")

    df["date"] = pd.to_datetime(df["date"])

    df["neighbourhood"] = df["neighbourhood"].astype("string").str.strip()
    df = df[df["neighbourhood"].notna() & (df["neighbourhood"] != "")]

    neighbourhoods = df["neighbourhood"].unique()
    date_range = pd.date_range(
        start="2016-01-01",
        end="2025-12-01",
        freq="MS"
    )

    full_index = pd.MultiIndex.from_product(
        [neighbourhoods, date_range],
        names=["neighbourhood", "date"]
    )

    full_df = (
        df.set_index(["neighbourhood", "date"])
          .reindex(full_index)
          .reset_index()
    )
    

    # Fill missing counts with 0
    full_df["incident_count"] = full_df["incident_count"].fillna(0)

    # Recalculate rolling + YoY on clean panel
    full_df = full_df.sort_values(["neighbourhood", "date"])

    full_df["rolling_3mo"] = (
        full_df.groupby("neighbourhood")["incident_count"]
               .rolling(window=3, min_periods=1)
               .mean()
               .reset_index(level=0, drop=True)
    )

    full_df["yoy_pct"] = (
        full_df.groupby("neighbourhood")["incident_count"]
               .pct_change(periods=12)
    )
    full_df["yoy_pct"] = full_df["yoy_pct"].replace([np.inf, -np.inf], np.nan)

    full_df["yoy_diff"] = (
        full_df.groupby("neighbourhood")["incident_count"]
           .diff(periods=12)
    )

    full_df["rank_yoy"] = (
        full_df.groupby("date")["yoy_pct"]
               .rank(ascending=False, na_option="bottom")
    )

    full_df.to_csv("data_processed/neighbourhood_monthly_metrics_complete.csv", index=False)

    print("Panel completed.")
    print("Rows:", len(full_df))
    print("Expected rows:", 24 * 120)

    

if __name__ == "__main__":
    main()