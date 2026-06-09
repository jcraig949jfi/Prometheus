"""Zoo-adapter smoke test (EXPERIMENTAL, CHIP-AWAY).

Runs `zoo_reasoner.make_zoo_reasoner` for a handful of reachable open-weight /
mid zoo models against a small sample of R0/R1/R2 probes from
`reasoning_phase0`, graded by `reasoning_phase0.grade`. The point is NOT a
capability measurement — it is to CONFIRM the adapter:
  (1) reaches each pinned model,
  (2) parses its free-text JSON into the harness answer format,
  (3) grades without error,
and to QUANTIFY the per-model parse-failure rate (free-text JSON is lossier
than the Anthropic structured-outputs path; that loss is a measured number).

Same probes across every model => apples-to-apples.

Usage:
    python harmonia/experiments/zoo_smoke.py [N_per_tier]   # default 4
"""
from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

_EXPERIMENTS = Path(__file__).resolve().parent
if str(_EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS))

from reasoning_phase0 import gen_R0, gen_R1, gen_R2, grade  # noqa: E402
from zoo_reasoner import make_zoo_reasoner, _resolve_key  # noqa: E402

# 3 reachable zoo models spanning the size range (open-small -> mid), all
# non-Anthropic / free-text-JSON path. Verified live in zoo_inventory 2026-05-29.
SMOKE_MODELS = [
    ("NVIDIA", "meta/llama-3.1-8b-instruct", "open-small"),
    ("NVIDIA", "meta/llama-3.3-70b-instruct", "mid"),
    ("Groq", "llama-3.1-8b-instant", "open-small"),
]

GENS = {"R0": gen_R0, "R1": gen_R1, "R2": gen_R2}


def sample_probes(n_per_tier: int):
    rng = random.Random(20260529)
    probes = []
    for t, g in GENS.items():
        allp = g(rng)
        # one of each version so we exercise iso/adversarial/transfer mapping too
        for v in ("clean", "iso", "adversarial", "transfer"):
            pv = [p for p in allp if p.version == v]
            rng.shuffle(pv)
            probes.extend(pv[:max(1, n_per_tier // 4)])
    return probes


# Error taxonomy — keep TRANSPORT and CONTENT failures separate from GENUINE
# JSON parse failures so the reported parse-failure rate isn't inflated by
# rate-limit noise (the whole point the synthesis cares about: free-text JSON is
# lossier than structured outputs — but ONLY the genuine-parse number measures that).
_TRANSPORT = lambda e: e.startswith("http_error:") or e.startswith("call_exception:") or e in (
    "unknown_transport_error", "no_key", "unknown_provider")
_CONTENT = lambda e: e in ("no_choices", "empty_content")
# everything else from parse_json_blob: empty_response, no_json_object,
# json_decode_error:*, unbalanced_braces  => GENUINE parse failure.


def run_model(provider, model, probes):
    log = []
    reasoner = make_zoo_reasoner(model, provider, call_log=log)
    n_ok = 0
    per_tier_ok = Counter()
    per_tier_tot = Counter()
    for p in probes:
        ans, tr = reasoner(p)
        v, ok = grade(p, ans, tr)
        n_ok += int(ok)
        per_tier_tot[p.tier] += 1
        if ok:
            per_tier_ok[p.tier] += 1
    errs = [c["parse_error"] for c in log if c.get("parse_error")]
    transport = [e for e in errs if _TRANSPORT(e)]
    content = [e for e in errs if _CONTENT(e)]
    genuine = [e for e in errs if not _TRANSPORT(e) and not _CONTENT(e)]
    return {
        "acc": n_ok / max(1, len(probes)),
        "n": len(probes),
        "transport_n": len(transport),
        "content_n": len(content),
        "genuine_parse_n": len(genuine),
        "genuine_parse_rate": len(genuine) / max(1, len(log)),
        "err_kinds": Counter(errs),
        "per_tier": {t: (per_tier_ok[t], per_tier_tot[t]) for t in GENS},
    }


def main():
    n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    probes = sample_probes(n_per)
    print(f"zoo smoke | {len(probes)} probes ({list(GENS)} x4 versions) | "
          f"{len(SMOKE_MODELS)} models\n")

    results = {}
    for provider, model, tier in SMOKE_MODELS:
        tag = f"{provider}/{model}"
        if not _resolve_key(provider):
            print(f"--- {tag} ({tier}): SKIP (no key) ---")
            continue
        print(f"--- {tag} ({tier}) ---", flush=True)
        r = run_model(provider, model, probes)
        results[tag] = r
        print(f"    acc={r['acc']:.2f} ({r['n']} probes)  "
              f"genuine_parse_fail={r['genuine_parse_n']}/{r['n']} "
              f"({r['genuine_parse_rate']:.0%})  "
              f"transport_fail={r['transport_n']}  content_empty={r['content_n']}")
        tline = "  ".join(f"{t}:{ok}/{tot}" for t, (ok, tot) in r["per_tier"].items())
        print(f"    per-tier: {tline}")
        if r["err_kinds"]:
            print(f"    err kinds: {dict(r['err_kinds'])}")

    print("\n======================= SMOKE SUMMARY =======================")
    print(f"{'model':45s} {'acc':>5s} {'genuineparse':>13s} {'transport':>10s}")
    any_pass = False
    for tag, r in results.items():
        print(f"{tag:45s} {r['acc']:5.2f} {r['genuine_parse_rate']:12.0%} "
              f"{r['transport_n']:10d}")
        # smoke PASS criterion: at least one model reached, with the parser
        # producing gradeable answers (genuine JSON parse failure <= 50%).
        # Transport (429/timeout) failures don't count against the adapter —
        # they're an infra/rate-limit problem the doc flags separately.
        if r["genuine_parse_rate"] <= 0.5 and (r["n"] - r["transport_n"]) > 0:
            any_pass = True
    print(f"\nSMOKE {'PASS' if any_pass else 'FAIL'} — "
          f"adapter reached/parsed/graded at least one model with genuine "
          f"JSON parse-failure <= 50%.")
    print("Note: accuracy here is incidental (tiny N, weak models on purpose). "
          "Load-bearing numbers = reachability + GENUINE parse-failure rate "
          "(transport/rate-limit failures reported separately).")


if __name__ == "__main__":
    main()
