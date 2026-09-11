# Techne — H0–H5 backlog

Schema: `roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md`. One line per item, in
priority order. The first five are the ones I start next.

Every row names the artifact that proves it done. Blocked rows stay on the list with the blocker
named, and every XL row names the decision the operator has to make — so the operator's queue is
the union of the seats' XL rows.

```
TECHNE-01 | DONE 2026-09-11 at 3c98ff775: stitch ran on H1/H0 phase 2's real solved programs | H1 | 1.0 | S | none (CLEARED 2026-09-11 -- Archaeon exported the solved programs on main at 9e9210893, sha256:581aed31; the blocker text naming a B1 read path was stale) | receipt: 17 solutions, 17/17 expansion-correct, and the finding is that EVERY abstraction has arity 0 -- a compression dictionary over a 2-4 node program space, not an instrument library
TECHNE-02 | DONE 2026-09-11 at 2baf0680f: h3_compare_policies re-run on Archaeon's v1 equal-mass descriptors | H3 | beta | S | none (CLEARED -- H3_DESCRIPTORS_v1 is on main) | receipt: occupancy 8/16 -> 15/16 and the random arm spread from 4 cells to 15; finding it exposed that my seam honoured v0's edges only because they were equal-width BY COINCIDENCE (erratum filed, fixed by pre-binning)
TECHNE-03 | Qualify pyribs CVTArchive as the H3 beta comparator against the same frozen stream | H3 | beta | M | none | an ADAPTER_QUALIFICATION receipt with retained-id agreement vs GridArchive on cs-c3-2 and the declared centroid seeding
TECHNE-04 | Qualify pyribs SlidingBoundariesArchive and state what moving boundaries do to replay determinism | H3 | beta | M | none | a receipt showing whether two replays of one frozen stream retain the same ids, and a refusal if they do not
TECHNE-05 | Write the licence/notice pack: one directory per tool with the notice, its sha256, the SPDX claim and its evidence grade | TOOLS | 1.0 | S | none | techne/acquisition/NOTICE_PACK/ plus a test that every installed distribution has a notice file or a recorded UNRESOLVED
TECHNE-06 | Send the stitch_bindings licensing question upstream and record the thread | TOOLS | 1.0 | S | operator decision D-17 (whether this seat may open an upstream issue in the programme's name) | a committed record of the request and any reply, beside LICENSE_EVIDENCE.json
TECHNE-07 | Add a lock-refresh command that re-resolves every pinned distribution and DIFFS against the committed lock without installing | TOOLS | 1.0 | S | none | techne/scripts/lock_refresh.py plus a committed diff report showing zero drift on the current five locks
TECHNE-08 | Declare and implement the tool-retirement rule for pins that drift | TOOLS | 1.0 | M | none | techne/acquisition/RETIREMENT_RULE.md plus a test that a pin whose upstream artifact digest changed is refused rather than silently re-resolved
TECHNE-09 | Run reconcile_packet on the operator's two JSONs and close or re-state DEV-T1 and DEV-T2 per entry | TOOLS | 1.0 | S | operator (prometheus-tool-acquisition-plan.json and prometheus-h0-h5-backlog.json are on no machine here) | techne/acquisition/PACKET_RECONCILIATION.json with a verdict per repository and the capacity conflicts named
TECHNE-10 | Measure the isolated-environment refresh cadence by re-resolving monthly and recording observed upstream drift | TOOLS | 1.1 | M | none | a drift log with at least three dated samples and a recommended cadence derived from them, not chosen
TECHNE-11 | Qualify z3 as an oracle for 4-input Boolean and state where exhaustive parity stops being affordable | H1 | 1.1 | M | none | a receipt with the parity count at n=4 (65,536 functions) and the measured wall clock, plus the n at which I stop and why
TECHNE-12 | DONE 2026-09-11: hypothesis qualified as a minimiser over structured H1 PROGRAMS | H1 | 1.1 | M | none (CLEARED -- Proteus's strategy and predicate are on main at 5eae54618) | receipt adapter_qualification-hypothesis-20260911T065703Z: SOUND on 45/45 scored, NOT MINIMAL on 24 of 45 (0.5333), max excess 4 nodes. PREDICATE SUBSTITUTED with the reason recorded: this row asked for still_a_counterexample, and Proteus measured that predicate trivial (every one of the 256 targets has a size-1 counterexample), so qualifying on it would have measured nothing -- still_solves is the non-trivial predicate
TECHNE-13 | DONE BY VIVARIUM 2026-09-11: the bounded external-backend contract exists, v1.1 on main at b45016944 | ENGINE | 1.0 | L | none (CLEARED -- and the ruling inside it is that at 1.0 a scientific kind may NOT call an external executable, so stitch stays a preparation-time tool) | the contract document, plus my F15 passing at N=5 and the thread arm invariant 1..16; the REST of my side is TECHNE-43 and is not this row
TECHNE-14 | Export the stitch abstractions as a typed library artifact an admitted interpreter can validate, from the MIT route only | H0 | 1.1 | M | none (UNBLOCKED 2026-09-11: TECHNE-13 landed, and Vivarium confirmed by running the real interface checker that boolean-components-v1 ACCEPTS arity-0 components -- closed subexpressions used as extra LEAVES, which is the whole mechanism, so my arity-0 result is the derived library H0 beta wants rather than a consolation prize) | a declarative export -- one named abstraction per component, its expression as nested JSON in Proteus's grammar, published as component_library/boolean-components-v1 -- with expansion verified by the independent expander and a test that no pickle crosses the boundary. Whether a derived library HELPS is the experiment, not this row: Vivarium's hand-built library solved maj3 and LOST xor3 at the same op cap, netting zero
TECHNE-15 | Build the DreamCoder smoke environment in WSL2 (docker image on python 3.7 + opam 4.06.1+flambda) and run one bounded domain smoke run | H0 | 1.1 | M | none | a smoke-run receipt from inside WSL, or a new obstruction measured there; the Linux-host blocker is GONE -- WSL2 Ubuntu 24.04.4 is installed and running, docker is present inside it, and opam is one apt away (candidate 2.1.5-1)
TECHNE-16 | Resolve DreamCoder's licensing or record it permanently unresolved | H0 | 1.1 | S | operator (its only notice is the AngularJS MIT text, "Copyright (c) 2010-2020 Google LLC") | an entry in LICENSE_EVIDENCE.json with either a grant or a permanent UNRESOLVED and the consequence for export
TECHNE-17 | PARKED to 2026-12-11: acquire POET only when H4 reaches 1.1 | H4 | 1.1 | S | H4 is at SCAFFOLD and POET is an H4 1.1 reference arm BY DESIGN (Harmonia ruling 2026-09-11); 1.1 is three gates away | the acquisition command's REFUSAL is the artifact until then; reopen on H4 1.0 closing. STALE CLAUSE STRUCK: H4-ADAPTIVE-1.0.0 has existed since dd38720c0 -- my blocker text was wrong while its outcome was right
TECHNE-18 | Distinguish original POET from Enhanced POET and pin the intended algorithm branch before any comparison | H4 | 1.1 | M | TECHNE-17 | a manifest entry naming the branch, its commit, and the reference experiment selected
TECHNE-19 | Add a RSS hard cap via a Windows job object and replace the sampled-only observation | TOOLS | 1.1 | M | none | a budget receipt whose rss_enforcement says ENFORCED with a test that an over-ceiling child is killed
TECHNE-20 | Measure whether mahler_measure_batch earns its tier, with the population stated | TOOLS | program | M | none | a profile over a narrow-degree corpus AND the 8,625-entry corpus, with a promote-or-retire recommendation; today's number is 0.99x on the wide corpus
TECHNE-21 | Split the three test_mahler_batch tests into a slow marker so techne/tests gives a fast regression signal | TOOLS | 1.0 | S | none | a committed pytest marker plus the measured suite time with and without it (today: 849 s total, 811 s in three tests)
TECHNE-22 | Qualify z3's UNKNOWN-by-incompleteness with a case that actually fires, or record the negative result as final for this build | H1 | 1.1 | S | none | either a fixture where reason_unknown is neither timeout nor rlimit, or a committed statement that six candidates failed to elicit one on z3 5.0.0
TECHNE-23 | Add a seam test that fires W1 and W2 in the FAILING direction on a malformed Archaeon record | H3 | 1.0 | S | none | two tests that refuse a carried digest of the wrong shape and a result_ref whose declared bytes disagree with the resolver
TECHNE-24 | DONE 2026-09-11 at a8e52d45a: cs-c3-2 replayed through the sealed future-query manifest, scored and NOT ranked | H3 | 1.0 | M | none (CLEARED -- manifest digest de4cae9b, recorded before anything was scored) | receipt: my adapter matches behavioral on all 12 queries, and 2 of the 9 scorable queries are unattainable by ANY policy (stable-ge-4's 0.85 threshold exceeds the corpus max 0.8125; cell-pc0-c3 is empty in all 150 rows), so the discriminating set is 7 and the tallies must be read against 7. The 3 transfer queries are UNSCORABLE by the manifest's own instruction
TECHNE-25 | Re-verify the tie policy against every pyribs archive class, not just GridArchive | H3 | beta | S | none | a verify_tie_policy result per archive class, with a raise if any class differs from FIRST_WRITER_WINS
TECHNE-26 | Add the Rust toolchain to the environment lock so a second machine can reproduce the stitch build | TOOLS | 1.0 | S | none | a committed toolchain lock with rustc/cargo versions and the gnu target, plus the WinLibs GCC requirement recorded as a host precondition
TECHNE-27 | Record the stitch build's own reproducibility: build twice and compare the binary digest | TOOLS | 1.1 | S | none | two sha256 values for compress.exe and a statement of whether the build is bit-reproducible here
TECHNE-28 | Qualify a cost model for the external stitch process so producer receipts can charge it | ENGINE | 1.0 | M | none | a resource vector per compress invocation with enforcement_class per dimension; FALSE BLOCKER CLEARED -- archaeon/producer/costs.py is on main with Resource(resource, quantity, unit, method, enforcement_class, scope) and CostEvent fully specified and validated, so nothing is owed by Archaeon here
TECHNE-29 | Audit every committed receipt for stage honesty: no receipt claiming a stage it did not test | TOOLS | 1.0 | S | none | a test over techne/acquisition/receipts/ extending the existing one to every stage, not only LOCAL_SCIENTIFIC_BENEFIT
TECHNE-30 | Write the arsenal capability matrix for the six H0-H5 tools with qualification stage per consumer | TOOLS | 1.0 | S | none | a committed matrix derived FROM the receipts rather than hand-maintained, plus the script that derives it
TECHNE-31 | CLOSED 2026-09-11 as "none known": no roadmap SDP lives at 1e10 conditioning, so no MOSEK spend is justified | TOOLS | program | S | none | Harmonia's ruling -- theta(G) n=25-35 is well conditioned (spread O(n), 6-9 orders from 1e10) and already measured solved; kissing numbers d=5..10 is a MEMORY problem at 0.5 ABSOLUTE tolerance, and MOSEK does not shrink an 8 GB block; Cohn-Elkies is an LP. REQ-029 closes with it
TECHNE-32 | Check whether any affiliation opens the Simons Foundation route to Magma before anything is paid | TOOLS | program | S | operator (eligibility is a fact about the programme, not about the tool) | a committed yes/no with the evidence, closing or opening the three Magma-dependent roadmap gaps
TECHNE-33 | Pin pip itself in the isolated environments so the lock's installer is not inherited | TOOLS | 1.1 | S | none | a receipt whose isolated_env.pip_pinned is true, replacing today's explicit false
TECHNE-34 | Verify every committed lock still installs from hashes on a clean environment | TOOLS | 1.0 | M | none | a from-scratch install receipt per lock with --require-hashes and the wall clock
TECHNE-35 | State the retirement disposition for the gnullvm Rust target, installed and unused | TOOLS | 1.1 | S | none | either its removal with the footprint delta measured, or a recorded reason to keep it
TECHNE-36 | Add a check that the engine still deserializes no upstream object graph, run on every tool acquisition | ENGINE | 1.0 | S | none | the existing test wired into the acquisition path so a new tool cannot land without it passing
TECHNE-37 | Put every paywalled or absent roadmap tool behind a capability-gap fixture, so a purchase or a build is authorised by a failing fixture and never by a roadmap row | TOOLS | 1.0 | M | none | one gap fixture per Tier-7 target in techne/scripts/capability_gap_fixture.py with a committed result per target, starting from the SDP one already landed
TECHNE-38 | Submit the ill-conditioned SDP fixture for adversarial review before it is quoted as evidence about any solver | TOOLS | 1.0 | S | Harmonia or Elenchus (review) | a review verdict on whether C_illcond_1e10 is a solver failure or a badly posed instance; both free solvers return DIFFERENT wrong answers on a problem with a certified-feasible point
TECHNE-39 | Wrap arbitrary-precision SDP (SDPA-GMP) as the certificate path no double-precision solver provides at any price | TOOLS | 1.1 | L | TECHNE-38 | a pm.optimization entry point solving the theta(C_5) anchor to a declared precision beyond double, with its GPL obligation recorded
TECHNE-40 | Measure the Clarabel/SCS crossover and route solve_sdp by problem shape rather than by a fixed default | TOOLS | 1.1 | M | none | a committed crossover curve (measured: Clarabel 19.3 s vs SCS 2.7 s at n=120, Clarabel more accurate below) and a dispatch rule derived from it
TECHNE-41 | Record the rational-rounding route from a numerical SDP solution to an exact certificate, or record why it does not apply to our problems | TOOLS | program | M | TECHNE-39 | either a worked exact certificate for one roadmap problem, or a committed statement of which step fails
TECHNE-42 | Re-verify every blocked row's BLOCKER TEXT against main before reporting it, and record the check | TOOLS | 1.0 | S | none | a dated verification line per blocked row; THREE of mine were stale on 2026-09-11 alone (28 costs.py already on main, 01 misattributed to Proteus, 17 naming a protocol that existed since 09-08) -- the defect is that I write blocker text once and never re-check it
TECHNE-43 | Write the stitch backend's section-1 DECLARATION and the EIGHT required boundary fixtures | ENGINE | 1.0 | M | none | a declaration with exact keys and no defaults (binary_sha256 re-checked before each launch, argv_template + argv_from_payload allowlist, env allowlist, mounts with modes, pinned RNG/threads, output schema, limits; container: null as a declared value) plus F1 F6 F7 F8 F13 F14 F15 F15b passing. F15 is done at N=5 and the thread arm is invariant 1..16. F15b was added by Vivarium on 2026-09-11 because my own cmd finding cuts both ways: an over-broad projection makes F15 pass VACUOUSLY, so F15b varies one declared argv_from_payload parameter and requires the projection to CHANGE -- F15 says the backend is repeatable, F15b says the thing compared is still the backend
TECHNE-44 | Replace taskkill /T with a Windows job object in the budget wrapper, or declare the preparation-job scope it is adequate for | TOOLS | 1.1 | M | none | either a job-object kill with Vivarium's probe_process_tree_kill.py passing on this host, or a recorded statement that taskkill /T is best-effort by documentation and therefore adequate only for a metered preparation job and never for an admitted in-run backend
```

