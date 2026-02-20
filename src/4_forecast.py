import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

INPUT_PATH = "data_processed/neighbourhood_monthly_metrics_complete.csv"
OUTPUT_PATH = "data_processed/neighbourhood_forecasts_6mo.csv"

START_FORECAST = "2026-01-01"  # month after your last date (2025-12-01)
HORIZON = 6

def forecast_one(ts: pd.Series):
    """
    ts: monthly incident_count indexed by date (freq=MS), length 120
    returns forecast series length HORIZON
    """
    # ETS with additive trend + additive seasonality (12 months)
    model = ExponentialSmoothing(
        ts,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated"
    )
    fit = model.fit(optimized=True)

    fc = fit.forecast(HORIZON)
    return fc, fit

def main():
    df = pd.read_csv(INPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["neighbourhood", "date"])

    forecasts = []
    diagnostics = []

    for nbhd, g in df.groupby("neighbourhood"):
        g = g.sort_values("date")
        ts = g.set_index("date")["incident_count"].asfreq("MS")

        fc, fit = forecast_one(ts)

        # Simple uncertainty band using residual std (good enough for portfolio)
        resid_std = (ts - fit.fittedvalues).std()
        lower = (fc - 1.96 * resid_std).clip(lower=0)
        upper = (fc + 1.96 * resid_std)

        out = pd.DataFrame({
            "neighbourhood": nbhd,
            "date": fc.index,
            "forecast": fc.values,
            "lower_95": lower.values,
            "upper_95": upper.values
        })
        forecasts.append(out)

        diagnostics.append({
            "neighbourhood": nbhd,
            "resid_std": float(resid_std),
            "aic": float(getattr(fit, "aic", float("nan")))
        })

    fc_df = pd.concat(forecasts, ignore_index=True)
    fc_df.to_csv(OUTPUT_PATH, index=False)

    diag_df = pd.DataFrame(diagnostics).sort_values("resid_std", ascending=False)
    diag_df.to_csv("data_processed/forecast_diagnostics.csv", index=False)

    print("Forecasts saved:", OUTPUT_PATH)
    print("Neighbourhoods forecasted:", fc_df["neighbourhood"].nunique())
    print("Forecast months:", fc_df["date"].min().date(), "to", fc_df["date"].max().date())

if __name__ == "__main__":
    main()