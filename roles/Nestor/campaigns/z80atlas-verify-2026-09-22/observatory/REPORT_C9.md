# Cycle 9 -- verification report

Generated from `ADJUDICATION_C9.json`; every number below is rendered from the machine block and recomputed from the raw bundle files by `report_audit_c9.py`.
Provenance: protocol `5819bc6d20f1421802db5fca99e32564139cc604bafe3689f4003ac2f4134c8d`, manifest `8d88cf06123b6e62c85c356a65c85a5d9903b220d09979ba71b20509241ea67a`.

<!-- MACHINE-BEGIN
{
 "H1": {
  "I": 0.0,
  "M": 0.0,
  "means_held_final": {
   "gate_off_cost_free": 0.325,
   "gate_off_cost_vm": 0.325,
   "gate_on_cost_free": 0.325,
   "gate_on_cost_vm": 0.325
  },
  "n_complete": 60,
  "threshold": 0.15,
  "verdict": "NO_DETECTED_EFFECT"
 },
 "H2": {
  "distinct_supporting_strata": 0,
  "per_specimen": {
   "03650e1ad792eefa-s9040-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "08b4c94e2ea65998-s76929-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "193576337017c94a-s74845-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "2c45891544a22e46-s8700-tM-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "48c75e149fc7d62d-s12269-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "4931614d912c52b2-s1190-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "6da4c0b9a40141f8-s5058-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "7ae3f9c1437c8000-s54765-tL-a0": {
    "B_reaching": 4,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "9cba7113df39009e-s3882-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "a62116831aa6d956-s7926-tM-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "aaa8c7857c2e5f02-s7313-tM-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "c2a87e5970ad345d-s80949-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "cb7f5ca16e697938-s60768-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "dd30f47fda54b9d0-s46022-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "e16055dd06cff594-s37315-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   },
   "ffa6b3fb06df72a7-s55806-tL-a0": {
    "B_reaching": 0,
    "C_reaching": 0,
    "verdict": "DOES_NOT_SUPPORT"
   }
  },
  "sensitivity_literal_verdict": "REPLICATION_EVENTS_WITHOUT_PROPAGATION",
  "supporting": [],
  "verdict": "REPLICATION_EVENTS_WITHOUT_PROPAGATION"
 },
 "H3": {
  "certificates": {
   "A_easy_plus_migration": 1,
   "B_homogeneous_same_migration": 1,
   "C_easy_no_migration": 0
  },
  "n_complete": 64,
  "separation_vs_B": 0.0,
  "separation_vs_C": 0.0156,
  "verdict": "NOT_DEMONSTRATED"
 },
 "constants_sha256": "c0e488deabebd03afd398b5aa5665a1e6dbce4ddc2683385113ca4bd7b655719"
}
MACHINE-END -->

## H1 -- cue gating

Verdict **NO_DETECTED_EFFECT** over 60 complete bundles: gate main effect M = 0.0, cost interaction I = 0.0 (threshold 0.15 on final held-out competence).

## H2 -- propagation of P-11 replicators

Verdict **REPLICATION_EVENTS_WITHOUT_PROPAGATION**: 0 supporting specimen(s) across 0 distinct stratum/strata. Literal-authorship sensitivity verdict: **REPLICATION_EVENTS_WITHOUT_PROPAGATION**.

| specimen | verdict | B reaching depth 5 | C reaching depth 5 |
|---|---|---|---|
| 03650e1ad792eefa-s9040-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 08b4c94e2ea65998-s76929-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 193576337017c94a-s74845-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 2c45891544a22e46-s8700-tM-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 48c75e149fc7d62d-s12269-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 4931614d912c52b2-s1190-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 6da4c0b9a40141f8-s5058-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| 7ae3f9c1437c8000-s54765-tL-a0 | DOES_NOT_SUPPORT | 4 | 0 |
| 9cba7113df39009e-s3882-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| a62116831aa6d956-s7926-tM-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| aaa8c7857c2e5f02-s7313-tM-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| c2a87e5970ad345d-s80949-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| cb7f5ca16e697938-s60768-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| dd30f47fda54b9d0-s46022-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| e16055dd06cff594-s37315-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |
| ffa6b3fb06df72a7-s55806-tL-a0 | DOES_NOT_SUPPORT | 0 | 0 |

## H3 -- easy-niche reservoir (material ruler R3)

Verdict **NOT_DEMONSTRATED** over 64 complete bundles. Certificates A/B/C = {'A_easy_plus_migration': 1, 'B_homogeneous_same_migration': 1, 'C_easy_no_migration': 0}; separation A-B = 0.0, A-C = 0.0156.

