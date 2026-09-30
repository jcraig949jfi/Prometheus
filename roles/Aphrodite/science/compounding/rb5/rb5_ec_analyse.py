"""RB-5 part (2) for the EC ladder: analyse every verified EC witness class
(T4 family_profile, fclass, body_class, K7 G1 test, Q2, permutation invariance).
G5 = G4 witnesses + depth-3 extras witnesses (H1 inits). Forensic, not a disposition."""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rb5_common as C      # noqa: E402


def job(item):
    f, progs = item
    return f, C.analyse_family(progs)


def main():
    g4 = json.loads((HERE / "EC_SEARCH_G4.json").read_text(encoding="utf-8"))["families"]
    g5 = json.loads((HERE / "EC_SEARCH_G5.json").read_text(encoding="utf-8"))["families"]
    items = {}
    for f in g4:
        a, b = g4[f]["verified"], g5[f]["verified"]
        if a:
            items[("g4", f)] = a
        if a or b:
            items[("g5", f)] = a + [p for p in b if p not in a]
    keys = list(items)
    with ProcessPoolExecutor(max_workers=C.WORKERS, initializer=C.worker_init) as ex:
        res = dict(ex.map(job, [(k, items[k]) for k in keys], chunksize=4))
    out = {}
    for (gr, f), cls in res.items():
        out.setdefault(f, {})[gr] = {"classes": cls, "summary": C.family_summary(cls)}
    (HERE / "EC_ANALYSIS.json").write_text(json.dumps(
        {"families": {k: v for k, v in sorted(out.items())}}, indent=0), encoding="utf-8")
    print("analysed", len(res))


if __name__ == "__main__":
    main()
