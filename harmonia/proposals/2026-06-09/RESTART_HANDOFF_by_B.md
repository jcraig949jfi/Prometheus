# Restart Handoff — Harmonia B work program (A/B/D/E/F)

**Author:** Harmonia_M2_B  **Written:** 2026-06-15  **HEAD at write:** `cbcf8abb`
**Purpose:** cold-restart restore for this specific work program. Read this + the
files in §2 (≈15 min) and you have full operational state. This supplements — does
not replace — `harmonia/memory/restore_protocol.md` (the general Harmonia boot).

---

## 0. One-paragraph state

I (Harmonia B) authored five proposals to advance Prometheus, James ranked/sequenced
them (A→E→B; D thin; F parked), and three concurrent Harmonia instances (C, D, E)
executed three of them in parallel while I built the shared primitive and acted as
adversarial reviewer + cartographer. **All three lanes closed with decisive results
that converge on one finding** (below). The honest number of novel discoveries is
**zero** — two of the program's most-promising leads were *killed with proofs*. The
work is now in a quiet/holding state; this doc lists what's done and the open items.

**Naming caution:** *Proposals* are lettered A,B,D,E,F (documents). *Harmonia
instances* are lettered B,C,D,E (sessions). They collide. Harmonia **D** executed
Proposal **B**; Harmonia **C** executed Proposal **E**; Harmonia **E** executed
Proposal **D**. I am Harmonia **B**, owner of Proposal **A**.

---

## 1. Infra reality (CHANGED from restore_protocol.md — trust this)

- **Redis / Agora is DOWN** (192.168.1.176:6379 unreachable). `substrate_health()`,
  `tail_sync`, the work queue, the live tensor mirror — all dead. Do NOT rely on them.
- **Postgres is UP** (192.168.1.176:5432) — LMFDB + signals registry live.
- **Coordination is file-based:** artifacts under `harmonia/proposals/2026-06-09/` and
  `harmonia/{primitives,experiments}/`, plus commits to `origin/main`
  (`https://github.com/jcraig949jfi/Prometheus.git`). Many agents push to main
  concurrently → always `git pull --rebase` before pushing; commit messages end with
  the Co-Authored-By trailer.
- **Env primer:** `export PYTHONPATH=. PYTHONIOENCODING=utf-8` before running anything.
- **Gotcha learned 2026-06-15:** other agents leave files *staged-but-uncommitted* in
  the shared index. `git add <specific files>` then commit can sweep them in. Check
  `git status` / `git diff --cached --stat` before committing.

---

## 2. Read-in order (the program, fastest path)

1. `00_SEQUENCING_AND_HANDOFF.md` — James's ranking + the C/D/E assignment + the
   frozen `costume_check` contract. The decision of record.
2. `SYNTHESIS_v2_by_B.md` — **the capstone.** The coordinate-collapse finding, the two
   refuted kill-topography recs, the corrections D forced on my proposals, honest tier.
3. The five proposals (skim): `A_baseline_costume_detector.md`,
   `B_a3_lattice_void_mining.md`, `D_cross_agent_failure_primitive_atlas.md`,
   `E_h2_opaque_kill_backfill.md`, `F_reasoning_ladder_confound_kills.md`.
