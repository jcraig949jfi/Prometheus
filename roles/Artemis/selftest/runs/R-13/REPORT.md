# REPORT -- can another node recompute the ecology's headline numbers from Git alone?

Host: ubu002 (Linux, 4 cores, Python 3.14.4, NumPy 2.3.5). Repository snapshot: origin/main @ 6ff2b2f8a
(2026-09-28 08:59 -0400) plus seat branches as named below. Scratch: /home/jcraig/artemis-selftest/work/R-13
(scripts/, out/, src/). No repository writes, no M2 access, no canonical-store queries, and no sealed holdout was
used. Plain ASCII.

## 1. WHAT I SET OUT TO TEST

The question was whether the evidence behind each active engine's headline result can be reached, and checked, by a
node other than the one that produced it. "Reached" here means in Git on main, in Git on a seat branch, or only on
the producing host. The package gave a census of 12 engine results and a pre-stated rule. I would pick ONE headline
number per row, as the engine's own report states it, and try to rebuild that number on this node from committed
material only, using my own read-only code. Each row gets one grade: RECOMPUTED, FILES-ONLY (the files exist but the
number cannot be rebuilt), or HOST-ONLY. The decision rule was fixed in advance. If 8 or more of 12 are RECOMPUTED,
evidence reachability is a narrow problem confined to the big Z80 campaigns. If 5 or fewer are, evidence packs plus a
reachability field should become a program-wide standard. For the host-only cases I also had to name the smallest
committed artifact that would let any node verify the claim. A second step was an M2-side hash attestation for the
one open link in the existing single-run verification pack.

## 2. WHAT I DID

I graded strictly. RECOMPUTED means one of two things:
- (R) re-executed from code and inputs in Git, with the output matched to a committed or attested hash; or
- (D) rebuilt by my own code from per-unit records committed in Git (per seed, per run or per birth), and not
  copied from an aggregate.

A number that exists in Git only as an aggregate is FILES-ONLY. A number that has no committed outcome is HOST-ONLY.

Scripts are in scripts/ (common.py reads blobs with `git show`). Their outputs are in out/.

