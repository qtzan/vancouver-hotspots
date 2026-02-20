from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "postgresql+psycopg2://postgres:Icey_Mech0204@localhost:1234/Vancouver_analytics"
)

df = pd.read_sql("SELECT version();", engine)
print(df)