#!/usr/bin/env python3
"""
Fetch Fama-French factor data + FRED macro series for Prometheus finance domain expansion.
All data is public, no API keys needed for FF. FRED needs a key but has CSV bulk download.

Machine: M1 (Skullport), 2026-04-12
"""
import os, sys, json, io, zipfile
import urllib.request
from pathlib import Path
from datetime import datetime

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

def download(url, desc):
    print(f"Downloading {desc}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Prometheus/1.0"})
        resp = urllib.request.urlopen(req, timeout=60)
        data = resp.read()
        print(f"  Got {len(data):,} bytes")
        return data
    except Exception as e:
        print(f"  FAILED: {e}")
        return None

# ─── 1. Fama-French 5 Factors (Daily) ───
print("="*70)
print("FAMA-FRENCH 5 FACTORS (DAILY)")
print("="*70)

ff5_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
ff5_data = download(ff5_url, "FF 5-factor daily")

if ff5_data:
    zf = zipfile.ZipFile(io.BytesIO(ff5_data))
    csv_name = [n for n in zf.namelist() if n.endswith('.CSV') or n.endswith('.csv')][0]
    csv_text = zf.read(csv_name).decode('utf-8', errors='replace')

    # Parse: skip header lines until we find the data
    lines = csv_text.strip().split('\n')
    header_idx = None
    for i, line in enumerate(lines):
        if 'Mkt-RF' in line or 'Mkt_RF' in line or 'MktRF' in line:
            header_idx = i
            break
        if line.strip().startswith('199') or line.strip().startswith('200') or line.strip().startswith('201') or line.strip().startswith('202'):
            header_idx = i - 1 if i > 0 else i
            break

    if header_idx is None:
        # Try finding by comma-separated numeric data
        for i, line in enumerate(lines):
            parts = line.strip().split(',')
            if len(parts) >= 6 and parts[0].strip().isdigit() and len(parts[0].strip()) == 8:
                header_idx = i - 1
                break

    if header_idx is not None:
        import csv
        reader = csv.reader(lines[header_idx:])
        headers = next(reader)
        headers = [h.strip() for h in headers]
        print(f"  Headers: {headers}")

        records = []
        for row in reader:
            if len(row) < 6:
                continue
            date_str = row[0].strip()
            if not date_str or not date_str[0].isdigit():
                continue
            if len(date_str) != 8:
                continue
            try:
                vals = {headers[i]: float(row[i].strip()) for i in range(1, min(len(headers), len(row)))}
                vals["date"] = date_str
                records.append(vals)
            except (ValueError, IndexError):
                continue

        print(f"  Parsed {len(records)} daily records")
        print(f"  Date range: {records[0]['date']} to {records[-1]['date']}" if records else "  No records")

        with open(DATA / "ff5_daily.json", "w") as f:
            json.dump(records, f)
        print(f"  Saved to ff5_daily.json")
    else:
        print("  Could not find header row")
        # Save raw for debugging
        with open(DATA / "ff5_raw.csv", "w") as f:
            f.write(csv_text)
        print(f"  Saved raw CSV for debugging")

# ─── 2. Fama-French Industry Portfolios (10 industry, daily) ───
print("\n" + "="*70)
print("FAMA-FRENCH 10 INDUSTRY PORTFOLIOS (DAILY)")
print("="*70)

ind_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/10_Industry_Portfolios_daily_CSV.zip"
ind_data = download(ind_url, "FF 10-industry daily")

