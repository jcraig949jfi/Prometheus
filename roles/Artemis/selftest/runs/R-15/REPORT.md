REPORT -- label-free scoring of a self-organised memory index (R-15)

1. WHAT I SET OUT TO TEST
An earlier program experiment (the D-10 phase-2 capacity gate in
SerendipityFoundry/D10phase2) showed that task-conditional relevance in its
StackVM program corpus is large (69% of relevance variance is artifact x task
interaction) but cannot be keyed from program syntax. It left open two things:
(a) whether an index keyed on behaviour (what stored programs DO when run),
built by the system from its own execution history with no human labels, can
find the relevant memories for a new task cheaply; and (b) whether such an
index can be scored by a criterion the system produces itself, one that
predicts its operational value, instead of by external labels. I tested both
offline on the committed relevance data. Operational value here means how much
of the conditional-retrieval headroom a budgeted retrieval captures. The
label-free criteria were self-retrieval on held-out history and compression
(description length) of held-out history observations.

2. WHAT I DID
Data (read-only, repo HEAD ca189b020; the files were added in d332658cf):
  SerendipityFoundry/D10phase2/phase2/relevance_dev.npy  (4110 corpus
    programs x 24 DEV tasks; entry = fraction of the task's 10 TRAIN cases the
    program solves exactly, i.e. what running it on the query's own train
    evidence reveals)
  SerendipityFoundry/D10phase2/phase2/dataset.json (corpus bytes, provenance,
    task families).
  I did not touch the held-out GATE tasks.
Code (all in /home/jcraig/artemis-selftest/work/R-15): index_study.py,
lf_mdl2.py, controls.py, correlate.py. Outputs: results_v1.json,
results_lf2.json, results_controls.json, results_correlation.json, *.log.
Data was exported with git archive into src/.
Protocol. Each DEV task in turn is the query. The other tasks are the
system's "history": either all 23 (LOTO) or only the 21 from other task
families (LOFO, so no sibling tasks). Indices are built from history only:
  behaviour-k : k-means (k = 8..128) on each program's vector of history
                relevance (its execution record), label-free
  syntax-k    : k-means on opcode histogram + log length (the family D-10 retired)
  random-k    : random partition
  run         : buckets by which history search produced the program
  flat_random : no index, execute M random programs
  flat_histbest: execute the M programs with the best mean history relevance
