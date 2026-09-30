# Cosmos GRAVEYARD (killed laws are scientific output)

Currency: 2026-09-29 (T-I1 backfill from the C0/C1/C2 stores). Machine-checked. Each entry:
`### <id> | <campaign> | <law id(s)>` then keys law, campaign, killed_by, evidence, fragments. `killed_by`
names the TRANSFORMATION or TEST that killed the law. If it has not yet been recovered, it starts with
UNRECOVERED and the checker counts it. Nothing is ever deleted from this file.

Source of the backfill (read-only, M2): C:/Users/James/cosmos_runs/<store>/store/cwe.sqlite (law_events)
and <store>/adversary.json (per-round attack tallies). Stores: c0_main_run2_f31339054 (C0), c1_run2 (C1),
c2_7b14ec99e (C2; c2_RERUN has the same events). Attack classes (prometheus/cosmos/adversary.py):
errorseek (worlds the law is confidently wrong about), extreme (lattice corners), coordpres /
coordpres_base (microscopically different worlds with IDENTICAL declared coordinates), band
(calibration only, never a kill). "Confirmed" = the contradiction replicated on 2 fresh replicates.
Location (locate.py) = mean offset of the true boundary from the law's, in log2 cost, per family,
tolerance 0.10.

### G-0001 | C0 | 424fa143b7 v1
- law: ((N - K) * C) <= -0.1584 AND (C - exp(-(C * N))) <= -0.136   (cmap v1)
- campaign: C0
- killed_by: ADVERSARY round 0 -- 17/108 confirmed counterexamples (15.7%). By class: errorseek 9, coordpres 5, extreme 2, coordpres_base 1. By family: ca 7, ring 7, regs 3.
- evidence: c0_main_run2_f31339054 law_events + adversary.json[0]
- fragments: 6 of 17 kills came from coordinate-preserving pairs, so the v1 coordinates themselves were incomplete (C0 later added capacity / repair coordinates). The second atom has the C - f(N) shape that survivors share.

### G-0002 | C0 | d45d1069e0 v2
- law: ((C + K) * C) >= 0.1647 AND (C - (G * exp(-N))) <= -0.06142   (cmap v1)
- campaign: C0
- killed_by: ADVERSARY round 1 -- 11/108 confirmed (10.2%). errorseek 8, extreme 2, coordpres 1. ALL 11 in family ca (regs 0, ring 0).
- evidence: c0_main_run2_f31339054 law_events + adversary.json[1]
- fragments: the ceiling atom C - G exp(-N) <= t, which survives in law B. The kill is one-family (ca), so this is a candidate "restrict, not kill" case under the four-layer rule. In C0 it was killed outright (the rule then was global).

### G-0003 | C0 | 964c086e6d v3
- law: (C * K) >= 0.1608 AND (C - (G * exp(-N))) <= -0.08702   (cmap v2)
- campaign: C0
- killed_by: ADVERSARY round 2 -- 25/108 confirmed (23.1%). errorseek 15, coordpres 6, extreme 3, coordpres_base 1. ca 13, ring 12, regs 0.
- evidence: c0_main_run2_f31339054 law_events + adversary.json[2]
- fragments: the ceiling atom again. The cmap change v1 -> v2 made the kill rate WORSE (10.2% -> 23.1%), so the v2 coordinates were a regression on ring.

### G-0004 | C1 | eec9c5a571 / 9ed4a83871 / 78d3bd6297 (v1-v3 of the C1 lineage)
- law: v1 (Q - (C * K)) <= 0.872 AND (K / (N + log(C))) <= -0.6075; v2 (K / (N + log(C))) <= -0.5829 AND ((C * log(C)) + Q) <= 0.9112; v3 same form as v2, thresholds -0.5903 / 0.9105   (cmap v4)
- campaign: C1
- killed_by: BOTH adversary AND location, each round. Counterexamples 4/107, 2/106, 4/108 (errorseek mostly; ca/ring). Location offsets far outside tolerance: v1 regs -0.495, ring -0.554, ca -0.543 (SE ~0.05-0.08); v2/v3 ring -0.43/-0.53, ca -0.37/-0.38 (regs INDETERMINATE).
- evidence: c1_run2 law_events + adversary.json[0..2]
- fragments: the K / (N + log C) atom never appears in a survivor. These kills are ROBUST. Artemis R-05 (worker claim, consistent with these tallies) reports that the 2-4% contradiction rates also fail at tolerance 0.20 (6-9 SE), so the 0.10 bar did not decide them.

