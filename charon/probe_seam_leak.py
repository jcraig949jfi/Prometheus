"""Charon adversarial probe of the 2026-06-15 seam-fidelity fix (db4b2cac).

Attacks three claims from SEAM_FIDELITY_FIX_2026-06-15.md on a stratified
cross-batch sample of the REAL corpus:
  1. "leak audit 0"  -> inspect rendered non-invariant heads for surviving answers.
  2. "24 kinds, leak-safe-or-skip" -> per-kind skip rate (renderable-kind monoculture?).
  3. "56.6% rejected / 43.4% promoted" -> is renderability correlated with verdict?

Bounded read: stratified across batches, PER lines each. No 346 GB walk.
"""
import json
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from theseus.emit.corpus_files import iter_batch_paths, open_batch
from theseus.config import CORPUS_DIR
from theseus.handoff.ergon_handoff import (
    _renderable, _leak_safe_claim, _verdict_to_predicate_holds,
)

paths = iter_batch_paths(CORPUS_DIR)
idxs = sorted(set(int(i * (len(paths) - 1) / 39) for i in range(40)))
sel = [paths[i] for i in idxs]
PER = 1500

by_kind = Counter()
gold_total = Counter()
gold_renderable = Counter()
skip_by_kind = Counter()
rend_by_kind = Counter()
head_samples = defaultdict(list)
nogold = 0
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
                v = r.get("verdict")
                by_kind[k] += 1
                ph = _verdict_to_predicate_holds(v)
                if ph is None:
                    nogold += 1
                    continue
                cls = "kill" if ph is False else "survivor"
                gold_total[cls] += 1
                if _renderable(r):
                    rend_by_kind[k] += 1
                    gold_renderable[cls] += 1
                    if k != "invariant_equality":
                        h = _leak_safe_claim(r.get("canonical_claim_text") or "")
                        if h and len(head_samples[k]) < 3:
                            head_samples[k].append((v, h[:170]))
                else:
                    skip_by_kind[k] += 1
    except OSError:
        continue

print(f"batches={len(sel)} sampled={seen} distinct_kinds={len(by_kind)} "
      f"no_gold={nogold} ({100*nogold/max(seen,1):.1f}%)")
print()
print("=== OUTCOME-BIAS ATTACK: renderable rate by verdict class ===")
for cls in ("kill", "survivor"):
    t = gold_total[cls]
    rr = gold_renderable[cls]
    print(f"  {cls:9}: gold={t:6} rend={rr:6} rate={100*rr/t:.1f}%" if t else f"  {cls}: 0")
print()
print("=== per-kind: total / renderable / leak-skip / skip% (gold-bearing) ===")
for k, c in by_kind.most_common(30):
    rr = rend_by_kind[k]
    sk = skip_by_kind[k]
    goldk = rr + sk
    if goldk:
        print(f"  {k:30} tot={c:6} rend={rr:6} leakskip={sk:5} skip%={100*sk/goldk:.0f}")
    else:
        print(f"  {k:30} tot={c:6} (no gold verdict)")
print()
# Fully-absent kinds: 100% leak-skip, or 100% no-gold (never reach the corpus)
print("=== FULLY-ABSENT KINDS (contribute 0 trainable anchors) ===")
for k, c in by_kind.most_common(40):
    rr = rend_by_kind[k]
    sk = skip_by_kind[k]
    goldk = rr + sk
    if rr == 0 and c > 0:
        reason = "100% leak-skip" if goldk > 0 else "100% no-gold verdict"
        print(f"  {k:30} tot={c:6}  {reason}")
print()
# Degenerate-head attack: rendered heads at/near the MIN length floor
print("=== DEGENERATE RENDERED HEADS (len <= 30, near MIN floor) ===")
ndeg = 0
for k, samps in head_samples.items():
    for v, h in samps:
        if len(h) <= 30:
            ndeg += 1
            print(f"  [{k}|{v}] len={len(h)} -> {h!r}")
print(f"  (degenerate samples shown: {ndeg})")
print()
print("=== rendered non-invariant heads (LEAK INSPECTION) ===")
for k, samps in head_samples.items():
    for v, h in samps:
        print(f"  [{k}|{v}] {h}")
