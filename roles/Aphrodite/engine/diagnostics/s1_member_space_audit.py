"""DIAGNOSTIC (not a gate, changes nothing frozen): after S1 run 3 failed on 13
rare overflow-threshold false merges, measure the false-merge count on the
space S3 actually abstracts over -- M = H1 x H2 x FINAL_SPACE (AMENDMENT 14 D3)
-- under D_TASK_T3_v1 with B1 v3 / B2 v3."""
import json, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import identity as I   # noqa: E402
import tier3d as T     # noqa: E402


def _b(p):
    return p, I.behavior_id(p, True)


def _a(p):
    return p, I.audit_id(p, True)


def main():
    t0 = time.perf_counter()
    M = T.member_space()
    with ProcessPoolExecutor(7) as ex:
        B = dict(ex.map(_b, M, chunksize=64))
    cls = {}
    for p, b in B.items():
        cls.setdefault(b, []).append(p)
    multi = [p for v in cls.values() if len(v) > 1 for p in v]
    print("classes", len(cls), "members in multi-member classes", len(multi), flush=True)
    with ProcessPoolExecutor(7) as ex:
        A = dict(ex.map(_a, multi, chunksize=16))
    fm = []
    for b, v in cls.items():
        if len(v) > 1 and len({A[p] for p in v}) > 1:
            fm.append([list(p) for p in v][:6])
    out = {"space": "H1 x H2 x FINAL_SPACE", "programs": len(M), "classes": len(cls),
           "members_in_multi_member_classes": len(multi), "false_merges": len(fm),
           "examples": fm[:20], "seconds": round(time.perf_counter() - t0, 1),
           "domain": I.DOMAIN, "B1_sha256": I.B1_SHA}
    (HERE / "diagnostics" / "S1_MEMBER_SPACE_AUDIT_2026-09-24.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("false merges in M:", len(fm), "(%.0fs)" % out["seconds"], flush=True)


if __name__ == "__main__":
    main()
