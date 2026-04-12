# Charon Spectral Survey — Sprint Plan
## "Point the telescope at everything"
## Date: 2026-04-04

---

## Mission

Confirm or falsify the universal spectral compression phenomenon across
every L-function family accessible in LMFDB. Three families already show
the sign inversion (EC, genus-2, modular forms). We fan out to every
remaining family simultaneously.

This is exploration, not publication. Speed over polish. Every agent
runs the same protocol. Results converge to a shared table. We interpret
after the data is in.

---

## The Protocol (Same for Every Agent)

Every agent executes the identical 5-step Charon methodology:

### Step 1: Ingest
- Pull objects from LMFDB API for the assigned family
- Download precomputed zeros (LMFDB stores first N zeros for most objects)
- Record: object label, conductor, rank/degree/dimension (whatever the
  structural parameter is for this family), zero values

### Step 2: Compute Spacing
- For each object, compute normalized zero gaps: z1-z2, z2-z3, ..., z19-z20
- Normalize by mean spacing (so gaps are comparable across conductors)
- Group objects by structural parameter (rank, degree, dimension, etc.)

### Step 3: Compare to Baseline
- Use rank-0 / degree-1 / lowest-structural-parameter group as reference
- Compute Cohen's d for each gap between reference group and each
  higher-structure group
- Record the SIGN of each Cohen's d — positive = wider gaps (RMT
  prediction), negative = tighter gaps (our phenomenon)

### Step 4: Dose-Response
- If multiple structural levels exist (rank 0,1,2,3 or degree 1,2,3,4),
  check whether effect scales monotonically with structure
- Compute Spearman correlation between structural parameter and gap
  compression

### Step 5: Conductor Control
- Bin objects by conductor (low/medium/high)
- Check whether the sign inversion persists within each bin
- If effect disappears at high conductor → pre-asymptotic
- If effect persists → genuine

### Output Format (EVERY agent produces this)

```json
{
  "family": "number_fields",
  "degree": 1,
  "symmetry_type": "unknown",
  "structural_parameter": "degree",
  "structural_levels": [1, 2, 3, 4, 5],
  "n_objects_per_level": [1000, 2000, 1500, 800, 200],
  "total_objects": 5500,
  "gaps_measured": "z1-z2 through z19-z20",
  "reference_group": "degree_1",
  "cohens_d_by_gap": {
    "z1_z2": [-0.05, -0.12, -0.18, -0.25],
    "z2_z3": [-0.08, -0.15, -0.22, -0.30],
    "...": "..."
  },
  "all_negative": true,
  "dose_response_spearman": -0.94,
  "conductor_independent": true,
  "verdict": "SIGN_INVERSION_CONFIRMED"
}
```

