"""Verify the 2026-06-22 allowlist rebuild against Charon's three findings
(SEAM_FIDELITY_ADVERSARIAL_VERDICT_2026-06-17), on the REAL corpus.

  F1 leak: inspect every RENDERED prompt for answer/verdict/statistic tokens.
  F2 holes: per-kind renderable rate; flag kinds that contribute 0 anchors.
  F3 bias: renderable rate by verdict class (kill vs survivor).

Bounded read: stratified across batches, PER lines each.
"""
import json
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from theseus.emit.corpus_files import iter_batch_paths, open_batch
from theseus.config import CORPUS_DIR
from theseus.handoff.ergon_handoff import (
    _render_prompt, _verdict_to_predicate_holds, _DELIBERATELY_UNRENDERED,
)

# Tokens that can only originate from an answer/verdict/statistic span.
ANSWER_TOKENS = (
    "confirmed", "refuted", "falsified", "rejected", "shadow_catalog",
    "promoted", "holds=", "r_raw", "p_raw", "p_value", "r_detrended",
    "survives_", "=true", "=false", "self_inverse=", "is_fixed_point=",
    "stays_in_set",
)

paths = iter_batch_paths(CORPUS_DIR)
idxs = sorted(set(int(i * (len(paths) - 1) / 39) for i in range(40)))
sel = [paths[i] for i in idxs]
PER = 1500

by_kind = Counter()
gold_total = Counter()
gold_rend = Counter()
rend_by_kind = Counter()
goldkind_by_kind = Counter()
leaks = []
seen = 0

for p in sel:
    c = 0
    try:
        with open_batch(p) as f:
            for line in f:
                if c >= PER:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                c += 1
                seen += 1
                k = r.get("claim_kind", "?")
                by_kind[k] += 1
                ph = _verdict_to_predicate_holds(r.get("verdict"))
                if ph is None:
                    continue
                cls = "kill" if ph is False else "survivor"
                gold_total[cls] += 1
                goldkind_by_kind[k] += 1
                prompt = _render_prompt(k, r.get("claim_payload") or {})
                if prompt is None:
                    continue
                rend_by_kind[k] += 1
                gold_rend[cls] += 1
                low = prompt.lower()
                for tok in ANSWER_TOKENS:
                    if tok in low:
                        leaks.append((k, tok, prompt[:160]))
                        break
    except OSError:
        continue

print(f"batches={len(sel)} sampled={seen} distinct_kinds={len(by_kind)}")
print()
print("=== F1 LEAK ATTACK: answer tokens in RENDERED prompts ===")
print(f"  total rendered prompts inspected: {sum(rend_by_kind.values())}")
print(f"  prompts that leak an answer token: {len(leaks)}")
for k, tok, pr in leaks[:20]:
    print(f"    [{k}] leak={tok!r}: {pr}")
print()
print("=== F3 OUTCOME-BIAS: renderable rate by verdict class ===")
for cls in ("kill", "survivor"):
    t, rr = gold_total[cls], gold_rend[cls]
    print(f"  {cls:9}: gold={t:6} rend={rr:6} rate={100*rr/t:.1f}%" if t else f"  {cls}: 0")
if gold_total["kill"] and gold_total["survivor"]:
    raw = 100 * gold_total["kill"] / (gold_total["kill"] + gold_total["survivor"])
    post = 100 * gold_rend["kill"] / max(1, gold_rend["kill"] + gold_rend["survivor"])
    print(f"  raw gold kill-share={raw:.1f}%  ->  post-render kill-share={post:.1f}%  "
          f"(gate shift {post-raw:+.1f}pp)")
print()
print("=== F2 PER-KIND: total / gold / renderable / skip% (gold-bearing) ===")
for k, c in by_kind.most_common(35):
    gk = goldkind_by_kind[k]
    rr = rend_by_kind[k]
    if gk:
        flag = ""
        if rr == 0:
            flag = "  <-- 0 anchors (render-fail)"
        print(f"  {k:28} tot={c:6} gold={gk:6} rend={rr:6} skip%={100*(gk-rr)/gk:3.0f}{flag}")
    else:
        tag = " (deliberate)" if k in _DELIBERATELY_UNRENDERED else ""
        print(f"  {k:28} tot={c:6} (no gold verdict){tag}")
