# Aether follow-up ranking (CWO 2026-09-30, Aether CURRENT)

Authority: operator CWO 2026-09-30 (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md, blob ab93f646..., verbatim record
roles/Aporia/prompts/2026-09-30_cwo_fleet_activation/), which supplements MWO-0004. The broker dependency (CURRENT) is
blocked on Odysseus (#917), so under CWO s5 the seat ranks and promotes NEXT.

State of the line: rcv_add and rcv_str are super-additive and replicated (E-006, E-009). The horizon is characterised
(E-008). The E-006 cause probe gave the mechanisms: rcv_add = persistence of activity traces; rcv_str = activity
re-routing activity via ENERGY-STEERED AIM. Those mechanism statements are observational (post hoc probe); no
intervention has tested them.

Criteria (CWO s3): 1 falsifiability, 2 expected information gain, 3 ability to distinguish causal mechanisms,
4 compute cost, 5 reusable infrastructure. The CWO asks to prefer controlled interventions over observation.

| rank | candidate | 1 | 2 | 3 | 4 cost | 5 | why this rank |
|---|---|---|---|---|---|---|---|
| **1** | **rcv_str steering lesion**: new law `rcv_sfx` = rcv_str with its energy term (energy>>6) replaced by a static per-site pseudo-random offset in 0..3. Aim distribution is kept; coupling to energy dynamics is cut. Same assay and N1 rule, E-009 seeds 4-7, paired with the existing rcv_str units. | high: a stated prediction either way | high | **direct**: it tests the cause probe's mechanism claim by intervention | ~4 units, <1 CPU-h | the lesion-variant pattern is reusable | the only candidate that turns an observational mechanism claim into an interventional one, at trivial cost |
| 2 | rcv_add trace lesion: rcv_add with add's persisted trace made unreadable by the relay (or decayed each tick) | high | high | direct, for rcv_add | ~4 units | as above | same logic; needs a clean definition of "the trace" in add's code first, so it follows #1 |
| 3 | value-provenance detector (E-P1 failed: the XOR content signature is blind to transport in a rich soup) | medium | high, long-term | enables content-transport questions at all | engineering, little compute | **high**: fixes a known instrument limit for every law | infrastructure, not an experiment; the best Builder-lane item |
| 4 | AETH-01 arbitration finite-run diagnostic (D-AETH01-08; Artemis #1002 Q9) | high | low-medium | no (substrate check) | small | medium | a real open falsifier, but no current claim depends on it (twin assays share arbitration) |
| 5 | energy-regime robustness of rcv_add/rcv_str (one alternative regime) | medium | medium | no (generality, not mechanism) | ~20 units + parameter plumbing | low | observational generality; the CWO asks for interventions first |
| 6 | TH-009 frozen-medium (a law whose dynamics rewrite the medium) | medium | high but diffuse | no | large (new law class) | medium | a new research programme, not a bounded follow-up |

NEXT = rank 1. It needs no promexec: it is the same deterministic unit runner, on Fabric or R3 native. The CWO's
"after the broker path is cleared" is satisfied by s5, which promotes NEXT when CURRENT is blocked; the broker stays
in BLOCKED. Rank 1 will be preregistered as E-010 (hypothesis, prediction, decision rule, code pin and a regression
check that existing laws are unchanged) and pushed before any run.
RESERVE = ranks 2 and 3, plus AGE/Builder friction per the CWO (DEF-AETH-001 is already routed; nothing else is
open).