Retrieval has an execution budget M (each program run on the query costs 1).
The index version runs one medoid per cluster, then spends the rest of the
budget inside clusters in order of how well their medoid scored. It returns
the top 4 programs executed. The score is D-10's own capture metric,
(top-4 relevance - global-best top-4) / (oracle top-4 - global-best top-4),
averaged over 24 queries x 8 index seeds. One query has oracle = global, so
its capture is undefined and paired tests use n=23.
Controls for behaviour-32 (controls.py): flat_alive, which samples only
programs that were ever non-zero in history (tests "it just skips dead
code"); beh_noquery, which keeps the same medoids but walks clusters in random
order; beh_repsonly_r, which uses the medoids and then uniform samples. Paired
sign-flip permutation test across queries at M=64.
Label-free scores, computed with no access to the query. History is split
into build and held-out halves, the index is built on the build half, and:
  LF_self      = the same retrieval's capture on held-out history tasks
  LF_dm_gain   = bits/entry saved coding held-out history columns given the
                 partition (adaptive Dirichlet-multinomial code, so the
                 parameter cost is included; 11 levels, and a binary
                 "useful >= 0.5" version)
  pooled_mdl   = a naive two-part code that predicts held-out columns from each
                 cluster's build-column value distribution
Spearman rank correlation over the 13 index variants between each LF score and
operational capture at M = 64 / 128 / 400.

3. RESULT
Capture of the conditional headroom (LOFO; LOTO within +-0.03):
  budget M                 32     64    128    256    400
  behaviour-32           0.60   0.79   0.84   0.84   0.85
  behaviour-128          0.29   0.73   0.87   0.93   0.93
  syntax-32              0.00   0.32   0.42   0.50   0.65
  run (provenance)       0.41   0.53   0.61   0.71   0.75
  random-16 partition    0.05   0.26   0.49   0.67   0.73
  flat_random            0.02   0.22   0.49   0.68   0.71
  flat_histbest          0.11   0.13   0.17   0.24   0.24
  (full scan of all 4110 = 1.00 by definition; D-10's syntax-only keys: -0.13
   to +0.03)
Controls at M=64, behaviour-32 minus control, paired over 23 queries (LOFO):
  vs flat_random +0.57 (16 wins / 3 losses, p<1e-4); vs flat_alive +0.48
  (16/2, p<1e-4); vs beh_noquery +0.34 (20/1, p<1e-4); vs beh_repsonly_r +0.24
  (16/2, p=5e-5). LOTO is the same to within 0.02.
  The gain therefore comes mostly from the query-conditioned expansion, not
  from avoiding dead programs or from diversity alone.
Label-free vs operational (Spearman over 13 variants, LOFO; LOTO similar):
  LF_self    : 0.98 (M=64), 0.80 (M=128), 0.62 (M=400)
  LF_dm_gain : 0.76, 0.57, 0.39. Positive (0.40-0.46 bits/entry) only for
               behaviour indices. Syntax, random and provenance partitions get
               zero or negative gain, correctly marking them as useless.
  pooled_mdl : -0.82, -0.81, -0.60. Anti-correlated: it rewards the useless
               partitions.
  Within the behaviour k-sweep, only LF_self tracks the best k at small
  budgets (0.9-1.0 at M=64). Compression gain does not pick k (0.1-0.2 at
  M>=128).
Plain conclusion: on this corpus, a label-free index keyed on the programs' own
execution record reaches about 79% of the conditional-oracle headroom while
running 64 of 4110 programs. Flat random sampling at the same cost gets 22%, a
syntax index 32%. The result holds with sibling tasks removed from history.
Compressing held-out history under the partition is a usable label-free
criterion for "is this partition about function at all" (rank 0.76), but it
is weak at tuning the index. A naive per-cluster MDL is inversely related to
usefulness. Self-retrieval on held-out history is the strongest label-free
score, but it is close to the operational metric by construction.

4. DID IT RESOLVE THE QUESTION
Partly. Yes on the narrow form. Once execution is allowed, an endogenous,
behaviour-keyed memory index does key task-conditional relevance on the D-10
corpus, which supports the "syntax cannot reach function; execution is the
bridge" diagnosis. A system-generated criterion (compression gain or
self-retrieval on its own history) does separate functional from
non-functional organisations. It is not resolved in these ways:
(i) The operational measure is the train-case relevance proxy, not the
downstream held-out solve rate. The StackVM interpreter (foundry/engines/gp/
stackvm) is not committed in any branch, so I could not run acquisition
downstream, run programs on fresh probe inputs, or run the full execution-
bridge gate.
(ii) History and queries come from one task generator, and there are only
24 tasks.
(iii) Building the index costs one execution per program per history task
(about 86k runs), which is amortised and not charged against M.
(iv) "Which memories are the same" was settled here by choosing to partition
on execution outcomes. The data show this choice matters a lot (syntax and
provenance partitions fail), but I did not search the space of possible
equivalence relations.

5. CONSEQUENCES
- New positive result, offline: an execution-keyed, self-organised index beats
  random, provenance, syntax and past-utility baselines at equal execution
  budget. The D-10 owners (Daedalus / SerendipityFoundry) and the Aporia
  thread on endogenous memory geometry should know that the untried
  "execution bridge" option looks strongly viable. Its real gate test is
  blocked only by a missing artifact.
- Instrument/archive defect: the D10phase2 archive cannot be re-run from the
  repository because the Foundry StackVM source is not committed. Anyone who
  wants to reproduce or extend D-10 (Daedalus, Ensorain) needs it committed or
  pinned.
- Methodological warning for anyone scoring memory with MDL (Ensorain's null
  ladder, Cosmos): a naive per-cluster code fitted across different tasks
  ranks useless partitions best (rho about -0.8). Use within-observation
  adaptive codes. Even those only say whether a partition is functional; they
  do not tune it.
- flat_histbest (retrieve past winners) is nearly worthless here (0.13 at
  M=64). This reconfirms D-10's finding that relevance is mostly conditional.

6. COST
About 1.5 h of my time. About 35 CPU-minutes in total: main study 24 min
user, the rest a few minutes each; at most 2 processes at once; under 1 GB
RAM. No GPU, no gate data, no database access. Not done: downstream solve-rate
arms, fresh-probe behavioural signatures and the frozen gate run. All three
need the uncommitted StackVM interpreter.