| row | headline number chosen (report @ ref) | script | method |
|---|---|---|---|
| BEE multi-day (running) | none exists yet; prereg MULTIDAY_PREREG.md @ origin/bellerophon/multiday-campaign-2026-09-26 (ee7a7d954) | -- | inspected branch: prereg, code, pilot cost receipts only |
| BEE coupling | ECHO K40 de novo competent self-replicator 29/150 ON vs 6/150 OFF/YOKED/SHUFFLED (COUPLING_CAMPAIGN_REPORT.md s2 @ main) | r_bee_coupling.py | recount from COUPLING_ORIGIN_LEDGER.jsonl per-run rows |
| Z80xAtlas 72h campaign | verified de novo spontaneous replication = 0 of 101,003 DONE runs; 26 flagged runs = transplants (Z80ATLAS_POSTCAMPAIGN_ADJUDICATION @ main) | r_z80atlas.py | recount from replays/REPLAY_flagged.json; hash-check of committed campaign top files |
| causal lens B6 (r038751) | W_by_location=NO & W_by_material=YES = 27,083 (out_v02/B6_PROBE_r038751.json @ main) | r_b6.py + replay | git archive of harness 16fc6c2a, traced VM 98a28dd39, probe + pack @ main; full replay (65 s), pack verify, my own re-implementation of the table |
| Archaeon deep block | its strongest-finding #1: environmental blocking, genetic establishments U 24 vs BAND0 5, 12+/2- blocks, p = 0.0065 (A0_ARCHAEON_LENS.md -> archaeon/envgate2/VERDICT_2026-09-26.md @ main) | r_envgate2.py | recount of the 39 per-establishment records + my own sign test |
| NPE W1 C-STATELESS-FFA6 | DENSE 11/33 vs STATELESS 34/42, one-sided Fisher p = 3.27e-5 (VERDICT.json) | r_npe.py | 96 per-seed JSONs; L2 and depth>=20 rule; my own hypergeometric |
| PTE (E-002) | 4/16 GA crossovers are self-crosses; 10 of 15 "decided" reversible by inert flips; 0/16 beat the operator null (ops/campaigns/C-001/E-002/RESULT.md @ main) | r_pte.py | 16 per-crossover rows in out/T-009_ga.json |
| Aether AETH-03 block | rcv_add P_sust 0.172 (22/128), NEW_BEHAVIOUR under N1 (PHYSICS_DESIGN_03 s5.2; E-006 RESULT @ main) | r_aether.py + 4 unit runs | components from committed E-003 per-seed files; rcv_add re-executed, 4 seeds x 32 origins, code @ c49f2ebad (flight commit) |
| Aphrodite A17 | E1 BOUNDED_RSI = NO (0/8 replicates select a semantically new schema); catalog A per-stratum admissions (A16 campaign report 2026-09-26 @ origin/aphrodite/* only) | r_aphrodite.py | 416 foundry evaluations; 16 donor-adjudication traces, with the selection rule re-applied |
| Ares cycle 2 | Gate A: c2_no_recur 10/10 at cap; collapse on cut: plasticity 7/10, keep 3/10, recurrence 0/10; median time 20 gens (ARES_CYCLE2_REPORT.md @ main) | r_ares.py | 10 per-seed dissect JSONs |
| Cosmos C3 | the only public C3 result, gate v3 PASS: 6 planted systems x 5 seeds all classified as expected (S1_PREREG_P1P2_GATE.md @ main). The C3 science is withheld under seal, so I did not score it. | r_cosmos.py | re-applied the prereg decision rule (p1 <= 0.02; P2 effect > 3 SE; indeterminate bands) to 60 rows |
| Herakles HC-T01 | same-probe history effect H = +2.28, +0.60, +0.51, +0.52 at gens 300/1000/2000/3000; "24 to 108 times noise"; 12/12 pairs both at the optimum (HC_T01_CORRECTION @ main) | r_herakles.py (+ the seat's analyze.py) | per-run CSVs in derived/grid and derived/sens_long |

Commands:
- Replay: `python3 -I tools/codeprov_replay.py r038751 out.json --config r038751.config.json --harness harness`, then
  `tools/th006_pack.py verify --pack pack.json --pack-sha256 212844af... --replay out.json --published published.json`
  (in src/b6).
- Aether units: `python3 observatory/aeth03_unit.py --law rcv_add --seed-index {0,1,2,3} --arm off --out ...`
  (in src/aether/Aether), at most 2 in parallel.
- Everything else is read-only `git show` plus python3.

## 3. RESULT

| # | row | where the evidence is | grade |
|---|---|---|---|
| 1 | BEE multi-day | prereg/code/pilots on a seat branch only; all outcomes on M2 | HOST-ONLY (no committed outcome) |
| 2 | BEE coupling | report, ledgers, RESULTS on main; results.jsonl on M2 (sha256 in report s6) | RECOMPUTED(D) for the numerators; denominators FILES-ONLY |
| 3 | Z80xAtlas campaign | adjudication, 26 replays, top files on main; RUNS.jsonl (157.7 MB) + 14.1 GB tree on M2 | FILES-ONLY (sub-claim recomputed) |
| 4 | B6 27,083 | code, config, pack on main; attestation on main | RECOMPUTED(R) |
| 5 | deep block / ENVGATE-02 | RESULTS.json per-establishment records on main; block files on M2 (manifest-hashed) | RECOMPUTED(D) |
| 6 | NPE ffa6 | 96 per-seed JSONs, now on main as well as the seat branch | RECOMPUTED(D) |
| 7 | PTE E-002 | per-crossover rows on main | RECOMPUTED(D) |
| 8 | Aether rcv_add | code + E-003 component files on main; 72 E-006 unit files on M2 | RECOMPUTED(R) |
| 9 | Aphrodite A17 | per-draw and per-replicate JSON on 4 aphrodite/* seat branches, NOT on main | RECOMPUTED(D), branch-only |
| 10 | Ares c2 | per-seed dissects on main | RECOMPUTED(D) |
| 11 | Cosmos C3 gate | per-row gate records on main | RECOMPUTED(D) (C3 science withheld, not scored) |
| 12 | Herakles HC-T01 | per-run CSVs on main | RECOMPUTED(D) |

Numbers:
- **B6.** Replay on ubu002 took 65.3 s wall, 144 MB RSS. result_sha256 = cd9547c2..., which equals the recipe. The
  pack verify returned PASS on all 4 checks. My own re-implementation of the rules gives:

  | cell | count |
  |---|---|
  | NO/YES | 27,083 |
  | NO/NI | 1,059 |
  | NO/NO | 21 |
  | YES/YES | 44,279 |
  | NI/NI | 2,336 |
  | NI/YES | 22 |

  The row content is 8,118,119 bytes, sha256 95a12c29.... That equals the hash M2 attested for the preserved log
  (roles/Odysseus/th006/attest/M2_r038751_2026-09-28.txt, commit f525de9ef, status MATCH). The package's step 2 was
  already done before this run. The trust chain is now closed end to end: a Git-only replay on a third node
  reproduces bytes that are identical to the M2 preserved log.
- **Aether.** The re-executed rcv_add seeds give 5/32, 7/32, 6/32 and 4/32, i.e. 0.156 / 0.219 / 0.188 / 0.125.
  Pooled that is 22/128 = 0.1719, exactly the report's per-seed figures and REDUCTION.json. The components, from
  committed E-003 files, are rcv 6/128 = 0.047 and add 1/128 = 0.008. N1 holds (0.172 >= 0.10, >= 2 x 0.047,
  > 0.055).
  - Seed 0's result_sha256 08929d70... is byte-identical to the committed BUCKKEEP (Windows, NumPy 2.4.3) unit. That
    extends cross-host determinism to a Linux node with NumPy 2.3.5.
  - For seeds 1-3 the pod's result hashes are not in Git (the manifest records artifact-file hashes only), so those
    matched on the science numbers, not on hashes.
- **Z80xAtlas.** 26/26 flagged replays were admitted, and the legacy label was reproduced 26/26. Repaired spontaneous
  replication is 0/26, inserted-lineage 26/26, random founders 0. CAMPAIGN_DONE.json (runs 101003), PACKET.json,
  CAMPAIGN_PACKET.md, GRAMMAR_FROZEN.json and STATUS.json in Git are byte-identical to the evidence-bundle hashes.
  However, "0 of 101,003" also asserts that no other run was flagged. That part needs RUNS.jsonl, which is on M2
  only.
- **BEE coupling.** The origin ledger has 47 unique ECHO K40 runs: ON 29, OFF 6, YOKED 6, SHUFFLED 6. This matches
  the report. The denominators (150 per arm), the comp_final p = 3.5e-6 and P1-P6 exist only as aggregates.
  Side observation: 13 of the 47 rows (5 of the 6 YOKED rows) carry arch.self_copy = false on the recorded tape.
  This is a question for the seat, not a finding. The competence test may be dynamic, with the tape recorded as a
  representative.
- **Other RECOMPUTED rows.** Every one matched exactly:
  - NPE: 11/33 vs 34/42, p = 3.2684e-5.
  - Ares:
    - 10/10 at cap;
    - classes PLAST 6 / KEEP 2 / REDUNDANT 1 / MIXED 1;
    - collapse on cut: plasticity 7, keep 3, recurrence 0;
    - median time 20.
  - PTE: 4 self-crosses (n_differing = 0); 10 of 15 reversible; 0/16 below p 0.05.
  - ENVGATE-02: 24 vs 5, 12+/2-, p = 0.00647; all 39 from random inflow.
  - Aphrodite:
    - catalog A admissions per stratum: add 4/20, fdiv 1/32, gcd 2/32, sub 4/28, 0 for the rest;
    - donor selections INHERITED 16/16, re-derived from the selection tables 16/16;
    - G1 NEW = [].
  - Cosmos: all 6 systems 5/5; 0 of 60 rows where my class differs.
  - Herakles:

    | generation | H |
    |---|---|
    | 300 | +2.281 |
    | 1000 | +0.604 |
    | 2000 | +0.513 |
    | 3000 | +0.516 |

    This is 24.2 to 107.8 times the md noise floor, with 12/12 pairs both at the optimum at 2000 and 3000.
- **One label ambiguity (Aphrodite).** Catalog B add shows 5 accepted candidates against the report's "4/22". The
  engine caps admissions at K = 4 per stratum, so the report's "accepted" means admitted rather than qualifying.
  This is not a defect.

Count: strictly 9/12 RECOMPUTED. Including the BEE coupling numerators it is 10/12. There is 1 FILES-ONLY (Z80xAtlas)
and 1 HOST-ONLY (the running multi-day campaign). By the pre-stated rule (>= 8/12) the reading is: **headline-level
evidence reachability is a narrow problem.** It sits exactly where the package predicted, in the big Z80 campaign
bodies (BEE coupling denominators, BEE multi-day, Z80xAtlas RUNS.jsonl). It is not program-wide.

Smallest committed artifact that would make each host-only case verifiable (sizes are estimates; I could not see the
files):
- **Z80xAtlas.** The scorer (scheduler.family_table @ c7610ea19) reads only status, family, run_id, spec_id,
  scheduler_reason, factor_vector.task and signals. The artifact would be:
  - a pack in the existing single-run-pack style: content sha256 of RUNS.jsonl (already committed as 3afa36b7...)
    plus chunk hashes;
  - a per-run projection {run_id, family, status, reason, task, flags, flag_score}, about 101k rows, roughly
    1 MB gzipped;
  - one M2 attestation that the projection derives from the hashed file.

  Together with the 26 committed replays, that verifies "0 of 101,003".
- **BEE coupling.** A per-run projection of results.jsonl (sha 23b55f78... already committed): run, lane, cell, K,
  arm, seed and the frozen analysis's outcome fields. That is 11,657 rows, roughly 0.1-0.2 MB gzipped. It would let
  any node rerun the frozen coupling_analysis.py and rebuild P1-P6 and all lane tables, not only the positive-run
  numerators. It also needs an M2 attestation.
- **BEE multi-day.** Decide now, before it ends: md_analysis.py is frozen, so have the close-out emit and commit the
  same kind of projection of exactly the fields md_analysis.py reads, plus the results file's hash.
- **Aether (already verifiable).** Record result_sha256, not just the artifact-file sha256, per unit in
  units_manifest.json. A re-execution on another host can then be matched by hash rather than by summary numbers.

## 4. DID IT RESOLVE THE QUESTION

Partly, leaning yes. The census step resolved cleanly: the pre-stated threshold is met (9-10 of 12). The
attestation step had already been completed by another seat, and I confirmed it from the other side, from a replay
on a third node.

Four limits keep this from being a full yes:

1. **The headline choice is mine.**
   - For the deep block I scored Archaeon's own strongest finding, not the synthesis's BEE-derived numbers. The
     synthesis says those rest on M2.
   - For Cosmos, the C3 science is sealed/withheld, so I scored its public gate.

   A different pick on those two rows could move the count to 8/12. That is still at the threshold.
2. **Most RECOMPUTED rows are (D), rebuilt from committed per-unit records, not re-executed.** Only B6 and Aether were
   regenerated from code. Two (D) rows, ENVGATE-02 and the BEE numerators, list positives only. Completeness of those
   positive lists, meaning that no other unit was positive, still rests on host files. The files are manifest-hashed,
   but the hashes are not checkable here.
3. **I did not check whether the M2 paths still exist or match their hashes.** That requires M2.
4. **The package's census was partly stale.** It had already moved toward reachability:
   - NPE, Aether, the deep block, the coupling report and the Z80xAtlas post-campaign files are now on main;
   - the attestation is done.

   The branch-only risk now applies to Aphrodite A17 (4 seat branches, not main) and to the BEE multi-day branch.

## 5. CONSEQUENCES

- **Reproduction of known work, now extended (for Odysseus and ops):**
  - The single-run verification pack works on a second node (ubu002; the pack's author used ubu001).
  - Its one open trust link is closed: Git-only replay content sha256 = the M2-attested preserved log, MATCH.
- **New positive result (Aether, Archaeon/ops):** the Aether rcv_add NEW_BEHAVIOUR verdict re-executes from Git alone
  on a Linux node. That took about 39 CPU-min, and seed 0 is hash-identical across Windows and Linux. The engine's
  design (deterministic portable units, LF-normalised code hashes, a result hash that excludes host fields) is what
  made a lost-artifact situation harmless. Other engines should copy that design.
- **Narrow gap confirmed (Bellerophon, Archaeon, Atlas):** only the big Z80 campaigns lack a verifiable path. The fix
  is projection packs with M2 attestation for Z80xAtlas RUNS.jsonl, BEE coupling results.jsonl and, before it ends,
  BEE multi-day. A program-wide standard is not warranted by this evidence. A cheap reachability column in the Atlas
  registry (main / branch / host + committed-hash yes/no) would still keep this census current.
- **Harness gap, small (Aether/platform):** units_manifest.json records artifact-file hashes, not result hashes, so a
  cross-host re-execution can only be matched on science numbers. Adding result_sha256 per unit is a one-line change.
- **Quieter risk (operator):** some evidence is committed only on unmerged seat branches (Aphrodite A17, BEE
  multi-day). There is still no merge policy.
- **Questions for seats, not defects:**
  - Bellerophon: why do 13/47 ECHO K40 "de novo competent self-replicator" ledger rows (5/6 YOKED) show
    self_copy = false and, for 9 of them, no copy op on the recorded tape?
  - Aphrodite: the report's "accepted/evaluated" means capped admissions (K = 4), not qualifying candidates. Label it.
- **No engine or instrument defect was found** in any recomputed number. All 11 non-host-only rows matched their
  reports exactly where they were checkable.

## 6. COST

- Agent time: about 2 h.
- CPU time: about 41 CPU-min in total, all on ubu002 CPU with at most 2 worker processes and under 150 MB RSS:
  - B6 replay: 64 s;
  - Aether units: 542 + 569 + 619 + 613 s;
  - Herakles analysis: 3 s;
  - everything else was seconds.
- Not done, and why:
  - No existence or hash checks of M2 paths: this needs M2.
  - No re-execution of Aphrodite E1 (8 replicates, about 265 s on 8 workers on M4), the ENVGATE-02 blocks, the Cosmos
    gate, or any BEE coupling runs: budget, and their numbers were already rebuildable from records.
  - Did not read the sealed/withheld Cosmos C3 branch.
  - Did not verify the static-architecture question on the BEE tapes (it would need the BEE VM run on 47 tapes;
    feasible, but out of scope).
