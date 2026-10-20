import pandas as pd
import requests
import sys

print("--- DIAGNOSTIC START ---")
try:
    print("Checking CSV reading...")
    df = pd.read_csv("/mnt/c/Users/Esteban Selvaggi/Desktop/AI_Agent/docs/tay.com.ar, decotay.com.ar/_TAY - Base de Familia.csv", sep=None, engine='python', encoding='utf-8')
    print(f"CSV Read Success! Rows: {len(df)}")
except Exception as e:
    print(f"CSV Read Failed: {e}")

try:
    print("Checking API connectivity...")
    r = requests.get("https://decotay.com.ar/wp-json/wc/v3/products", params={"per_page": 1}, timeout=10)
    print(f"API Response: {r.status_code}")
except Exception as e:
    print(f"API Connectivity Failed: {e}")
print("--- DIAGNOSTIC END ---")
