# Local-Dataset Strategy for the Prometheus Arsenal

**Question:** Would more local datasets help the prometheus_math tools?

**Short answer:** Yes — substantially, in three ways:

1. **Resilience against API gating.** OEIS's JSON search endpoint is currently
   Cloudflare-blocked from this network. A local OEIS mirror (~1.5 GB
   compressed) makes lookup near-instant and offline.
2. **Throughput.** Bulk scans (the kind Charon and Ergon run regularly) on
   the LMFDB Postgres mirror at devmirror.lmfdb.xyz are network-bound. A
   local Postgres replica is 50–500× faster on aggregate queries.
3. **Reproducibility.** A research result depending on "the live state of
   LMFDB on date X" is fragile. A versioned local snapshot is durable.

---

## Already local

- **LMFDB Postgres mirror** subset (per `cartography/shared/scripts/
  lmfdb_postgres_dump.py`). Tables already dumped: `hecke_*`,
  `mf_hecke_*`, `smf_*`, `g2c_*`, `ec_*`, `nf_fields`, `modcurve_*`,
  `maass_*`. Dumped to `cartography/lmfdb_dump/` (per memory note).
  Status: useful for cross-check but the live mirror is preferred for
  freshness.
- **KnotInfo + LinkInfo** via `database_knotinfo` pip package, which
  ships the full ~13 K knot + 4 K link census in-package (~17 MB
  wheel). Status: 🟢 fully local, no network needed.

---

## High-priority dataset acquisitions

Ranked by impact-per-GB on Prometheus research today.

### 1. OEIS local mirror — HIGHEST PRIORITY

**Why:** Resolves the Cloudflare blocker on `prometheus_math.databases.oeis`.
OEIS is used by Aporia for conjecture seeding and by anyone running a
sequence-comparison cross-check.

**Data:** OEIS publishes `stripped.gz` (~50 MB compressed: A-numbers + first
30-50 terms) and `names.gz` (~5 MB: A-number → name mapping). Together
they cover the most common queries. The full dump including b-files,
formulas, programs, references is ~1.5 GB.

**Source:** https://oeis.org/wiki/QandA_For_New_OEIS#Q:_How_can_I_download_the_complete_OEIS.3F
(direct download links published; refresh nightly)

**Integration:** Modify `prometheus_math/databases/oeis.py` to check a local
mirror at `$PROMETHEUS_DATA_DIR/oeis/stripped.gz` (or wherever) before
falling back to the API. `is_known(values)` and `lookup(A_number)` both
become near-instant.

**Cost:** ~50 MB minimal, ~1.5 GB full. Refresh weekly via cron or CI.

---

### 2. Mathlib Lean corpus snapshot — HIGH PRIORITY

**Why:** Future Lean integration (Tier 6 of ARSENAL_ROADMAP). Having a
snapshot of Mathlib lets us:
- Train a small AI tactic-suggester on it (locally, no third-party
  inference service)
- Run lemma-search queries without booting full Lean
- Diff against new releases for capability tracking

**Data:** Mathlib4 source ~1.5 GB (cloneable via git). Compiled
`.olean` files for our local Lean version: another ~5 GB. The
preprocessed AST corpus (used by AlphaProof / DeepSeek-Prover) is
typically distributed as JSONL ~10–20 GB.

**Source:** https://github.com/leanprover-community/mathlib4 (source);
HuggingFace `leanprover/mathlib4` (preprocessed dumps).

**Integration:** `prometheus_math/lean.py` (future module) checks
`$LEAN_PATH` for Mathlib; uses local AST corpus for lemma search.

**Cost:** ~1.5 GB source minimum; full corpus ~20 GB.

---

### 3. Mossinghoff Mahler-measure tables — MEDIUM-HIGH PRIORITY

**Why:** Charon's Lehmer/Salem work this session relied on cross-checking
against Mossinghoff's published tables, which I had to do from memory.
Loading them locally makes that cross-check robust and machine-readable.

**Data:** Mossinghoff publishes machine-readable lists of small Mahler
measures up to degree ~44, including the polynomial coefficients,
M(f), and known Salem/Lehmer family memberships. Total ~few MB.

**Source:** Michael Mossinghoff's homepage at Davidson:
https://wayback.cecm.sfu.ca/~mjm/Lehmer/

**Integration:** New module `prometheus_math/databases/mahler.py`
exposing `mossinghoff_table()`, `lookup_polynomial(coeffs)`,
`smallest_known(degree)`. Useful for any Lehmer-conjecture audit.

**Cost:** ~5 MB. Trivial to mirror.

---

### 4. ATLAS of Finite Groups — MEDIUM PRIORITY

**Why:** When GAP gets installed (Tier 3 native), ATLAS data becomes the
authoritative reference for finite simple group representations,
character tables, Schur multipliers. Useful for Aporia's Galois /
modular-form correspondence work.

**Data:** ATLAS data ships with GAP, but standalone JSON/CSV exports
also exist (~50 MB). Several finite-group cohomology databases (Carlson
et al.) supplement.

**Source:** https://brauer.maths.qmul.ac.uk/Atlas/v3/ (online ATLAS);
GAP ships a copy.

