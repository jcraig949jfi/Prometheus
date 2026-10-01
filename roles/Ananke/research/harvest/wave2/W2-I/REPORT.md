<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-I; sha256(report)=a97b4ddb97e92fca; delimited; see REPORT.provenance.json -->
# W2-I: hop-matched topology transplants and a citation-kind auditor (Ananke Wave-2, 2026-10-01)

Worker W2-I. Directory: `roles/Ananke/research/harvest/wave2/W2-I/`.
- CPU only: CUDA_VISIBLE_DEVICES=-1, `torch.cuda.is_available()==False` is asserted, 2 threads per process.
- No git writes, no searches, no leases.
- Fresh seed namespace "W2GI" (0x57324749). Every condition uses the same 64 worlds (32 mirror pairs).
- SIGNAL means lo99 > .55, C1's threshold.

## Deliverables

**Task 1 (topology transplants)**
- Shared code:
  - `w2i_common.py`: graph variants. It swaps the neighbour table and the env distance for a run, then restores them. An identity patch reproduces native scores bit-exactly (smoke.py).
  - `transplant_hop.py MODE CID...`: one process per cell.
- Modes:
  - `main` / `lite`: the hop-matched transplants.
  - `hopscan`: native ring at 2 hops.
  - `fact` / `fact2` / `clique` / `ringlabels`: graph-variant decomposition.
- `aggregate_hop.py` writes `hop_verdicts.csv` and `hop_verdicts.json`.
- Raw per-cell outputs: `out/*.json`.
- `maj_direction_census.py` writes `out/maj_direction_census.json`.
- Proposed fix: `patches/envs_maj_inward_placement.diff`, with `patches/envs_patched.py` and `tests/test_maj_inward_placement.py`.

**Task 2 (kind auditor)**
- `kind_audit.py` writes `kind_audit.csv` (all 1411 citations) and `kind_audit_summary.json`.
- `tests/test_kind_audit.py`: 9 tests, including the requested positive fixture (fac4aaa2 "search held .5") and negative fixture (fac4aaa2 described as a transfer).
- Test run: `python -m pytest roles/Ananke/research/harvest/wave2/W2-I/tests -q` gives 11 passed, 1 xfailed (strict).

## 1. Findings

### F1 [V] At 2 hops, every transplanted law collapses to chance on its own native ring. The D-wave ".500 on a random graph" therefore needs no geometry.
Confidence: high.

- **Check:** `transplant_hop.py hopscan` on the 7 ring cells C1 transplanted, native physics, task moved to d = r+1 and 2r.
- **RELAY:** bbef66a1, 31cd2a8a, 62a7fff9 and c16d5231 all score .500 [.500] at d4 and at d6 (c16d5231 d4: .498).
- **MAJ:** 4781b0a1, 0a23398f and f6b623cd score .500 [.500] at d6, where all sensors are 2 hops away.
  - At d4 they stay SIGNAL (.65-.71), because 96 of 160 sensors are still 1 hop away.
- Same pattern elsewhere: on the clustered graph and on the Schreier graph (described in F3), 3 hops gives .500 for all 7.
- **Reading:** evolved transport crosses exactly one hop. It goes from "some signal" to "none" with nothing in between.
- **Strongest objection:** one physics point, d9cc for 4 of the 7 cells.
- **Unresolved:** whether any law in C1 relays at all. My guess is none, given W2-G F5's two marginal multi-hop cells.

### F2 [V] At matched hop count, 6 of the 7 laws C1 moved to a random graph keep SIGNAL on that same C1 graph. Two of them pass only after correcting a MAJ placement artefact.
Confidence: high.

The check is `transplant_hop.py main`. Values are acc [lo99]. The hop-matched distance is d_h = ceil(d/r) = 1.

