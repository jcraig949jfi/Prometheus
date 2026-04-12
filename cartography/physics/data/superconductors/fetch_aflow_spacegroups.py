"""
Fetch space group data from AFLOW for superconductor materials.
Uses AFLUX REST API — free, no auth required.
"""
import pandas as pd
import requests
import time
import json
import re
import os
from collections import defaultdict

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(DATA_DIR, '3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv'), comment='#')

def parse_elements(formula):
    return sorted(set(re.findall(r'[A-Z][a-z]?', formula)))

# Get representative formulas per (sc_class, spacegroup) 
representatives = df.groupby(['sc_class', 'spacegroup_2']).first().reset_index()

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

# Select subset per class
by_class = defaultdict(list)
for key, info in element_sets.items():
    by_class[info['sc_class']].append((key, info))

selected = []
for cls, items in by_class.items():
    selected.extend(items[:15])
print(f"Selected for AFLOW query: {len(selected)}")

# Query AFLOW AFLUX API
AFLOW_URL = "https://aflow.org/API/aflux/"
results = []
errors = []

for i, (key, info) in enumerate(selected):
    elems = info['elements']
    species_str = ','.join(elems)
    
    # AFLUX query: search by species and nspecies
    query = f"species({species_str}),nspecies({len(elems)}),paging(0)"
    url = f"{AFLOW_URL}?{query},$auid,compound,spacegroup_relax,Pearson_symbol_relax,lattice_system_relax,geometry,enthalpy_formation_atom,Egap"
    
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data:
                    for entry in data[:5]:  # Up to 5 per query
                        results.append({
                            'query_formula': info['formula'],
                            'query_elements': '-'.join(elems),
                            'sc_class': info['sc_class'],
                            'mp_spacegroup': info['mp_sg'],
                            'mp_tc': info['tc'],
                            'aflow_auid': entry.get('auid', ''),
                            'aflow_compound': entry.get('compound', ''),
                            'aflow_spacegroup': entry.get('spacegroup_relax', ''),
                            'aflow_pearson': entry.get('Pearson_symbol_relax', ''),
                            'aflow_lattice': entry.get('lattice_system_relax', ''),
                            'aflow_geometry': entry.get('geometry', ''),
                            'aflow_Hf': entry.get('enthalpy_formation_atom', ''),
                            'aflow_Egap': entry.get('Egap', ''),
                        })
                    print(f"[{i+1}/{len(selected)}] {info['formula']}: {len(data)} AFLOW hits")
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
    
    time.sleep(1.0)  # AFLOW rate limit

# Save
out_path = os.path.join(DATA_DIR, 'aflow_spacegroup_crossmatch.csv')
if results:
    pd.DataFrame(results).to_csv(out_path, index=False)
    print(f"\nSaved {len(results)} AFLOW entries to {out_path}")
    print(f"Errors: {len(errors)}")
    
    rdf = pd.DataFrame(results)
    matches = rdf[rdf['aflow_spacegroup'] != '']
    print(f"Entries with SG data: {len(matches)}")
    print(f"Unique AFLOW space groups: {matches['aflow_spacegroup'].nunique()}")
else:
    print("No results obtained from AFLOW")
