"""
Fetch space group data from COD (Crystallography Open Database) for superconductor materials.
Queries by element set to avoid formula formatting issues.
"""
import pandas as pd
import requests
import time
import json
import re
import csv
import os
from collections import defaultdict

# Load 3DSC dataset
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(DATA_DIR, '3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv'), comment='#')

# Extract unique element sets from formulas
def parse_elements(formula):
    """Extract element symbols from a chemical formula."""
    return sorted(set(re.findall(r'[A-Z][a-z]?', formula)))

# Get representative formulas per (sc_class, spacegroup) combination
# We don't need all 5759 — we need coverage across classes and SGs
representatives = df.groupby(['sc_class', 'spacegroup_2']).first().reset_index()
print(f"Unique (class, SG) combos: {len(representatives)}")

# Get unique element sets to query
element_sets = {}
for _, row in representatives.iterrows():
    formula = row['formula_sc']
    elems = parse_elements(formula)
    key = tuple(elems)
    if key not in element_sets:
        element_sets[key] = {
            'formula': formula,
            'elements': elems,
            'sc_class': row['sc_class'],
            'mp_sg': row['spacegroup_2'],
            'tc': row['tc']
        }

print(f"Unique element sets to query: {len(element_sets)}")
# Limit to manageable number — prioritize by class diversity
# Take up to 20 per class
by_class = defaultdict(list)
for key, info in element_sets.items():
    by_class[info['sc_class']].append((key, info))

selected = []
for cls, items in by_class.items():
    selected.extend(items[:20])
print(f"Selected for COD query: {len(selected)}")

# Query COD REST API
COD_URL = "https://www.crystallography.net/cod/result"
results = []
errors = []

for i, (key, info) in enumerate(selected):
    elems = info['elements']
    # Build query params
    params = {'format': 'json'}
    for j, el in enumerate(elems[:8], 1):  # COD supports up to el1-el8
        params[f'el{j}'] = el
    # Strict element count to avoid supersets
    params['strictmin'] = len(elems)
    params['strictmax'] = len(elems)
    
    try:
        resp = requests.get(COD_URL, params=params, timeout=15)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data:
                    for entry in data[:5]:  # Take up to 5 matches per query
                        results.append({
                            'query_formula': info['formula'],
                            'query_elements': '-'.join(elems),
                            'sc_class': info['sc_class'],
                            'mp_spacegroup': info['mp_sg'],
                            'mp_tc': info['tc'],
                            'cod_id': entry.get('file', ''),
                            'cod_formula': entry.get('formula', ''),
                            'cod_spacegroup': entry.get('sg', entry.get('sgHall', '')),
                            'cod_sg_number': entry.get('sgNumber', ''),
                            'cod_a': entry.get('a', ''),
                            'cod_b': entry.get('b', ''),
                            'cod_c': entry.get('c', ''),
                            'cod_vol': entry.get('vol', ''),
                            'cod_year': entry.get('year', ''),
                        })
                    print(f"[{i+1}/{len(selected)}] {info['formula']}: {len(data)} COD hits")
                else:
                    print(f"[{i+1}/{len(selected)}] {info['formula']}: no hits")
            except (json.JSONDecodeError, ValueError):
                print(f"[{i+1}/{len(selected)}] {info['formula']}: JSON parse error")
                errors.append(info['formula'])
        else:
            print(f"[{i+1}/{len(selected)}] {info['formula']}: HTTP {resp.status_code}")
            errors.append(info['formula'])
    except requests.exceptions.Timeout:
        print(f"[{i+1}/{len(selected)}] {info['formula']}: timeout")
        errors.append(info['formula'])
    except Exception as e:
        print(f"[{i+1}/{len(selected)}] {info['formula']}: {e}")
        errors.append(info['formula'])
    
    time.sleep(0.5)  # Be polite to COD

# Save results
out_path = os.path.join(DATA_DIR, 'cod_spacegroup_crossmatch.csv')
if results:
    pd.DataFrame(results).to_csv(out_path, index=False)
    print(f"\nSaved {len(results)} COD entries to {out_path}")
    print(f"Errors: {len(errors)}")
    
    # Quick summary
    rdf = pd.DataFrame(results)
    matches = rdf[rdf['cod_spacegroup'] != '']
    print(f"Entries with SG data: {len(matches)}")
    print(f"Unique COD space groups: {matches['cod_spacegroup'].nunique()}")
else:
    print("No results obtained from COD")