Verdicts:
- SIGN_INVERSION_CONFIRMED — all/nearly all gaps negative, dose-response present
- SIGN_INVERSION_PARTIAL — some gaps negative, pattern unclear
- NO_EFFECT — gaps near zero, no systematic sign
- OPPOSITE — gaps positive (RMT prediction holds, our phenomenon doesn't apply)
- INSUFFICIENT_DATA — not enough objects or zeros available

---

## The Five Families (Agent Assignments)

### Agent 1: Number Fields (Dedekind Zeta Functions)

**LMFDB endpoint:** `https://www.lmfdb.org/api/nf/fields/`
**Structural parameter:** Degree (1, 2, 3, 4, 5, 6+)
**Expected objects:** 500,000+ number fields in LMFDB
**Zeros available:** First 10-20 zeros for many fields
**What to look for:** Does higher field degree compress spectral gaps?
**Secondary parameter:** Discriminant (analog of conductor)
**Why it matters:** Dedekind zeta functions are degree-1 L-functions
attached to number fields. If the sign inversion appears here, it
extends the phenomenon to the simplest possible L-function family
beyond Riemann zeta itself.

### Agent 2: Dirichlet Characters (Dirichlet L-functions)

**LMFDB endpoint:** `https://www.lmfdb.org/api/char/Dirichlet/`
**Structural parameter:** Order of character (1, 2, 3, 4, ...)
**Expected objects:** Tens of thousands
**Zeros available:** Extensive — these are the best-computed L-functions
**What to look for:** Does higher character order compress spectral gaps?
**Secondary parameter:** Modulus (conductor)
**Why it matters:** Dirichlet L-functions are the simplest non-trivial
L-functions. If the phenomenon appears here, it's as universal as
possible. If it DOESN'T appear here, the phenomenon requires more
complex arithmetic structure (rank, not just character data).
**IMPORTANT:** We already killed raw Dirichlet coefficients as a
representation in the original Charon sprint. This is different — we're
looking at ZERO SPACING, not coefficient geometry.

### Agent 3: Artin Representations

**LMFDB endpoint:** `https://www.lmfdb.org/api/artin/`
**Structural parameter:** Dimension of representation (1, 2, 3, 4+)
**Expected objects:** ~10,000 in LMFDB
**Zeros available:** Varies — may need to compute
**What to look for:** Does higher representation dimension compress gaps?
**Secondary parameter:** Conductor
**Why it matters:** Artin representations are the Galois side of
Langlands. If tail signatures detect representation dimension, we're
seeing Langlands structure through spectral geometry.

### Agent 4: Maass Forms

**LMFDB endpoint:** `https://www.lmfdb.org/api/mf/maass/`
**Structural parameter:** Spectral parameter R (eigenvalue on the
hyperbolic Laplacian)
**Expected objects:** ~20,000 in LMFDB
**Zeros available:** First zeros computed for many forms
**What to look for:** Does spectral parameter R correlate with gap
compression? This is different from rank — Maass forms don't have
algebraic rank, but they have a continuous spectral parameter that
controls their analytic behavior.
**Why it matters:** Maass forms are non-holomorphic. If the phenomenon
appears here, it's not specific to holomorphic/algebraic objects. That
would be a major extension.

### Agent 5: Hilbert Modular Forms (and Cross-Family Bridges)

**LMFDB endpoint:** `https://www.lmfdb.org/api/hmf/forms/`
**Structural parameter:** Parallel weight, level norm
**Expected objects:** ~500,000 in LMFDB
**Zeros available:** Limited — this is the hardest family
**What to look for:** Weight and level effects on gap spacing
**SECONDARY MISSION:** After computing signatures for this family,
cross-reference ALL families' tail signatures. Build the cross-type
landscape. Look for objects from different families whose tail
signatures cluster together. Every cross-type cluster is a candidate
Langlands bridge.

---

## Shared Infrastructure

### Results Directory

```
F:\Prometheus\charon\spectral_survey\
├── protocol.md              ← this file (copied to each agent)
├── results/
│   ├── number_fields.json   ← Agent 1 output
│   ├── dirichlet.json       ← Agent 2 output
│   ├── artin.json           ← Agent 3 output
│   ├── maass.json           ← Agent 4 output
│   ├── hilbert.json         ← Agent 5 output
│   └── cross_family.json    ← Agent 5 secondary mission
├── raw_data/
│   ├── nf_zeros/            ← downloaded zero data per family
│   ├── dirichlet_zeros/
│   ├── artin_zeros/
│   ├── maass_zeros/
│   └── hilbert_zeros/
├── scripts/
│   ├── lmfdb_ingest.py      ← shared LMFDB API client
│   ├── spacing_analysis.py  ← shared gap computation
│   ├── rmt_comparison.py    ← shared Cohen's d computation
│   └── landscape_builder.py ← cross-family clustering
└── summary/
    └── survey_results.md    ← consolidated findings
```

### Shared Python Module: spacing_analysis.py

Each agent imports this. It implements the core computation:

```python
"""
spacing_analysis.py — Core spectral gap analysis.
Shared across all Charon spectral survey agents.
"""

import numpy as np
from scipy import stats


def compute_normalized_gaps(zeros: list[float], n_gaps: int = 19) -> list[float]:
    """Compute normalized gaps between consecutive zeros.
    
    Args:
        zeros: Sorted list of zero values (imaginary parts)
        n_gaps: Number of gaps to compute (default 19 = z1-z2 through z19-z20)
    
    Returns:
        List of normalized gap values. Normalized by mean spacing.
    """
    if len(zeros) < n_gaps + 1:
        return []
    
    gaps = []
    for i in range(n_gaps):
        gaps.append(zeros[i + 1] - zeros[i])
    
    mean_gap = np.mean(gaps)
    if mean_gap <= 0:
        return []
    
    return [g / mean_gap for g in gaps]


def group_by_parameter(objects: list[dict], param_name: str) -> dict:
    """Group objects by structural parameter value.
    
    Args:
        objects: List of dicts with 'zeros' and param_name fields
        param_name: Name of structural parameter (e.g., 'rank', 'degree')
    
    Returns:
        Dict mapping parameter value -> list of gap arrays
    """
    groups = {}
    for obj in objects:
        val = obj.get(param_name)
        if val is None:
            continue
        gaps = compute_normalized_gaps(obj['zeros'])
        if gaps:
            groups.setdefault(val, []).append(gaps)
    return groups


def compute_cohens_d(group_a: list, group_b: list) -> float:
    """Cohen's d effect size between two groups."""
    a = np.array(group_a)
    b = np.array(group_b)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    
    pooled_std = np.sqrt(
        ((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1))
        / (na + nb - 2)
    )
    if pooled_std == 0:
        return 0.0
    
    return (np.mean(a) - np.mean(b)) / pooled_std


def sign_inversion_analysis(groups: dict, reference_key,
                             n_gaps: int = 19) -> dict:
    """Full sign inversion analysis.
    
    Args:
        groups: Dict from group_by_parameter (param_value -> list of gap arrays)
        reference_key: Which parameter value is the reference (e.g., rank 0)
        n_gaps: Number of gaps to analyze
    
    Returns:
        Dict with Cohen's d per gap per comparison group,
        dose-response statistics, and verdict.
    """
    if reference_key not in groups:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "reference group missing"}
    
    ref_gaps = np.array(groups[reference_key])  # shape: (n_objects, n_gaps)
    if len(ref_gaps) < 10:
        return {"verdict": "INSUFFICIENT_DATA", "reason": f"reference group too small: {len(ref_gaps)}"}
    
    comparison_keys = sorted([k for k in groups.keys() if k != reference_key])
    if not comparison_keys:
        return {"verdict": "INSUFFICIENT_DATA", "reason": "no comparison groups"}
    
    results = {
        "reference": reference_key,
        "n_reference": len(ref_gaps),
        "comparisons": {},
        "all_negative_count": 0,
        "total_comparisons": 0,
    }
    
    all_ds = []
    
    for comp_key in comparison_keys:
        comp_gaps = np.array(groups[comp_key])
        if len(comp_gaps) < 10:
            continue
        
        ds = []
        for gap_idx in range(min(n_gaps, ref_gaps.shape[1], comp_gaps.shape[1])):
            d = compute_cohens_d(ref_gaps[:, gap_idx], comp_gaps[:, gap_idx])
            ds.append(round(d, 4))
        
        n_negative = sum(1 for d in ds if d < 0)
        results["comparisons"][str(comp_key)] = {
            "n_objects": len(comp_gaps),
            "cohens_d": ds,
            "n_negative": n_negative,
            "n_total": len(ds),
            "fraction_negative": round(n_negative / max(len(ds), 1), 3),
        }
        results["total_comparisons"] += len(ds)
        results["all_negative_count"] += n_negative
        all_ds.extend([(comp_key, d) for d in ds])
    
    # Dose-response: correlation between structural parameter and mean d
    if len(comparison_keys) >= 2:
        param_values = []
        mean_ds = []
        for comp_key in comparison_keys:
            if str(comp_key) in results["comparisons"]:
                param_values.append(float(comp_key))
                mean_ds.append(np.mean(results["comparisons"][str(comp_key)]["cohens_d"]))
        
        if len(param_values) >= 2:
            spearman_r, spearman_p = stats.spearmanr(param_values, mean_ds)
            results["dose_response"] = {
                "spearman_r": round(float(spearman_r), 4),
                "spearman_p": round(float(spearman_p), 6),
            }
    
    # Verdict
    if results["total_comparisons"] == 0:
        results["verdict"] = "INSUFFICIENT_DATA"
    else:
        frac_negative = results["all_negative_count"] / results["total_comparisons"]
        results["fraction_all_negative"] = round(frac_negative, 3)
        
        if frac_negative >= 0.85:
            results["verdict"] = "SIGN_INVERSION_CONFIRMED"
        elif frac_negative >= 0.65:
            results["verdict"] = "SIGN_INVERSION_PARTIAL"
        elif frac_negative <= 0.35:
            results["verdict"] = "OPPOSITE"
        else:
            results["verdict"] = "NO_EFFECT"
    
    return results


def conductor_control(objects: list[dict], param_name: str,
                       conductor_name: str = 'conductor',
                       reference_key=None, n_bins: int = 3) -> dict:
    """Check whether sign inversion persists across conductor bins.
    
    Bins objects by conductor, runs sign_inversion_analysis within each bin.
    If effect persists in all bins → conductor-independent.
    If effect weakens in high-conductor bin → pre-asymptotic.
    """
    conductors = [obj[conductor_name] for obj in objects if conductor_name in obj]
    if not conductors:
        return {"verdict": "NO_CONDUCTOR_DATA"}
    
    # Compute bin edges
    percentiles = np.linspace(0, 100, n_bins + 1)
    edges = np.percentile(conductors, percentiles)
    
    bin_results = {}
    for b in range(n_bins):
        lo, hi = edges[b], edges[b + 1]
        bin_objects = [
            obj for obj in objects
            if conductor_name in obj and lo <= obj[conductor_name] <= hi
        ]
        groups = group_by_parameter(bin_objects, param_name)
        if reference_key is not None and reference_key in groups:
            analysis = sign_inversion_analysis(groups, reference_key)
            bin_results[f"bin_{b}_({lo:.0f}-{hi:.0f})"] = {
                "n_objects": len(bin_objects),
                "verdict": analysis.get("verdict", "UNKNOWN"),
                "fraction_negative": analysis.get("fraction_all_negative", None),
            }
    
    # Check if all bins confirm
    verdicts = [v["verdict"] for v in bin_results.values()]
    all_confirmed = all(v == "SIGN_INVERSION_CONFIRMED" for v in verdicts)
    
    return {
        "bins": bin_results,
        "conductor_independent": all_confirmed,
        "verdict": "CONDUCTOR_INDEPENDENT" if all_confirmed else "CONDUCTOR_DEPENDENT",
    }
```

---

## Agent Deployment

### Option A: Sequential (1 Claude Code agent, 5 runs)
- Time: ~2-3 hours per family × 5 = 10-15 hours
- Pro: Simple, no coordination needed
- Con: Slow

### Option B: Parallel on 2 machines (2-3 agents simultaneously)
- M1: Agent 1 (number fields) + Agent 2 (Dirichlet)
- M2: Agent 3 (Artin) + Agent 4 (Maass) + Agent 5 (Hilbert)
- Time: ~3-5 hours total
- Pro: Fast, within a single session
- Con: Needs 2 Claude Code windows running simultaneously

### Option C: Maximum parallelism (5 agents)
- Each agent in its own Claude Code window/tab
- All five families simultaneously
- Time: ~2-3 hours
- Pro: Fastest possible
- Con: Token burn across all agents

### RECOMMENDED: Option B
Two machines, 2-3 families per machine, done by tonight.
Apollo keeps running on both machines in the background —
this is CPU+network work (LMFDB API calls + numpy), not GPU work.
No conflict with Apollo's GPU usage.

---

## Each Agent Gets

1. This protocol document
2. The Charon role document (for methodology principles)
3. `spacing_analysis.py` (shared computation module)
4. Their specific family assignment (endpoint, structural parameter, what to look for)
5. An output path for their results JSON

### Agent Prompt Template

```
You are Charon, the Cross-Domain Cartographer. Your mission today is
to test whether the spectral compression phenomenon — higher arithmetic
structure producing tighter zero spacing, opposite to RMT prediction —
extends to [FAMILY NAME] L-functions.

Read the protocol document at [PATH]. Execute the 5-step methodology
on [FAMILY] data from LMFDB. Use the shared spacing_analysis.py module
for core computations.

Your structural parameter is [PARAMETER]. Your reference group is
[REFERENCE]. You are looking for negative Cohen's d values across
zeros 1-20 gaps, scaling with [PARAMETER].

Deposit your results JSON to:
F:\Prometheus\charon\spectral_survey\results\[FAMILY].json

Work fast. Explore first, polish later. If LMFDB API is slow, cache
aggressively. If a family has insufficient zeros precomputed, note it
and move to the next analysis.

The forcing principle applies: record your thresholds BEFORE looking
at data. Sign inversion confirmed = ≥85% of gap comparisons negative.
Partial = 65-85%. No effect = 35-65%. Opposite = ≤35%.

Go.
```

---

## After All Agents Report

### Consolidation (30 minutes, human + Claude)

1. Collect all 5 results JSONs
2. Build the summary table:

```
| Family          | Degree | Param     | Levels | N     | Verdict              | Dose-Response | Conductor |
|-----------------|--------|-----------|--------|-------|----------------------|---------------|-----------|
| Elliptic Curves | 2      | rank      | 0,1    | 336K  | CONFIRMED            | yes           | FLAT      |
| Genus-2         | 4      | rank      | 0,1,2,3| 3K    | CONFIRMED            | yes (3x)      | ?         |
| Modular Forms   | 2      | dimension | 1-5    | ?     | CONFIRMED            | yes           | ?         |
| Number Fields   | 1      | degree    | 1-6    | ?     | ?                    | ?             | ?         |
| Dirichlet       | 1      | order     | 1-4+   | ?     | ?                    | ?             | ?         |
| Artin           | varies | dim       | 1-4    | ?     | ?                    | ?             | ?         |
| Maass           | 2      | R         | cont.  | ?     | ?                    | ?             | ?         |
| Hilbert         | 2      | weight    | varies | ?     | ?                    | ?             | ?         |
```

3. If ≥5/8 families show CONFIRMED: the phenomenon is universal.
   Write the cross-family paper.

4. If 3-4/8 show CONFIRMED and others show NO_EFFECT: the phenomenon
   requires specific arithmetic structure (rank/dimension, not just
   any structural parameter). That's also a finding — it tells you
   what the telescope detects and what it doesn't.

5. If only the original 3 show CONFIRMED: the phenomenon is real but
   specific to algebraic rank and modular form dimension. Still
   publishable as a three-family result.

6. Cross-family landscape (Agent 5's secondary mission): if any
   cross-type clustering emerges, that's the bridge-building result
   that connects to the Langlands telescope vision.

---

## IMPORTANT: What NOT to Do

- Do NOT strip 15 mechanisms on every family. That's weeks of work.
  Just get the sign and the dose-response. Mechanism stripping comes
  later for confirmed families.
- Do NOT compute Ollivier-Ricci curvature or build geometric landscapes.
  That's Phase 2. This is Phase 1: sign, magnitude, dose-response.
- Do NOT try to explain WHY. Collect the data. The theory comes after
  the measurements.
- Do NOT wait for perfect data. If a family has 100 objects with zeros,
  that's enough for a preliminary verdict. Note the N and move on.

---

## Timeline

| Time     | Action |
|----------|--------|
| Hour 0   | Deploy agents on M1 and M2 |
| Hour 1   | First results (Dirichlet — best-computed family, fastest) |
| Hour 2   | Number fields + Artin results |
| Hour 3   | Maass + Hilbert results |
| Hour 4   | Cross-family consolidation |
| Hour 5   | Summary table complete. Decision on next steps. |

---

*The telescope is built. The lens is ground. Point it at the sky.*
*Every L-function family is a star. We're checking if they all*
*twinkle the same way.*