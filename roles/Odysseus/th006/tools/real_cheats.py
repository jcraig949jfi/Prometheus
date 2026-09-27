"""Adversarial controls on the REAL specimen (r038751): mutate a copy of the node's replay
output and confirm the committed pack rejects it, and say what it rejects it for.

    python3 real_cheats.py OUT.json PACK.json PACK_SHA256 PUBLISHED.json

C1 claim-relevant: one birth that the published table counts as "location NO, material YES"
   is rewritten so its copy writes are foreign by material (codeprov) -- a real scientific change.
C2 claim-relevant row field: by_own_code (f9) set to writes, so location reads YES.
C3 claim-irrelevant: the tick (f0) of one birth +1.
Every mutation must give verdict FAIL; the report records which checks caught it.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import th006_pack as P  # noqa: E402


def main(out_path, pack_path, pack_sha, published):
    with open(out_path, encoding="utf-8") as f:
        d = json.load(f)
    rows, cp = d["births_rows"], d["codeprov"]
    i = next(k for k, (r, c) in enumerate(zip(rows, cp))
             if P.by_location(r) == "NO" and P.by_material(r, c) == "YES" and r[7] >= 4)

    def mutated(fn, label):
        r2, c2 = [list(r) for r in rows], [dict(c) for c in cp]
        fn(r2, c2)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=os.path.dirname(os.path.abspath(out_path))) as t:
            json.dump({"births_rows": r2, "codeprov": c2}, t)
        try:
            v = P.verify(pack_path, t.name, pack_sha, published)
        finally:
            os.unlink(t.name)
        return {"control": label, "row": i, "verdict": v["verdict"],
                "identity": v["identity"]["status"], "fields_changed": v["identity"]["fields_changed"],
                "claim_fields_changed": v["identity"]["claim_fields_changed"],
                "first_bad_chunk": v["identity"]["first_bad_chunk"],
                "codeprov": v["codeprov"]["status"], "claim": v["claim"]["status"],
                "table_W_NO_YES": v["claim"]["recomputed"]["location_vs_material"].get("W_by_location=NO | W_by_material=YES")}

    def c1(r2, c2):
        w = r2[i][7]
        c2[i] = {"own_region": 0, "self_copied": 0, "foreign": w, "elsewhere": 0}

    def c2_(r2, c2):
        r2[i][9] = r2[i][7]

    def c3(r2, c2):
        r2[i][0] += 1

    res = [mutated(c1, "C1 codeprov: self-copied -> foreign (relevant)"),
           mutated(c2_, "C2 row f9 by_own_code := writes (relevant)"),
           mutated(c3, "C3 row f0 tick + 1 (irrelevant)")]
    print(json.dumps(res, indent=1))
    return 0 if all(r["verdict"] == "FAIL" for r in res) else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