## Notes on the ordering

**01, 02, 12, 13 and 24 are DONE as of 2026-09-11**, and four of the five were done by another
seat landing one artifact -- Archaeon's solved-program export and descriptor declaration and sealed
manifest, Proteus's strategy and predicate, Vivarium's contract. That is the pattern worth naming:
the rows I called blocked were each one handoff from cheap, and the handoffs arrived within a day of
being asked for. **03-05 and 14 and 43 are next; none of them needs anybody.**

**There are now ZERO XL rows, and that is a change rather than a tidy-up.** Both operator
decisions I filed this morning dissolved under measurement:

- **TECHNE-15 (DreamCoder)** was "is a Linux host worth it?". The host already exists -- **WSL2
  Ubuntu 24.04.4 is installed and running** on this machine, `docker` is present inside it, `gcc`
  and `make` are there, and `opam` is one `apt install` away (candidate 2.1.5-1). There is no
  hardware decision; there is an M-sized build. It drops to a normal row. Worth separating too:
  BLK-DC-4 (199 cloud-launcher commands) blocks reproducing THEIR experiments, not a smoke run.
- **TECHNE-31 (MOSEK)** was "buy at $4,300, or close REQ-029?". `GAP_FIXTURE_SDP.json` answers the
  half that was missing: the free path is fine on the authority anchor (Clarabel to 1.8e-9 on
  theta(C_5)), fine to n=120, and fails in exactly **one** regime -- 1e10 spectral spread, where
  both solvers return *different wrong answers* on a problem with a certified-feasible point. The
  question is no longer "buy?" but "does any roadmap SDP live at 1e10 conditioning?", which is a
  fact Aporia and Harmonia hold. It drops to S.

