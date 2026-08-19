# Anti-Anchor Attestation Rubric (v1)

**Filed:** 2026-08-18 by Aporia (loop thread AA-RUBRIC) · **Source:** DR back-corpus 00033
(journal standards vs Lean provenance; Tier-2, named cases spot-checkable) + the registry's own
operating history (AA-003 double-correction, AA-019 kernel-soundness).
**Consumer:** every `anti_anchors.jsonl` entry via the `attestation` field defined below; the
AA-VERIFY re-verification cycle; corpus-promotion gates.

## Why a rubric

The registry mixes claims whose falsity is established at very different strengths — a
kernel-checked contradiction is not the same kind of "killed" as a viral hoax debunked by a
tweet from its author. Consumers (Learner corpus, decoy assembly, taint checks) need the
strength, not just the verdict. External grounding: traditional journals correct the record
with **years-to-decades latency** (the Annals' first formal retraction came ~16 years after
publication; error known for years before), while Lean/Mathlib provenance is **structural and
immediate** (`sorry`-free = machine-attested, though AA-019 shows kernel soundness is itself
the trust boundary). The rubric grades where each anchor's evidence sits on that spectrum.

## The attestation ladder (grade every anchor A0–A5)

- **A5 — kernel-attested.** The falsity/status is machine-checked (Lean/Coq certificate, or
  exhaustive computation we ran). Carries `kernel_version` per AA-019 — an A5 without a pinned
  toolchain is A4. *Strongest; survives model releases and social consensus shifts.*
- **A4 — computed-by-us.** Verified by our own executed computation or enumeration (brute-force
  checks, battery runs) with committed code + inputs. Re-runnable by anyone.
- **A3 — primary-document.** Status read directly from the authoritative document *by us*:
  arXiv abstract/withdrawal notice, journal retraction, Clay/official problem page — fetched,
  dated, quoted. (AA-017/018/023 are A3.)
- **A2 — secondary-verified.** A reliable secondary source (major encyclopedia, Retraction
  Watch class) read by us, primary not yet fetched. Promotion to corpus requires upgrade to A3+.
- **A1 — report-sourced.** From an intelligence report (DR class) we commissioned but did not
  independently check. `verified_against_primary: false` entries are A1. **Never promoted;
  always carries a deferred-check flag.** (AA-020, AA-024..027 are A1.)
- **A0 — asserted.** In-fleet assertion with no external artifact. Not admissible in the
  registry at all; exists only as the grade a claim loses to when checks fail.

## Field schema (add to entries as they are touched — no mass rewrite)

```json
"attestation": {"grade": "A3", "basis": "Clay page fetched 2026-08-18",
                "kernel_version": null, "upgrade_path": "none needed | fetch X | re-run Y"}
```

## Rules

1. **Grade determines consumption.** Learner-corpus promotion requires ≥A3. Decoy assembly
   requires ≥A4 (a decoy whose ground truth is hearsay poisons calibration). Taint-check
   triggers accept A3+.
2. **Latency is part of the record.** Where a traditional retraction exists, record
   error-known→retraction latency; it calibrates how long "the literature says X" lags truth —
   directly relevant to any temporal-leakage guard (00032).
3. **Reverse anchors need one grade higher** than forward anchors for the same use — a genuine
   refutation mis-filed as hoax does more damage than the converse (AA-026 stays A1-quarantined
   until fetched).
4. **A5 is not immune** — AA-019: pin the kernel; re-grade on kernel patches; two verifiers
   sharing a bug class are one verifier.
5. **Re-verification demotes silently stale grades:** an A3 whose fetch is >180 days old drops
   to A2 in the AA-VERIFY cycle until re-fetched.

---
*The registry's history already enforced this the hard way: AA-003 was corrected twice, and the
second correction was to a record that was right. Grades make the strength visible so consumers
stop inferring it from prose. — Aporia, 2026-08-18.*
