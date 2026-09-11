# Techne — H0–H5 backlog

Schema: `roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md`. One line per item, in
priority order. The first five are the ones I start next.

Every row names the artifact that proves it done. Blocked rows stay on the list with the blocker
named, and every XL row names the decision the operator has to make — so the operator's queue is
the union of the seats' XL rows.

```
TECHNE-01 | Run the stitch extraction route on H1/H0 phase 2's solved programs and report whether they share structure | H1 | 1.0 | S | the B1 read path, or an export from Archaeon/Vivarium (the programs exist only as engine observations; H1H0_PHASE2_READOUT carries solved true/false, not the programs) | a receipt with n_abstractions on the real solved programs: 3 DISTINCT TASKS solved, 14 solved cells, so up to 14 programs whose syntactic overlap is unknown until read
TECHNE-02 | Re-run h3_compare_policies on a descriptor pair that separates the acquisition arm, once Archaeon declares one | H3 | beta | S | Archaeon (descriptor declaration; my measurement says all 120 random rules fall in 4 of 16 cells) | a second H3 receipt with the cell-occupancy table under the new descriptors, beside the 8-of-16 table from today
TECHNE-03 | Qualify pyribs CVTArchive as the H3 beta comparator against the same frozen stream | H3 | beta | M | none | an ADAPTER_QUALIFICATION receipt with retained-id agreement vs GridArchive on cs-c3-2 and the declared centroid seeding
TECHNE-04 | Qualify pyribs SlidingBoundariesArchive and state what moving boundaries do to replay determinism | H3 | beta | M | none | a receipt showing whether two replays of one frozen stream retain the same ids, and a refusal if they do not
TECHNE-05 | Write the licence/notice pack: one directory per tool with the notice, its sha256, the SPDX claim and its evidence grade | TOOLS | 1.0 | S | none | techne/acquisition/NOTICE_PACK/ plus a test that every installed distribution has a notice file or a recorded UNRESOLVED
TECHNE-06 | Send the stitch_bindings licensing question upstream and record the thread | TOOLS | 1.0 | S | operator decision D-17 (whether this seat may open an upstream issue in the programme's name) | a committed record of the request and any reply, beside LICENSE_EVIDENCE.json
TECHNE-07 | Add a lock-refresh command that re-resolves every pinned distribution and DIFFS against the committed lock without installing | TOOLS | 1.0 | S | none | techne/scripts/lock_refresh.py plus a committed diff report showing zero drift on the current five locks
TECHNE-08 | Declare and implement the tool-retirement rule for pins that drift | TOOLS | 1.0 | M | none | techne/acquisition/RETIREMENT_RULE.md plus a test that a pin whose upstream artifact digest changed is refused rather than silently re-resolved
TECHNE-09 | Run reconcile_packet on the operator's two JSONs and close or re-state DEV-T1 and DEV-T2 per entry | TOOLS | 1.0 | S | operator (prometheus-tool-acquisition-plan.json and prometheus-h0-h5-backlog.json are on no machine here) | techne/acquisition/PACKET_RECONCILIATION.json with a verdict per repository and the capacity conflicts named
TECHNE-10 | Measure the isolated-environment refresh cadence by re-resolving monthly and recording observed upstream drift | TOOLS | 1.1 | M | none | a drift log with at least three dated samples and a recommended cadence derived from them, not chosen
TECHNE-11 | Qualify z3 as an oracle for 4-input Boolean and state where exhaustive parity stops being affordable | H1 | 1.1 | M | none | a receipt with the parity count at n=4 (65,536 functions) and the measured wall clock, plus the n at which I stop and why
TECHNE-12 | Extend the hypothesis minimiser qualification to structured H1 PROGRAMS rather than assignments | H1 | 1.1 | M | Proteus (a program-space strategy and its validity predicate) | a receipt where every shrunk program is still a counterexample under Proteus's evaluator, with a negative control
TECHNE-13 | Build the bounded external-backend contract for the stitch Rust binary: process-tree cancellation, lease renewal, limits, repeatability, output validation | ENGINE | 1.0 | L | Vivarium (the contract's shape is theirs; the design makes it a prerequisite for any kind calling an external executable) | a Vivarium-admitted contract document plus my adapter passing its boundary-failure fixtures
TECHNE-14 | Export the stitch abstractions as a typed library artifact an admitted interpreter can validate, from the MIT route only | H0 | 1.1 | M | TECHNE-13 | a declarative export with a typed AST per abstraction, its expansion verified by the independent expander, and a test that no pickle crosses the boundary
TECHNE-15 | Build the DreamCoder smoke environment in WSL2 (docker image on python 3.7 + opam 4.06.1+flambda) and run one bounded domain smoke run | H0 | 1.1 | M | none | a smoke-run receipt from inside WSL, or a new obstruction measured there; the Linux-host blocker is GONE -- WSL2 Ubuntu 24.04.4 is installed and running, docker is present inside it, and opam is one apt away (candidate 2.1.5-1)
TECHNE-16 | Resolve DreamCoder's licensing or record it permanently unresolved | H0 | 1.1 | S | operator (its only notice is the AngularJS MIT text, "Copyright (c) 2010-2020 Google LLC") | an entry in LICENSE_EVIDENCE.json with either a grant or a permanent UNRESOLVED and the consequence for export
TECHNE-17 | Acquire POET at its pinned revision once a consumer names it | H4 | 1.1 | S | Harmonia (H4's adaptive protocol does not exist, so POET has no named consumer; licence and cost are settled: Apache-2.0, $0) | an INSTALLATION receipt, and until then the tool's own refusal is the artifact
TECHNE-18 | Distinguish original POET from Enhanced POET and pin the intended algorithm branch before any comparison | H4 | 1.1 | M | TECHNE-17 | a manifest entry naming the branch, its commit, and the reference experiment selected
TECHNE-19 | Add a RSS hard cap via a Windows job object and replace the sampled-only observation | TOOLS | 1.1 | M | none | a budget receipt whose rss_enforcement says ENFORCED with a test that an over-ceiling child is killed
TECHNE-20 | Measure whether mahler_measure_batch earns its tier, with the population stated | TOOLS | program | M | none | a profile over a narrow-degree corpus AND the 8,625-entry corpus, with a promote-or-retire recommendation; today's number is 0.99x on the wide corpus
TECHNE-21 | Split the three test_mahler_batch tests into a slow marker so techne/tests gives a fast regression signal | TOOLS | 1.0 | S | none | a committed pytest marker plus the measured suite time with and without it (today: 849 s total, 811 s in three tests)
TECHNE-22 | Qualify z3's UNKNOWN-by-incompleteness with a case that actually fires, or record the negative result as final for this build | H1 | 1.1 | S | none | either a fixture where reason_unknown is neither timeout nor rlimit, or a committed statement that six candidates failed to elicit one on z3 5.0.0
TECHNE-23 | Add a seam test that fires W1 and W2 in the FAILING direction on a malformed Archaeon record | H3 | 1.0 | S | none | two tests that refuse a carried digest of the wrong shape and a result_ref whose declared bytes disagree with the resolver
TECHNE-24 | Replay cs-c3-2 through Archaeon's sealed future-query manifest once it exists and report per-policy scores without interpreting them | H3 | 1.0 | M | Archaeon (the sealed future-query manifest) | a receipt with the four policies' scores and an explicit refusal to rank them
TECHNE-25 | Re-verify the tie policy against every pyribs archive class, not just GridArchive | H3 | beta | S | none | a verify_tie_policy result per archive class, with a raise if any class differs from FIRST_WRITER_WINS
TECHNE-26 | Add the Rust toolchain to the environment lock so a second machine can reproduce the stitch build | TOOLS | 1.0 | S | none | a committed toolchain lock with rustc/cargo versions and the gnu target, plus the WinLibs GCC requirement recorded as a host precondition
TECHNE-27 | Record the stitch build's own reproducibility: build twice and compare the binary digest | TOOLS | 1.1 | S | none | two sha256 values for compress.exe and a statement of whether the build is bit-reproducible here
TECHNE-28 | Qualify a cost model for the external stitch process so producer receipts can charge it | ENGINE | 1.0 | M | none | a resource vector per compress invocation with enforcement_class per dimension; FALSE BLOCKER CLEARED -- archaeon/producer/costs.py is on main with Resource(resource, quantity, unit, method, enforcement_class, scope) and CostEvent fully specified and validated, so nothing is owed by Archaeon here
TECHNE-29 | Audit every committed receipt for stage honesty: no receipt claiming a stage it did not test | TOOLS | 1.0 | S | none | a test over techne/acquisition/receipts/ extending the existing one to every stage, not only LOCAL_SCIENTIFIC_BENEFIT
TECHNE-30 | Write the arsenal capability matrix for the six H0-H5 tools with qualification stage per consumer | TOOLS | 1.0 | S | none | a committed matrix derived FROM the receipts rather than hand-maintained, plus the script that derives it
TECHNE-31 | State whether any roadmap SDP actually lives in the one regime where the free path fails, before any MOSEK spend | TOOLS | program | S | Aporia/Harmonia (which roadmap problems are SDPs, and at what conditioning) | a committed list of roadmap SDPs with their conditioning, against GAP_FIXTURE_SDP.json which found a candidate gap ONLY at 1e10 spectral spread
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
```

## Notes on the ordering

**01-05 are today's next.** 01 and 02 are blocked on one artifact each from another seat and are
cheap the moment those land -- 01 needs three expressions, 02 needs a descriptor declaration, and
both of my measurements today are what make them worth doing. 03-05 need nobody.

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

**17 of the 41 rows are blocked**, each naming its blocker. Four remain operator-blocked but are S
rather than XL, because each needs an action or a fact rather than a judgement: TECHNE-06 (may this
seat open an upstream issue in the programme's name), TECHNE-09 (paste the two packet JSONs),
TECHNE-16 (DreamCoder's licensing), TECHNE-32 (Simons eligibility for Magma).

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