if ind_data:
    zf = zipfile.ZipFile(io.BytesIO(ind_data))
    csv_name = [n for n in zf.namelist() if n.endswith('.CSV') or n.endswith('.csv')][0]
    csv_text = zf.read(csv_name).decode('utf-8', errors='replace')

    lines = csv_text.strip().split('\n')

    # Find the value-weighted returns section
    header_idx = None
    for i, line in enumerate(lines):
        parts = line.strip().split(',')
        if len(parts) >= 10:
            # Check if this looks like industry names
            non_numeric = sum(1 for p in parts[1:] if p.strip() and not p.strip().replace('.','').replace('-','').isdigit())
            if non_numeric >= 5:
                header_idx = i
                break

    if header_idx is None:
        for i, line in enumerate(lines):
            if 'NoDur' in line or 'Durbl' in line or 'Manuf' in line:
                header_idx = i
                break

    if header_idx is not None:
        import csv
        reader = csv.reader(lines[header_idx:])
        headers = next(reader)
        headers = [h.strip() for h in headers]
        print(f"  Headers: {headers[:12]}")

        records = []
        for row in reader:
            if len(row) < 10:
                continue
            date_str = row[0].strip()
            if not date_str or not date_str[0].isdigit() or len(date_str) != 8:
                continue
            try:
                vals = {headers[i]: float(row[i].strip()) for i in range(1, min(len(headers), len(row)))}
                vals["date"] = date_str
                records.append(vals)
            except (ValueError, IndexError):
                continue

        print(f"  Parsed {len(records)} daily records")
        if records:
            print(f"  Date range: {records[0]['date']} to {records[-1]['date']}")
            print(f"  Sectors: {[h for h in headers[1:] if h]}")

        with open(DATA / "ff_10industry_daily.json", "w") as f:
            json.dump(records, f)
        print(f"  Saved to ff_10industry_daily.json")
    else:
        with open(DATA / "ff_10industry_raw.csv", "w") as f:
            f.write(csv_text)
        print(f"  Saved raw CSV for debugging")

# ─── 3. Fama-French Momentum Factor (Daily) ───
print("\n" + "="*70)
print("FAMA-FRENCH MOMENTUM FACTOR (DAILY)")
print("="*70)

mom_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip"
mom_data = download(mom_url, "FF momentum daily")

if mom_data:
    zf = zipfile.ZipFile(io.BytesIO(mom_data))
    csv_name = [n for n in zf.namelist() if n.endswith('.CSV') or n.endswith('.csv')][0]
    csv_text = zf.read(csv_name).decode('utf-8', errors='replace')

    lines = csv_text.strip().split('\n')
    records = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            date_str = parts[0].strip()
            if date_str and date_str[0].isdigit() and len(date_str) == 8:
                try:
                    records.append({"date": date_str, "Mom": float(parts[1].strip())})
                except ValueError:
                    continue

    print(f"  Parsed {len(records)} daily records")
    with open(DATA / "ff_momentum_daily.json", "w") as f:
        json.dump(records, f)
    print(f"  Saved to ff_momentum_daily.json")

# ─── 4. FRED Key Macro Series (via CSV bulk) ───
print("\n" + "="*70)
print("FRED MACRO SERIES (via direct CSV)")
print("="*70)

fred_series = {
    "GDP": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP",
    "CPIAUCSL": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL",
    "UNRATE": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE",
    "FEDFUNDS": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS",
    "GS10": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS10",
    "SP500": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500",
    "VIXCLS": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS",
    "T10Y2Y": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y",
    "DTWEXBGS": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
    "INDPRO": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INDPRO",
}

fred_data = {}
for series_id, url in fred_series.items():
    raw = download(url, f"FRED {series_id}")
    if raw:
        text = raw.decode('utf-8', errors='replace')
        lines = text.strip().split('\n')
        if len(lines) > 1:
            records = []
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 2 and parts[1].strip() != '.':
                    try:
                        records.append({"date": parts[0].strip(), "value": float(parts[1].strip())})
                    except ValueError:
                        continue
            fred_data[series_id] = records
            print(f"  {series_id}: {len(records)} records")

with open(DATA / "fred_macro.json", "w") as f:
    json.dump(fred_data, f)
print(f"\nSaved {len(fred_data)} FRED series to fred_macro.json")

# ─── Summary ───
print("\n" + "="*70)
print("DOWNLOAD SUMMARY")
print("="*70)
for f_path in sorted(DATA.glob("*.json")):
    size = f_path.stat().st_size
    print(f"  {f_path.name}: {size:,} bytes")