### G-0005 | C2 | c5cd50beb1 v1
- law: (C - (G * exp(-N))) <= -0.1026 AND ((C * K) + exp(-Q)) >= 0.5122   (cmap v4)
- campaign: C2
- killed_by: LOCATION only, one family. 0/106 confirmed counterexamples. regs offset -0.168 (SE 0.067); ca and ring LOCATION_OK (-0.018 each). The offset exceeds the 0.10 tolerance by (0.168 - 0.10) / 0.067 = 1.01 SE.
- evidence: c2_7b14ec99e (and c2_RERUN, identical events) law_events + adversary.json[0]
- fragments: a MARGINAL kill. The 1.01-SE excess decided which law became law B: the successor a079ad5ec1 had regs -0.015 (SE 0.014). The ceiling atom survived unchanged in law B (t -0.1026 -> -0.102); only the second atom changed. This is a tolerance-sensitivity scar: under tolerance 0.15, G-0005 would not have died.

### G-0006 | C3 | C3 preliminary law (Session 1; text withheld until the withheld branch is published)
- law: WITHHELD (hash-committed through the withheld branch head 0ecafed1..., FREEZES F-0000)
- campaign: C3
- killed_by: PRE-RESULT COORDINATE AUDIT, verdict REJECT from 2 independent native replicas (2026-09-29, research/reviews/COORD_AUDIT_C3_2026-09-29.md), with the checkable claims EXECUTED by Cosmos: the coordinates restate the certificate's P1/P2 definition (a zero-parameter certificate rule reproduces 104/120 visible classes, and every miss is a noise-limited boundary case) or fingerprint the substrate family. Killed BEFORE holdout D2 was spent.
- evidence: research/reviews/COORD_AUDIT_C3_2026-09-29.md; local VERIFY.json sha256 c294f24788ccfe04...; replica outputs e2d43755..., 6349aa10...
- fragments: the only admitted coordinate is a task covariate (the delay). The structural lesson recurs from C0 (R-0001/2): coordinates built from the certificate's own construction re-derive the certificate. Any successor needs representation-invariant, family-balanced quantities AND a preregistered requirement to beat the zero-parameter definition rung. The reviewers warn that invariance pushes such quantities back onto the P1/P2 rung, which is an open tension, recorded for T-A1/T-E1.
- disposition: 2026-09-30 operator: C3 CLOSED / KILLED BEFORE HOLDOUT. Preserve as a scientific scar. Do not revive, re-tune or reinterpret the REJECT as an invitation to repair. D2 was never spent. Autopsy: research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md (public) and the local branch cosmos/c3-autopsy-2026-09-30 (withheld).

## Cross-entry note (a pattern, not yet a claim)
The atom C - G exp(-N) <= t appears in 3 FAILED laws (G-0002, G-0003, G-0005) and in SURVIVED law B.
Law A carries the related C - (G + exp(-N)) instead. There is an explanation that makes this
uninformative. The zero-parameter economy written from the certificate definition ("PAYS iff
G e^-N - C >= .10 AND (Q<1 OR CK/2 >= .10)", c0e/PREREG.md) CONTAINS this atom. So its recurrence is
what one expects if the grammar keeps rediscovering the certificate's own economics. Artemis R-14
(worker claim; Cosmos has not re-run it) reports that the analytic formula scores 0.960 BA on the c2
pool vs laws A .964 and B .978, and is statistically indistinguishable from them on all three spent
sealed universes. That matches Cosmos's own record (HANDOFF s1 V2: 97.5% agreement with the
hand-derived law). T-I1's base-rate test must therefore use the ANALYTIC formula's atoms as the null,
not random atoms.

## T-I1 fragment test result (2026-09-29, v3 at d2ede5652; exploratory, Z1)
On the 720 spent sealed rows, 11 of 15 atoms of the C0-C2 laws re-express the zero-parameter definition
rung beyond a rate-matched, rung-equivalent-excluded grammar null (analysis/t_i1_fragments_v3.json). That
includes every instance of the ceiling atom. Atoms that do NOT: G-0001b (C - exp(-CN)), G-0004b (K/(N + log C)),
G-0004c (C log C + Q), and law B's log(Q - C K). So the atoms that died robustly (G-0004) were the non-certificate
ones, and the survivors are almost entirely the certificate. The graveyard's recurring fragment is the
planted economics, not a found invariant.
