import pandas as pd
from sqlalchemy import create_engine, text



CSV_PATH = "data_raw/crimedata_csv_AllNeighbourhoods_AllYears.csv"

DB_URL = "postgresql+psycopg2://postgres:Icey_Mech0204@localhost:1234/Vancouver_analytics"

def main():
    engine = create_engine(DB_URL)

    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]

    expected = [
        "type","year","month","day","hour","minute","hundred_block","neighbourhood","x","y"
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}/nFound: {list(df.columns)}")
    
    df = df[expected].copy()

    int_cols = ["year","month","day","hour","minute"]
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    for c in ["x", "y"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE crime_incidents_raw;"))

    df.to_sql(
        "crime_incidents_raw",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=50000
    )

    print("Loaded rows:", len(df))
    print("Data range (year):", df["year"].min(), "to", df["year"].max())
    print("Unique neighbourhoods:", df["neighbourhood"].nunique())

   

if __name__ == "__main__":
    main()