| Cell (D-wave adjudicated) | native d0 | C1-random d0 (C1's transplant) | C1-random d_h | Verdict |
|---|---|---|---|---|
| RELAY bbef66a1 | .891 [.862] | .500 [.500] | .876 [.824] | HOP-BOUND |
| RELAY 31cd2a8a | .888 [.863] | .500 | .822 [.764] | HOP-BOUND |
| RELAY 62a7fff9 | .807 [.768] | .500 | .611 [.585] | HOP-BOUND (retains .36 of the margin) |
| RELAY c16d5231 | .840 [.796] | .500 | .878 [.829] | HOP-BOUND |
| MAJ 0a23398f | .674 [.621] | .527 | naive .521; inward .691 [.646] | HOP-BOUND |
| MAJ f6b623cd | .678 [.641] | .513 | naive .519; inward .689 [.643] | HOP-BOUND |
| MAJ 4781b0a1 | .767 [.727] | .500 | naive .500; inward .505 [.500] | TOPOLOGY-BOUND, refined to CLUSTER-BOUND (F3) |

- My C1-random d0 values reproduce C1's recorded transplant scores (.5 / .534 / .523).
- **D-wave evolve replicates (ring):**
  - RELAY: 35c721fd, 4316f167, 72dd71d8, 8c37f32e and e9196cae are HOP-BOUND (hop-matched .59-.76).
  - e06701a5 is TOPOLOGY-BOUND but weak: native .639, hop-matched .553 [.536].
  - c3d2d697 and 405e5c56 are INDETERMINATE (native not SIGNAL on fresh seeds).
  - MAJ: 18c218f5 and 1a86071f are HOP-BOUND (inward .70 / .68).
  - 8743da7f (a D replicate in 4781b0a1's condition) is CLUSTER-BOUND.
  - 15e58864, 1c12d560 and 772ae210 are INDETERMINATE (no native signal).
- **Global D cells (C1 never ran this transplant on them):**
  - HOLD 85ca202e, ab089e45, a0a5244d and 7b7b025e score 1.0 on a random graph.
  - MAJ 613162a3 keeps .751 with inward placement. Only 108 of 160 sensors are at 1 hop (the in-degree is about 3), so its verdict is INDETERMINATE (hops not matched).
- **W-I panel, extra cells:**
  - RELAY e2afff1c, ed16c553, 2dccdaa5, 78f3b0ec, a02aa099 and dcd404a9 pass at matched hops (I did not run d0 for these).
  - bf82cb29 (.504) and cd5b6fd6 (.544) fail at matched hops (F3).
  - Torus, smallworld and the other HOLD span cells: no collapse. Those tasks were already 1-hop or need no transport.
- **Overall, native-SIGNAL ring transport cells:**
  - RELAY: 15 of 18 hop-bound and 3 fail (2 cluster-bound, 1 weak).
  - MAJ: 4 of 6 hop-bound and 2 cluster-bound.
- **"Hop-bound" means the collapse to chance disappears, not that the law is unharmed.** Median RELAY retention at matched hops is about .78; the range is .36-1.8. 62a7fff9 loses most of its margin, and part of that loss is latency labels (F3).
- **Strongest objection:** post hoc; one topology seed per graph variant; 32 pairs per condition.

### F3 [V] Graph-variant decomposition: no law needs lattice offsets or ordered ports. The real dependencies are clustering, per-port latency labels and, for one HOLD law, reciprocal edges.
Confidence: medium-high. Each variant uses one graph instance.

- **The engine (part b of the task):**
  - Kp is a per-site, per-instruction immediate offset: `I_all = imm + Kp`, and WIMM writes `Kp[A mod L]`. It never indexes neighbours, so the "Kp routing indices" hypothesis has no code basis.
  - Lattice semantics can enter in two ways:
    1. Port identity. `o_rport mod R` picks which weight w[j] to adapt. On a ring, port j is the same offset at every site; on the C1 random graph it is an arbitrary neighbour.
    2. The per-port `dist` label. It sets latency `lat_base + lat_hop*dist` (and loss_per_hop). On a ring, dist = |offset| in {1,2,3}; on the C1 random graph every port has dist 1.
  - The C1 random graph is also directed (no return edges) and tree-like (clustering about .02 versus .6 on the ring).
- **Variants, all at matched hops:**
  - ring_relabel (null control);
  - ring_portshuffle: each node gets its own random port order; adjacency and distance labels are kept;
  - ring_flatdist: every port gets dist 1;
  - schreier_ringdist / schreier_flatdist: an undirected degree-6 graph with the ring's port algebra (port j is the inverse of port 5-j) and the ring's labels, but no lattice structure and clustering .02;
  - clique2x4_flatdist: every site sits in two random K4s, degree 6, clustering .41, no order and no offsets.
- **Results:**
  - **Port order never removes SIGNAL** (12 cells). The largest drop is bbef66a1, .891 to .776. Most cells retain .9 or more. Lattice offset arithmetic is at most a modest contributor.
  - **The relabel control** stays within noise of native: .880, .824, .829, .747 against .891, .807, .840, .767.
  - **CLUSTER-BOUND:** 4781b0a1, bf82cb29, cd5b6fd6, and partly 8743da7f. They fail on both tree-like graphs at 1 hop but recover on the clustered non-lattice graph.

    | Cell | Schreier (1 hop) | Clique (1 hop) | Native |
    |---|---|---|---|
    | MAJ 4781b0a1 | .512 / .517 | .725 [.680] | .767 |
    | RELAY cd5b6fd6 | .527 | .718 [.697] | .729 |
    | RELAY bf82cb29 | .500 / .508 | .598 [.579] | .667 |
    | MAJ 8743da7f | .534 | .589 [.568] | .628 |

  - **LATENCY-LABEL-BOUND:** HOLD M2 echo 4ab2ba01. It needs no transport, yet it fails on the C1 random graph (.510).
    - It is hurt by flat labels: ring_flatdist .630, schreier_flatdist .662.
    - It is restored by the ring's labels on a tree-like graph: schreier_ringdist .865 against native .887.
    - The delay line uses the ring's spread of per-offset delays (2-5 ticks). The extra loss on the C1 graph (.51 versus .66) fits the missing return edges.
  - e06701a5 (weak law) is partly label-dependent: flat .549-.558, ring labels .583.
  - 62a7fff9 also loses to flat labels (ring_flatdist .641).
- **Strongest objection:**
  - The K4 graph differs from the Schreier graph in more than clustering (more short cycles, more 2-hop paths). "Cluster-bound" is really "needs redundant short paths in the neighbourhood".
  - There is one graph instance per variant.
- **Unresolved:** a clustering dose-response (K3 vs K4 vs K6 partitions), and repeats with 3-5 topology seeds.

### F4 [V] MAJ sensors are placed by out-distance from the actuator, but the MAJ signal flows from sensor to actuator. On directed graphs, C1's MAJ graph tasks were harder than their stated d.
Confidence: high on the code and counts, medium on the consequence.

- **Code:** `envs.build` MAJ branch, `_pick_at(g, M[a], env.d, ...)`, where `M[a]` is hops a->s. RELAY, XOR and FLIP use the signal direction `M[s]`.
- **Effect on the C1 random transplant (d0=3):** for 4781b0a1, sensors land 1-4 hops upstream (4/30/88/38). At "hop-matched" d=1, still only 2 of 160 sensors are 1 hop upstream. This is why a naive hop match fails for MAJ.
- **C1 rows** (`maj_direction_census.py`, placement only, no dynamics):
  - MAJ on random graphs: on average 79% of sensors sit more than d hops upstream; some cannot reach the actuator at all (unreachable).
  - MAJ on smallworld: 37%. One-sided rewiring makes the graph directed.
  - RELAY: 0%.
  - There are 53 MAJ graph rows (35 evolve) and 0 SIGNAL among them. Example: the d=1 random rows (5edb4474, e41b7b13, 09c6dc85) have 94% of sensors at 2+ hops.
- **Proposed fix:** use `M[:, a]`. It is byte-identical on ring, torus and global (tested), so no C1 ring, torus or global row changes.
- **Consequences:**
  - W2-G F5's "MAJ one-hop" and multi-hop counts mislabel the graph MAJ rows. For example, A1 smallworld d1 row 3a2f0152 has 30% of sensors at more than 1 hop.
  - H-SCI 1.4 and PTE_CAUSAL_AUDIT ("re-picks the actuator at 3 hops") are wrong for MAJ.
- **Strongest objection:** the 0/35 MAJ graph evolve SIGNAL rows may be NULL for other reasons too. I did not re-evaluate them under correct placement.

### F5 [V] Kind audit: 1411 citations of 123 distinct C1 cells in 136 files. 47 flagged: 5 HIGH, 17 NAMING, 25 LOW.
Confidence: high on the counts, medium on recall.

- **Command:** `python kind_audit.py`, then hand review.
- **Severity rules:**
  - HIGH: search-outcome words near a non-evolve id, and the window never names the row's true kind.
  - LOW: the true kind is named in the window.
  - NAMING: an adjudicate id with only "champion" or "evolved" nearby. All 12 adjudicate genomes are bit-identical to their parents' champions (I checked), so this is a provenance hole, not an outcome misattribution.
- **Hand check of the top 15 (review order: HIGH, then NAMING):**
  - 1-4 are TRUE: H-PLANT PLAN L120 fac4aaa2 "(NULL, held .5)"; REPORT L50 ef77ef2e "FLIP NULLs ... held .507"; REPORT L59 fac4aaa2 "C1 RELAY NULL cell ... C1 search held .5"; REPORT L29 1b26026f "where C1 searched".
  - 5 is FALSE: W2-G REPORT L253 is a ledger line about the audit itself.
  - 6-15 are NAMING, and correctly so:
    - W-E REPORT L14/L26/L53 name the champions "D_<adjudicate id>" (D_67ddd858, D_223acaee, D_a8f4ea11, D_023539c4, D_feadc823, D_f7e62fe3; this is `ret_census.py` L49);
    - W-G REPORT L57/L80 (f7e62fe3);
    - sub_arc3 notes_groupA L19 (D_544f3d24).
  - Other NAMING instances: BACKLOG_V2 L14/L16 and sub_arc3 NOTES L9/L29.
- **All 25 LOW reviewed:** 24 are correct statements or corrections. One is TRUE: H-PLANT/PRINCIPAL_REVIEW L19 says the FLIP NULL evidence "covers one cell (plus ef77ef2e per the worker ...)", which still counts the transfer as a NULL. The kind word in that window belongs to the next sentence.
- **Grouped by document:**

  | Document | HIGH | NAMING | LOW | Note |
  |---|---|---|---|---|
  | H-PLANT/REPORT | 3 | 0 | 2 | |
  | H-PLANT/PLAN | 1 | 0 | 0 | |
  | H-PLANT/PRINCIPAL_REVIEW | 0 | 0 | 3 | 1 true |
  | W2-G/REPORT | 1 | 0 | 11 | |
  | W-E/REPORT | 0 | 8 | 0 | |
  | W-G/REPORT | 0 | 3 | 0 | |
  | BACKLOG_V2 | 0 | 2 | 0 | |
  | sub_arc3 NOTES and notes_groupA | 0 | 4 (2+2) | 0 | |
  | INFERENCE_HARVEST_HANDOFF | 0 | 0 | 3 | |
  | wave2/INFERENCE_LEDGER | 0 | 0 | 4 | |
  | W2-A2/REPORT | 0 | 0 | 2 | |

- **Net new beyond W2-G F4:** the PRINCIPAL_REVIEW L19 true positive, and the scale of the NAMING hole (W-E's whole retention table is keyed by adjudicate ids). No census row is misattributed.
- **Strongest objection:** recall. The tool does not see ids shorter than 8 hex, upper-case ids, or text in .py/.json files.

## 2. Proposed fixes

1. **SEMANTIC for future campaigns; erratum only for C1 (directed-graph MAJ rows would not reproduce): `patches/envs_maj_inward_placement.diff`.** It places MAJ sensors with `M[:, a]`.
   - Test: `tests/test_maj_inward_placement.py`.
   - On current code the check fails (6/160 sensors 1 hop upstream). It is marked xfail(strict).
   - On the patched copy it passes (146/160).
   - On a ring the patch gives byte-identical schedules.
2. **NEUTRAL wording, C1_REPORT F2:**
   > "F2 Transport is one hop, not lattice-bound. The D-wave topology->random transplant kept env d, which on a random graph means BFS hops: the 1-hop RELAY task became a 3-hop task, and MAJ sensors were placed by out-distance from the actuator, mostly 2-4 hops upstream. On their own ring the same laws fall to exactly .500 at two hops (RELAY 4/4, MAJ 3/3), so the transplant's .500 measures hop count. At matched hops on the same random graph (W2-I, post hoc, 32 fresh pairs), 6 of 7 laws keep SIGNAL (RELAY .61-.88; MAJ .69 with upstream placement), often with reduced margin. One integration law (MAJ 4781b0a1, and its D replicate) fails at matched hops on tree-like graphs but recovers on a clustered non-lattice graph (.73): it needs clustered neighbourhoods, not lattice offsets. No law needs ordered ports (a per-node port shuffle never removes SIGNAL). Opening: multi-hop relays; transfer tests with hop count and clustering matched."
3. **NEUTRAL wording, C1_REPORT s1 (L20) and the L4 ladder:**
   - "topology-bound (...)" becomes "one-hop (every law collapses to .500 at two hops, on its own ring or a random graph; at one hop on a random graph 6 of 7 keep SIGNAL)".
   - "topology transfer NO" becomes "topology transfer yes at matched hops (6/7), no at 2+ hops".
4. **NEUTRAL wording, PTE_ENGINE_CARD** ("Transfer across size ... and topology (they are topology-bound)"):
   > "Transfer across topology works when hop count is matched; every evolved law fails at two hops even on its own ring; a minority need clustered neighbourhoods (MAJ 4781b0a1, RELAY bf82cb29/cd5b6fd6) or the ring's per-port delays (HOLD M2 4ab2ba01). Size: one law, one-hop at every N."
5. **NEUTRAL, documentation:**
   - annotate H-PLANT REPORT L29/L50/L59, PLAN L120 and PRINCIPAL_REVIEW L19 (transfers);
   - add an id map "D_<adj id> = champion of <parent id>" to W-E/REPORT and BACKLOG_V2.
6. **NEUTRAL, tooling:** run `kind_audit.py` before deposits. Treat HIGH as blocking and NAMING as a warning.

## 3. Disagreements

- **W2-G F1 and its proposed wording** ("The collapse measures hop count, not lattice geometry"):
  - Confirmed for the 4 RELAY D cells and generalised.
  - But it is incomplete for MAJ: a naive d=1 still fails because of the placement direction (F4).
  - And it is false for 3 of 18 RELAY panel cells and for 4781b0a1, 8743da7f and HOLD M2. Those need clustering or latency labels (F3).
  - Its follow-up question "does any law need lattice offsets?" gets the answer no, from the port-shuffle runs.
- **H-SCI 1.4** ("collapse to 0.500 (7/7)"): C1 recorded MAJ .534 and .523, not .500. MAJ was never "3 hops" in the RELAY sense.
- **PTE_CAUSAL_AUDIT** ("re-picks the actuator at 3 hops"): wrong mechanism for MAJ (sensors are placed by out-distance).
- **W2-G F5:** MAJ smallworld and random rows are not at their nominal hop count. The one-hop / multi-hop split for MAJ graph rows is mislabelled.
- **C1_REPORT F2's "routing to specific offsets":** unsupported. Port order is irrelevant to collapse, and dest_mode "all" MAJ laws use no routing at all.

## 4. Next questions (ranked)

1. Can any evolved law cross 2 hops? Every one tested is exactly .500 at 2 hops. Run a multi-hop RELAY search at d9cc (H-PLANT 5.2, needs authorization), with plant relay_flood as the positive control.
2. Clustering dose-response for the cluster-bound cells. Use K3/K4/K6 partition graphs and 3-5 topology seeds each. Does retention track the clustering coefficient or the number of 2-hop paths?
3. Re-evaluate the 35 MAJ graph evolve champions (all NULL) under inward placement (patched copy). How many become SIGNAL? This decides whether the MAJ graph NULLs were partly an env artefact.
4. Partial retention at matched hops (62a7fff9 .36; RELAY median about .78). Run flatdist and schreier_ringdist on all hop-bound cells to split latency labels from in-degree and saturation.
5. HOLD M2 4ab2ba01: separate reciprocity from labels. Use the C1 random graph plus reverse edges, with and without ring labels.
6. Extend the kind auditor to ids under 8 hex, upper-case ids and .py/.json text; wire it into the deposit step.
7. Repeat F1/F2 at a second physics point (N=100 dest_mode all reached only MAJ). Is "one hop" a property of d9cc or of C1 search in general?

## 5. Inference ledger

```
Q: is the D-wave random-graph collapse hop count? | hopscan native ring d=r+1,2r; C1-random d_h | yes: native 2-hop = .500 (7/7); 6/7 keep SIGNAL at matched hops | high | post hoc, 1 seed/graph, 32 pairs | why some lose margin | NQ4
Q: why does naive hop-matching fail for MAJ? | envs.build MAJ uses M[a] (out-dist); signal hops measured | placement artefact; inward placement restores .69 | high | - | C1 MAJ graph NULLs | NQ3
Q: do laws need lattice offsets / ordered ports? | engine.py routing/Kp read; ring_portshuffle on 12 cells | no; port order never removes SIGNAL; Kp is not a routing index | high | one shuffle seed | - | -
Q: what does 4781b0a1 need? | inward C1-random, Schreier (tree-like, ring port algebra), K4-clique graph | clustered neighbourhood (.51 tree-like vs .73 clique) | medium-high | clique differs in cycles/paths too | dose-response | NQ2
Q: what does HOLD M2 4ab2ba01 need? | flatdist, Schreier flat/ringdist, clique | ring per-port delays (+ return edges) | medium-high | one graph instance | reciprocity split | NQ5
Q: W-I panel and D replicates | main/lite modes, 41 cells | RELAY 15/18 hop-bound, 2 cluster-bound, 1 weak; MAJ 4/6 hop-bound, 2 cluster-bound | medium-high | d0 not run for 8 lite cells | - | NQ7
Q: MAJ graph placement across C1 | maj_direction_census.py | random 79%, smallworld 37% of sensors beyond nominal d; RELAY 0% | high | placement only | effect on NULLs | NQ3
Q: transfers/adjudicates cited as search outcomes | kind_audit.py + hand check | 5 true misattributions (4 H-PLANT + PRINCIPAL_REVIEW L19); 17 NAMING (W-E D_<adj id>) | high precision | recall <8 hex/.py | tooling | NQ6
```

## 6. Compute used

| Item | CPU time |
|---|---|
| Smoke test | 121 s |
| Transplant runs, all modes, 41 cells (per-cell processes; each under 70 s wall) | 1731 s |
| MAJ placement census | about 15 s |
| Tests and kind audit | about 20 s |
| **Total** | **about 1890 CPU-s, about 0.52 core-h** (cap 0.75) |

CPU only, 2 threads per process, no GPU, no searches, no leases.
