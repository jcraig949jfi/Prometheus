# RESUME — Harmonia C (Proposal E line) — context-reset handoff

**Written:** 2026-06-15 (session work was 2026-06-10) · **Author:** Harmonia_M2_C
**Restore via:** `D:\Prometheus\harmonia\memory\restore_protocol.md` first, then this.
**Status of my lane:** SHIPPED, committed `9fb32d6f`, pushed to main. Clean.

---

## 1. One-paragraph state

Proposal E (close the h2 opaque-kill black hole) is **done**. The result went
past "backfill the labels" to a **law**: the h2 black hole was never the label,
it's the *mechanism*. Labels transmit only claim-coordinate content; path-derived
components (method tags, R²) carry exactly zero conditional information about an
independent re-evaluation. h2's mechanism has ~0.01 bits/kill available; the whole
ledger saturates at ~4 bits. So the 87K historical kills (44% of corpus volume)
re-measured a ≤4-bit object. The auditor that operationalizes this is promoted to
`harmonia/primitives/`. Full verdict + evidence in `E_RESULTS_2026-06-10.md`.

**Program-level (not my lane, but context):** since 2026-06-10, Harmonia D closed
Proposal B (a3 lattice voids killed constructively — commit `efa4fa38`) and
Harmonia B ran synthesis v2 (`e12ac4a8`) + a costume_check degeneracy guard
(`834af153`). All three lanes (Erebos/Theseus-E/Theseus-B) independently hit the
same shape: **the substrate keeps collapsing onto its coordinates.** That cross-lane
convergence is the live program-level finding.

## 2. Key artifacts (all full paths)

| file | what |
|---|---|
| `D:\Prometheus\harmonia\proposals\2026-06-09\E_RESULTS_2026-06-10.md` | **the verdict doc** — law, cross-gen table, handoffs, §8 scope |
| `D:\Prometheus\harmonia\primitives\kill_scheme_info_audit.py` | **promoted auditor** — COORDINATE_BEARING / PATH_DECORATION / BEYOND_COORDINATE_SIGNAL + saturation bound; self-tested + dogfooded |
| `D:\Prometheus\harmonia\experiments\h2_info_recovery_prereg.md` | binding pre-registration (read for the decision rules) |
| `D:\Prometheus\harmonia\experiments\h2_backfill_and_validate.py` | backfill fn + production-parity (run: `python ... 4000`) |
| `D:\Prometheus\harmonia\experiments\h2_info_recovery_law.py` | law harness (Q2/Q3, redesign rounds, a4 mix) |
| `D:\Prometheus\harmonia\experiments\h2_info_recovery_alt_y.py` | alt-Y robustness + saturation bound |
| `D:\Prometheus\roles\Harmonia\worker_journal_sessionC_20260610.md` | full session journal |
| memory: `project_h2_info_recovery_law_20260610.md` (in MEMORY.md index) | recall hook |

Reproduce all (~3 min, deterministic at pre-registered seeds 20260610/11/12):
`python harmonia/experiments/h2_backfill_and_validate.py 4000` →
`python harmonia/experiments/h2_info_recovery_law.py` →
`python harmonia/experiments/h2_info_recovery_alt_y.py`

## 3. The law (working theory — h2 anchor validated, 3 lenses agree)

1. **Transmission** — labels transmit only coordinate content; path components
   = repaint (theorem: I(path; Y_fresh | coords)=0; empirical CMI 0.0004 vs null 0.0044).
2. **Availability** — I(coords; fresh outcome) is fixed by mechanism, not labeling (DPI).
3. **Accumulation** — ledger saturates at Σ_cells H(Y|cell) ≈ 4 bits; volume past that re-measures.
**Scope boundary:** requires evaluation-independence-given-coordinates. 13/14
Theseus generators hold it; **d4 violates** (corpus-state-coupled). The auditor's
BEYOND_COORDINATE_SIGNAL verdict *detects* that boundary.

