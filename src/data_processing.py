import pandas as pd
import duckdb

RAW = "data/raw/2018_Central_Park_Squirrel_Census.csv"
OUT_CSV = "data/processed/squirrels.csv"
OUT_PAR = "data/processed/squirrels.parquet"

# data cleaning
squirrels = pd.read_csv(RAW)
squirrels['Date'] = pd.to_datetime(squirrels['Date'], format='%m%d%Y')
squirrels.columns = squirrels.columns.str.lower().str.replace(' ', '_')

# save to csv
squirrels.to_csv(OUT_CSV, index=False)

# convert to parquet and save
duckdb.execute(f"""
    COPY (SELECT * FROM squirrels)
    TO '{OUT_PAR}' (FORMAT PARQUET)
""")