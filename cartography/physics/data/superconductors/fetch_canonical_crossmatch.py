"""
Fetch space group data from COD and AFLOW for canonical superconductor families.
Independent SG assignments for cross-validation against Materials Project.
"""
import requests
import json
import time
import csv
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# === COD ===
COD_URL = "https://www.crystallography.net/cod/result"

cod_queries = [
    # Cuprates
    ("YBCO", "Cuprate", {"el1": "Y", "el2": "Ba", "el3": "Cu", "el4": "O", "strictmin": 4, "strictmax": 4, "format": "json"}),
    ("La2CuO4", "Cuprate", {"el1": "La", "el2": "Cu", "el3": "O", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("BSCCO", "Cuprate", {"el1": "Bi", "el2": "Sr", "el3": "Ca", "el4": "Cu", "el5": "O", "strictmin": 5, "strictmax": 5, "format": "json"}),
    ("TlBaCaCuO", "Cuprate", {"el1": "Tl", "el2": "Ba", "el3": "Ca", "el4": "Cu", "el5": "O", "strictmin": 5, "strictmax": 5, "format": "json"}),
    ("HgBaCaCuO", "Cuprate", {"el1": "Hg", "el2": "Ba", "el3": "Ca", "el4": "Cu", "el5": "O", "strictmin": 5, "strictmax": 5, "format": "json"}),
    # Iron pnictides / chalcogenides
    ("BaFe2As2", "Ferrite", {"el1": "Ba", "el2": "Fe", "el3": "As", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("LaFeAsO", "Ferrite", {"el1": "La", "el2": "Fe", "el3": "As", "el4": "O", "strictmin": 4, "strictmax": 4, "format": "json"}),
    ("FeSe", "Ferrite", {"el1": "Fe", "el2": "Se", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("FeS", "Ferrite", {"el1": "Fe", "el2": "S", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("SrFeAsF", "Ferrite", {"el1": "Sr", "el2": "Fe", "el3": "As", "el4": "F", "strictmin": 4, "strictmax": 4, "format": "json"}),
    ("NdFeAsO", "Ferrite", {"el1": "Nd", "el2": "Fe", "el3": "As", "el4": "O", "strictmin": 4, "strictmax": 4, "format": "json"}),
    # Conventional
    ("MgB2", "Other", {"el1": "Mg", "el2": "B", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("Nb3Sn", "Other", {"el1": "Nb", "el2": "Sn", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("NbN", "Other", {"el1": "Nb", "el2": "N", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("NbTi", "Other", {"el1": "Nb", "el2": "Ti", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("V3Si", "Other", {"el1": "V", "el2": "Si", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("Nb3Ge", "Other", {"el1": "Nb", "el2": "Ge", "strictmin": 2, "strictmax": 2, "format": "json"}),
    # Chevrel
    ("PbMo6S8", "Chevrel", {"el1": "Pb", "el2": "Mo", "el3": "S", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("SnMo6S8", "Chevrel", {"el1": "Sn", "el2": "Mo", "el3": "S", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("CuMo6S8", "Chevrel", {"el1": "Cu", "el2": "Mo", "el3": "S", "strictmin": 3, "strictmax": 3, "format": "json"}),
    # Heavy fermion
    ("CeCu2Si2", "Heavy_fermion", {"el1": "Ce", "el2": "Cu", "el3": "Si", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("UPt3", "Heavy_fermion", {"el1": "U", "el2": "Pt", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("CeCoIn", "Heavy_fermion", {"el1": "Ce", "el2": "Co", "el3": "In", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("UBe13", "Heavy_fermion", {"el1": "U", "el2": "Be", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("CeRhIn5", "Heavy_fermion", {"el1": "Ce", "el2": "Rh", "el3": "In", "strictmin": 3, "strictmax": 3, "format": "json"}),
    # Oxide
    ("BaKBiO", "Oxide", {"el1": "Ba", "el2": "K", "el3": "Bi", "el4": "O", "strictmin": 4, "strictmax": 4, "format": "json"}),
    ("SrTiO3", "Oxide", {"el1": "Sr", "el2": "Ti", "el3": "O", "strictmin": 3, "strictmax": 3, "format": "json"}),
    ("LiTiO", "Oxide", {"el1": "Li", "el2": "Ti", "el3": "O", "strictmin": 3, "strictmax": 3, "format": "json"}),
    # Carbon
    ("KC", "Carbon", {"el1": "K", "el2": "C", "strictmin": 2, "strictmax": 2, "format": "json"}),
    ("RbC", "Carbon", {"el1": "Rb", "el2": "C", "strictmin": 2, "strictmax": 2, "format": "json"}),
]

cod_results = []
print("=== COD Fetch ===")
for name, sc_class, params in cod_queries:
    try:
        resp = requests.get(COD_URL, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  {name} ({sc_class}): {len(data)} entries")
            for entry in data:
                cod_results.append({
                    "query_name": name,
                    "sc_class": sc_class,
                    "cod_id": entry.get("file", ""),
                    "cod_formula": entry.get("formula", ""),
                    "cod_sg": entry.get("sg", ""),
                    "cod_sg_number": entry.get("sgNumber", ""),
                    "cod_a": entry.get("a", ""),
                    "cod_b": entry.get("b", ""),
                    "cod_c": entry.get("c", ""),
                    "cod_vol": entry.get("vol", ""),
                    "cod_year": entry.get("year", ""),
                    "cod_journal": entry.get("journal", ""),
                    "source": "COD",
                })
        else:
            print(f"  {name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  {name}: {e}")
    time.sleep(0.3)

cod_path = os.path.join(DATA_DIR, "cod_canonical_superconductors.csv")
if cod_results:
    keys = list(cod_results[0].keys())
    with open(cod_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(cod_results)
    print(f"\nCOD total: {len(cod_results)} entries -> {cod_path}")

# === AFLOW ===
AFLOW_URL = "https://aflow.org/API/aflux/"

aflow_queries = [
    ("BaFe2As2", "Ferrite", "species(Ba,Fe,As),nspecies(3)"),
    ("LaFeAsO", "Ferrite", "species(La,Fe,As,O),nspecies(4)"),
    ("FeSe", "Ferrite", "species(Fe,Se),nspecies(2)"),
    ("FeS", "Ferrite", "species(Fe,S),nspecies(2)"),
    ("NdFeAsO", "Ferrite", "species(Nd,Fe,As,O),nspecies(4)"),
    ("MgB2", "Other", "species(Mg,B),nspecies(2)"),
    ("Nb3Sn", "Other", "species(Nb,Sn),nspecies(2)"),
    ("NbN", "Other", "species(Nb,N),nspecies(2)"),
    ("NbTi", "Other", "species(Nb,Ti),nspecies(2)"),
    ("V3Si", "Other", "species(V,Si),nspecies(2)"),
    ("Nb3Ge", "Other", "species(Nb,Ge),nspecies(2)"),
    ("YBaCuO", "Cuprate", "species(Y,Ba,Cu,O),nspecies(4)"),
    ("LaCuO", "Cuprate", "species(La,Cu,O),nspecies(3)"),
    ("CeCuSi", "Heavy_fermion", "species(Ce,Cu,Si),nspecies(3)"),
    ("UPt", "Heavy_fermion", "species(U,Pt),nspecies(2)"),
    ("CeCoIn", "Heavy_fermion", "species(Ce,Co,In),nspecies(3)"),
    ("CeRhIn", "Heavy_fermion", "species(Ce,Rh,In),nspecies(3)"),
    ("PbMoS", "Chevrel", "species(Pb,Mo,S),nspecies(3)"),
    ("SnMoS", "Chevrel", "species(Sn,Mo,S),nspecies(3)"),
    ("BaKBiO", "Oxide", "species(Ba,K,Bi,O),nspecies(4)"),
    ("SrTiO", "Oxide", "species(Sr,Ti,O),nspecies(3)"),
]

aflow_results = []
print("\n=== AFLOW Fetch ===")
for name, sc_class, q in aflow_queries:
    url = f"{AFLOW_URL}?{q},paging(0),$auid,compound,spacegroup_relax,Pearson_symbol_relax,lattice_system_relax,geometry,enthalpy_formation_atom"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            count = len(data)
            print(f"  {name} ({sc_class}): {count} entries")
            for key, entry in data.items():
                aflow_results.append({
                    "query_name": name,
                    "sc_class": sc_class,
                    "aflow_auid": entry.get("auid", ""),
                    "aflow_compound": entry.get("compound", ""),
                    "aflow_sg": entry.get("spacegroup_relax", ""),
                    "aflow_pearson": entry.get("Pearson_symbol_relax", ""),
                    "aflow_lattice": entry.get("lattice_system_relax", ""),
                    "aflow_geometry": str(entry.get("geometry", "")),
                    "aflow_Hf": entry.get("enthalpy_formation_atom", ""),
                    "source": "AFLOW",
                })
        else:
            print(f"  {name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  {name}: {e}")
    time.sleep(1.0)

aflow_path = os.path.join(DATA_DIR, "aflow_canonical_superconductors.csv")
if aflow_results:
    keys = list(aflow_results[0].keys())
    with open(aflow_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(aflow_results)
    print(f"\nAFLOW total: {len(aflow_results)} entries -> {aflow_path}")

# === Summary ===
print("\n" + "=" * 60)
print("CROSS-MATCH DATA PULL SUMMARY")
print("=" * 60)
print(f"COD:   {len(cod_results)} entries from {len(cod_queries)} queries")
print(f"AFLOW: {len(aflow_results)} entries from {len(aflow_queries)} queries")
print(f"Total: {len(cod_results) + len(aflow_results)} independent SG assignments")

# Quick SG agreement check
if cod_results:
    print("\n--- COD SG distribution by class ---")
    from collections import Counter
    for cls in sorted(set(r["sc_class"] for r in cod_results)):
        sgs = Counter(r["cod_sg_number"] for r in cod_results if r["sc_class"] == cls and r["cod_sg_number"])
        top = sgs.most_common(5)
        print(f"  {cls}: {sum(sgs.values())} entries, top SGs: {top}")

if aflow_results:
    print("\n--- AFLOW SG distribution by class ---")
    from collections import Counter
    for cls in sorted(set(r["sc_class"] for r in aflow_results)):
        sgs = Counter(r["aflow_sg"] for r in aflow_results if r["sc_class"] == cls and r["aflow_sg"])
        top = sgs.most_common(5)
        print(f"  {cls}: {sum(sgs.values())} entries, top SGs: {top}")