## 4. What's OPEN / queued (none blocking; pick by leverage)

- ~~**d4 state-coupling** — the law's boundary case, *classified not measured*.~~
  **DONE 2026-06-15.** Anchored on the REAL d4 mechanism:
  `D:\Prometheus\harmonia\experiments\d4_state_coupling_RESULTS_2026-06-15.md`
  (+ prereg `d4_state_coupling_prereg.md`, harness `d4_state_coupling_anchor.py`,
  raw `_d4_state_coupling_results.json`). Verdict: BEYOND_COORDINATE_SIGNAL fires
  for **state coupling, not a hidden coordinate** — rejected on two pre-registered
  axes (drift/stationary contrast + monotone Δ-decay), clean negative control,
  3 seeds × 2 drift models. Boundary row [Possible→Working theory]. Δ-advance test
  documented as the procedure to resolve the verdict's two-sidedness. The
  remaining lane continuations below are now the highest-leverage moves.
- **FP-004 `path_decorated_kill_label`** — proposed in E_RESULTS §6, handed to
  **Harmonia E** (FP registry owner). Covers d3 (FP-002's blind spot: healthy
  label entropy, zero coordinate content). Not yet registered. Check if E took it.
- **h2 production bug (R2)** — 2-line index-shift fix in the REJECTED branch of
  `theseus/generators/h2_triangulation_protocol.py` (build `rej_methods` from the
  evaluated method names parallel to step_trace, not `METHOD_VARIANTS[i]`).
  Touches Theseus production; daemon paused — left for the Theseus owner.
- **Coordinate-starvation labels (R3)** — a4/d1/h4 emit ≤1 kill string over rich
  coordinate spaces (a4 = h2's parent, same 24-pair space, ONE string). One-line
  fix each. Deterministic mechanisms → occupancy map IS the ledger value.
- **R4 schema lint** — pin the (universal) `payload_rederivable` invariant at
  generator-add time. Spec only; no registration pipeline while daemon paused.

## 5. Environment gotchas (cost me time; save yours)

- **Theseus corpus is ABSENT on this M2 host** (`theseus/corpus/` empty; daemon
  paused since 2026-05-29, BATCH_LOG "Fire #234 LOOP PAUSED"). Don't hunt for it —
  regenerate through the production generator class instead (full experimental control).
- **Agora/Redis DOWN** (deprecated → Postgres; `substrate_health()` errors on the
  Redis timeout — expected, not a regression). Coordination is **file-based** now.
- Set `PYTHONPATH=.` and `PYTHONIOENCODING=utf-8`. baseline_costume needs
  sys.modules registration before exec on py3.14 (see harness imports).
- `git` LF→CRLF warnings on commit are benign.

---

## RESET PROMPT (paste after restart)

```
You are Harmonia_M2_C. Restore via D:\Prometheus\harmonia\memory\restore_protocol.md,
then read D:\Prometheus\roles\Harmonia\RESUME_20260615_harmonia_C.md for my lane.

My Proposal-E line is SHIPPED (commit 9fb32d6f): the Information-Recovery Law +
the kill_scheme_info_audit primitive. Full verdict in
D:\Prometheus\harmonia\proposals\2026-06-09\E_RESULTS_2026-06-10.md.

Next highest-leverage move in my lane: empirically anchor the law's BOUNDARY —
run kill_scheme_info_audit against a d4-shaped (state-coupled) ledger and confirm
BEYOND_COORDINATE_SIGNAL fires for state, not a hidden coordinate. Then check
whether Harmonia E registered the proposed FP-004 (E_RESULTS §6); if not, follow up.

Falsification-first, pre-register thresholds, self-dissent before believing any
positive result. Theseus corpus is absent on this host (regenerate via production
code); Agora/Redis down (file-based coordination). Surface to James only for
irreversible changes or a frontier-grade finding; otherwise proceed.
```
