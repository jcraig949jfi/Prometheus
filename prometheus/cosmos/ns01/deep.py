"""NS-01 step 5: deeper investigation of VIABLE_DISTINCT / DISTINCT_BEHAVIOR_UNEXPLAINED candidates (preregistered in
GENERATION_PROTOCOL.md): fresh-seed signature, the 4 disguises, distances to all witnesses and all other candidates.

    python -m prometheus.cosmos.ns01.deep run <campaign_dir> <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DISGUISES = ("Permute", "LinearEncode", "Rescale", "RenameState")


def _make(camp, arm, idx):
    from prometheus.cosmos.ns01.evaluate import load_llm
    from prometheus.cosmos.ns01.grammar import make_from_spec
    p = Path(camp) / "proposals" / arm / (f"{idx:02d}.json" if arm == "D" else f"{idx:02d}.py")
    return make_from_spec(json.loads(p.read_text())) if arm == "D" else load_llm(p.read_text())


def one(j):
    from prometheus.cosmos.ns01 import signature as S
    from prometheus.cosmos.ns01 import transforms as T
    from prometheus.cosmos.ns01.evaluate import _sigjson
    base = _make(j["camp"], j["arm"], j["idx"])
    if j["variant"] == "fresh_seed":
        sig = S.signature(base, seed=7)
    else:
        cls = getattr(T, j["variant"])
        mk = (lambda t: cls(base(t))) if j["variant"] in ("Rescale", "RenameState") else (lambda t: cls(base(t), seed=5))
        sig = S.signature(mk)
    return {**{k: j[k] for k in ("key", "arm", "idx", "variant")}, "sig": _sigjson(sig), "cls": S.classify(sig)}


def run(camp, rundir):
    from prometheus.cosmos import supervise as SV
    rows = [json.loads(x) for x in (Path(camp) / "EXCLUSION_RESULTS.jsonl").read_text().splitlines() if x.strip()]
    sel = [r for r in rows if r["label"] in ("VIABLE_DISTINCT", "DISTINCT_BEHAVIOR_UNEXPLAINED")]
    sel.sort(key=lambda r: (r["label"] != "DISTINCT_BEHAVIOR_UNEXPLAINED", r["arm"], r["idx"]))
    jobs = [{"key": f"{r['arm']}{r['idx']:02d}:{v}", "camp": str(camp), "arm": r["arm"], "idx": r["idx"], "variant": v}
            for r in sel for v in ("fresh_seed",) + DISGUISES]
    return SV.run_jobs(one, jobs, rundir, key="key", out="deep.jsonl", workers=2, max_failures=0)


if __name__ == "__main__":
    a = sys.argv
    run(a[2], a[3])
