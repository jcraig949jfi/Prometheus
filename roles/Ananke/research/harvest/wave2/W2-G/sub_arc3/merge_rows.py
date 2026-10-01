"""Merge rows_group{A,B,C,G}.csv into arc3_claims.csv. Run: python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/merge_rows.py"""
import csv, os, collections
H = os.path.dirname(os.path.abspath(__file__))
COLS = "claim_id,doc,location,claim_text,source_report,report_value,raw_path,rederived_value,status,denominator,denominator_ok,wording_exceeds,notes".split(",")
rows = []
for g in "GABC":
    with open(os.path.join(H, f"rows_group{g}.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            assert list(r.keys()) == COLS, (g, list(r.keys()))
            rows.append(r)
with open(os.path.join(H, "arc3_claims.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(rows)
c = collections.Counter(r["status"] for r in rows)
we = collections.Counter(r["wording_exceeds"].split()[0].lower() if r["wording_exceeds"] else "" for r in rows)
print(len(rows), dict(c)); print("wording_exceeds:", dict(we))