**Integration:** Couples with future `prometheus_math/groups.py` GAP
wrapper. Until GAP is installed, parse a JSON export directly.

**Cost:** ~50 MB.

---

### 5. Cremona's elliptic curve database (CSV form) — LOW PRIORITY

**Why:** Already accessible via LMFDB at devmirror.lmfdb.xyz (3.8 M
curves). A local CSV is faster for bulk scans (no SQL round trip), but
LMFDB is rich enough that the redundancy isn't urgent.

**Data:** `allcurves.cremona.csv` (~600 MB), with conductor, ainvs,
rank, regulator, sha_an, etc.

**Source:** John Cremona's GitHub: https://github.com/JohnCremona/ecdata

**Integration:** Optional local-mirror flag in
`prometheus_math.databases.lmfdb.elliptic_curves` — check local CSV
before SQL.

**Cost:** ~600 MB.

---

### 6. arXiv metadata bulk dump — LOW-MEDIUM PRIORITY

**Why:** The `arxiv` pip API is fast enough for typical search, but
training/finetuning ML models on arXiv requires bulk metadata.

**Data:** arXiv metadata snapshot via Kaggle: ~2 GB (titles, abstracts,
authors, categories, dates for ~2.5 M papers). Full PDFs: ~1 TB.

**Source:** https://www.kaggle.com/datasets/Cornell-University/arxiv

**Integration:** Optional metadata-snapshot mode for
`prometheus_math.databases.arxiv` for offline literature mining.

**Cost:** ~2 GB metadata only. Full PDFs out of scope.

---

### 7. Combinatorics / graph / 3-manifold censuses — MEDIUM PRIORITY (specialty)

Several niche but research-grade datasets:

- **Brendan McKay's graph census** (graphs on N vertices, all
  isomorphism classes): ~few GB up to N=10
- **Burnside / sporadic group character tables** (small, in-GAP)
- **3-manifold triangulation census** (Hodgson-Weeks-Burton orientable
  closed): ~few hundred MB; complements SnapPy's built-in censuses
- **Schöning's k-SAT instance database**: useful for SAT-based
  research

**Cost:** sub-GB each. Acquire as specific research needs surface.

---

## Architectural recommendation: local-first wrappers

The wrappers in `prometheus_math.databases.*` should adopt a uniform
**local-mirror-first** pattern:

```python
import prometheus_math as pm

# Configuration: ~/.prometheus or env var PROMETHEUS_DATA_DIR
# pm.databases.config.set_data_dir("/path/to/data")

# Each wrapper checks local mirror first, falls back to API
result = pm.databases.oeis.lookup('A000045')  # local hit; no network
result = pm.databases.lmfdb.elliptic_curves(label='37.a1')  # local CSV if present, else SQL
result = pm.databases.knotinfo.lookup('3_1')  # already 100% local via pip pkg
```

**Implementation sketch:**

```python
# prometheus_math/databases/_local.py (new helper module)
def data_dir() -> Path:
    """Resolve $PROMETHEUS_DATA_DIR or ~/.prometheus_data, create if absent."""

def has_mirror(name: str) -> bool:
    """Check whether dataset mirror exists locally."""

def mirror_path(name: str) -> Path:
    """Return path to local mirror; download on first call if absent."""

def update_mirror(name: str, force=False) -> None:
    """Refresh local mirror from upstream."""
```

Each wrapper module then has a `_lookup_local()` that's tried first, with
the API call as fallback.

**A `tools/` script** for one-shot mirror updates:

```bash
python -m prometheus_math.databases.update_mirrors --datasets oeis,mahler
```

CI can run this weekly to keep mirrors fresh.

---

## Recommended next steps (priority order)

1. **Build `prometheus_math/databases/_local.py`** — the mirror
   abstraction (~80 lines).
2. **Acquire OEIS `stripped.gz`** — solves Cloudflare blocker (highest
   impact-per-effort). Wire into `oeis.lookup()` and `oeis.is_known()`
   as a local-first lookup.
3. **Acquire Mossinghoff tables** — small file, immediate value for
   Charon's Lehmer work.
4. **Build `prometheus_math/databases/mahler.py`** wrapping the
   Mossinghoff data (~150 lines).
5. **Plan Mathlib snapshot acquisition** — coordinated with Lean 4
   install (Tier 3 of ARSENAL_ROADMAP). Hold until Lean is wired up.
6. **Cremona local CSV** — defer; LMFDB live is sufficient for now.

These add up to ~1.6 GB of local data plus ~250 lines of code, with
the OEIS Cloudflare resolution alone being a near-immediate win.

---

## Status integration with ARSENAL_ROADMAP

This document expands `techne/ARSENAL_ROADMAP.md` Tier 5 ("web service
wrappers") to formally include the local-mirror complement. Each Tier-5
target now has TWO status fields:

- **Wrapper status** — whether the API client exists and works
- **Local mirror status** — whether a local snapshot is available for
  offline / fast access

Many high-value targets are 🟢 wrapper / 🟠 mirror today; the
recommendation is to close the mirror gap on the highest-traffic
datasets (OEIS, Mossinghoff first).

---

*Compiled by Techne, 2026-04-25.*