4. Lane results: `B_RESULTS_2026-06-10.md` (D, a3), `E_RESULTS_2026-06-10.md` (C, h2).
5. My reviews: `REVIEW_C_h2_backfill_by_B.md`, `REVIEW_E_failure_primitives_by_B.md`,
   and `NOTE_D_to_B_costume_evidence_swap.md` (D's correction to me).
6. Shipped code: `harmonia/primitives/baseline_costume.py` (+ `test_baseline_costume_parity.py`),
   `harmonia/primitives/failure_primitives.py`, `harmonia/primitives/lattice_void_miner.py`.

All paths are under `D:\Prometheus\harmonia\proposals\2026-06-09\` unless rooted otherwise.

---

## 3. The central finding (working theory — NOT durable)

**Apparent structure in the substrate repeatedly collapses onto something already
present** — a cheap baseline, an already-available coordinate, or a saturated menu.
Confirmed across five substrates with no shared scour/scoring code:

| Substrate | "Structure" | Collapses onto | Evidence |
|---|---|---|---|
| Erebos L2 | motif routing | per-plugin counter | function-level parity, 25 seeds |
| Theseus h2 | 87K kills (44% volume) | the mechanism: ≤4 bits total | I(tag;Y\|pair)≈0 analytic+empirical |
| Theseus a3 | 250 lattice voids | set-level marginal facts | product-measure theorem (D) |
| Apollo branch-c | evolved comps | fixed-menu zero-improvement tail | FP-003 fired 49/49, 429/480 |
| Techne | search | bounded-menu wall | 90 zero-batches |

**Two standing kill-topography recommendations are refuted with proofs:** rec #2
("recover h2's 44% volume" — it's ≤4 bits, near-zero information) and rec #1 ("a3 voids
= candidate identities" — provably set-level marginal/selection facts; cross-domain
reading is Pattern-30 by construction).

**The north-star how-to the void converges on:** generators need richer **coordinate
systems**, not finer failure labels or more search inside the current menu.

**Tier = working theory, bounded by two open lenses** (see §5): authorship-independence
and information-vs-utility. The bar is ensemble invariance; not yet met.

---

## 4. What shipped (primitives + key artifacts)

- **`harmonia/primitives/baseline_costume.py`** (Proposal A, mine) — the falsification
  gate. `costume_check(claim, rows, baselines, *, key_fn, label_fn, signature_fn,
  comparator, ...) -> CostumeVerdict ∈ {DISTINCT, COSTUME_OF:<b>, INCONCLUSIVE,
  INCONCLUSIVE_DEGENERATE}`. v0 catalog: marginal_majority, volume_weighted, pair_aware.
  Parity-proven against the real Erebos counters (25 seeds). **Degeneracy guard added
  2026-06-15** (D's panel): unique-key aggregators flagged `vacuous`; imbalanced/unique-key
  claims → INCONCLUSIVE_DEGENERATE. Tests: `test_baseline_costume_parity.py` (all green).
- **`harmonia/primitives/failure_primitives.py`** (Proposal D, Harmonia E) — the
  cross-agent failure-primitive atlas (FP-001 baseline_costume, FP-002 opaque_kill,
  FP-003 bounded_menu_wall, +1 added). Lineage-based independence; live detectors;
  generative void hunt (`fp_void_audits_20260610`, `fp_void_map.py`,
  `fp_void_schedule_20260610.json`). FP-003 fired on Apollo (3rd-lineage candidate,
  promotion withheld pending cause audit).
- **`harmonia/primitives/lattice_void_miner.py`** (Proposal B, Harmonia D) — reusable
  void-mining engine; product-measure theorem + set-level certificates. Validator
  `harmonia/experiments/test_lattice_void_miner.py` (14/14). a3 run:
  `harmonia/experiments/a3_lattice_sweep_results.json` (3456 cells, 250 voids, all trivial).
- **h2 law** (Proposal E, Harmonia C) — `harmonia/experiments/h2_info_recovery_law.py`
  + `h2_backfill_and_validate.py` + pre-reg `h2_info_recovery_prereg.md`. Results in the
  `_*results.json` siblings. Found a production bug (index-shift method-misattribution in
  `theseus/generators/h2_triangulation_protocol.py` REJECTED branch) — owed a Theseus ticket.

---

## 5. OPEN ITEMS (pick up here) — ranked

1. **Finish Proposal A (my lane).** Two pieces: (a) refactor Erebos's
   `charon/agents/erebos/sprint1/phase3/{real_residue_smoke,pair_aware_counter}.py` to
   call `costume_check` and prove byte-for-byte verdict parity (the regression that A
   subsumes the bespoke gate; also the real FP-001 anchor); (b) add the `register()`
   hook to `baseline_costume.CATALOG` that Harmonia D requested (set-level baselines
   need clean injection, not `CATALOG[name]=fn` monkey-patching). **My recommended next
   action.**
2. **Authorship-independence probe** — the biggest threat to the central finding. All
   five substrates are code-independent but several were written by the same model;
   "the substrate fools itself the same way" may be a shared-prior of the author. Design
   a cross-model check. Cannot be closed at one author.
3. **h2 cross-generator audit** — C's information-recovery law is proven for h2 only.
   The "law needs ≥3 generators" step: run the same I(label;Y|pair) decomposition on 2+
   other generators; hunt a counterexample on a state-consuming generator (d1 /
   kill-neighborhood) where the conditional-independence premise may break. That
   counterexample, if found, is the real positive.
4. **FP-003 cause adjudication** — is Apollo's zero-improvement tail a structural ceiling
   or a broken gate / Goodhart? E flagged the capacity confound and withheld promotion;
   needs an Apollo-side audit before FP-003 reaches coordinate-invariant.
5. **Read the program-audit 4-prong strategy** (`Program audit 2026-06-10: full-portfolio
   assessment`, landed on main ~commit 070a9096) and re-rank everything against it. I
   never did this; it may supersede the above.
6. **Proposal F (reasoning ladder)** — parked. Pick up only if the next push is
   explicitly "stabilize the reasoning ladder." Note: Icarus cleared R5 since (commit
   ~96814789), which is adjacent.

---

## 6. Standing disposition (how to carry this)

- Falsification-first; the kill is as celebrated as the discovery; report failure
  SHAPES not verdict-lines. `SHADOWS_ON_WALL`: 1 lens = shadow, 3+ independent =
  coordinate-invariant. Reward-signal capture (F043) is the standing hazard.
- I am the adversary the workers need: independently re-run their results, attack my
  own primitives first (D's panel falsified mine twice — that is the system working).
- Every claim clears its own instrument before it is celebrated. Full absolute paths
  in all user-facing output. Commit to main with rebase; verify the staged set first.
- Leave the substrate sharper than found: promote primitives, seed the failure atlas.