**COUNTS, RE-VERIFIED 2026-09-11 against main rather than recalled** (this is TECHNE-42 applied to
this file, and it caught two stale numbers of my own): **44 rows, 23 S / 19 M / 2 L / zero XL, and 9
blocked -- not the "17 of the 41" this paragraph said.** Six blockers dissolved the same day: 01, 02,
24 (Archaeon, commit 9e9210893), 12 (Proteus, 5eae54618), 13 (Vivarium, b45016944) and 31 (Harmonia
closed REQ-029 as "none known"). Of the 9 that remain, three are chains behind a single root
(18 behind 17; 39 and 41 behind 38), so there are **six independent blockers**, and four are
operator-held -- each needing an action or a fact rather than a judgement, which is why all four are
S and none is XL: TECHNE-06 (may this seat open an upstream issue in the programme's name), TECHNE-09
(paste the two packet JSONs), TECHNE-16 (DreamCoder's licensing), TECHNE-32 (Simons eligibility for
Magma).

**A count written once and never re-checked is the same defect as a blocker written once and never
re-checked.** I have now made that error in both directions in this file -- first 3 XL / 11 blocked
when it was 2 XL / 15, now 17 of 41 when it is 9 of 44. The rule I am holding myself to: the counts
paragraph is regenerated by counting the fence, never edited by hand.

**The mechanism, not the three one-offs.** TECHNE-37 is the row that matters most for a roadmap with
paywalled items on it: every such item goes behind a capability-gap fixture, and a purchase or a
build is authorised by a *failing fixture*, never by the existence of a roadmap row. Today's SDP
fixture is the first, and it turned a $4,300 decision into a question for two other seats.

**Where building beats buying, stated once.** TECHNE-39 exists because the regime our mathematics
most needs -- a *verifiable certificate* rather than a fast double -- is one no commercial
double-precision solver serves at any price. MOSEK is float64. There, arbitrary precision
(SDPA-GMP, GPL, $0) is not the cheap substitute for MOSEK; it is the only thing that answers the
question, and buying would have been the wrong move even with the money.

**The roadmap's premise was also stale.** It treated SCS as the free path. CLARABEL -- an
interior-point solver, the same algorithm class as MOSEK, Apache-2.0 -- has been installed and
unmeasured the whole time. Part of closing a gap is checking whether it is still there.

**What I am deliberately not proposing.** No item here widens a tool's use beyond a named consumer,
and none acquires anything that lacks one -- POET stays at TECHNE-17, behind Harmonia, with its
licence and cost already settled so that price can never be the reason it waits.
