REPORT -- state injection as a representation-vs-mechanism splitter: where to apply it next

1. WHAT I SET OUT TO TEST

When an evolved organism fails a task, is it because the state the task needs never gets
into the organism (a percept, parse or stored value is missing), or because the organism
has no machinery that would use that state? Hand-filling state at a chosen depth and
re-scoring gives an upper bound that is meant to separate the two. The package asks which
current engine is the cheapest place to apply this next. Its first-ranked candidate (the
Apollo raw / oracle-state / corrupted-state arms) is marked as awaiting operator
authorisation, so I did not run it. I ran the second-ranked candidate, which is the
cheapest one in the evolution engines: a two-depth injection on the W2_K2 "half-credit
shelf" organisms of the WSE world (two keyed streams; PUT tagA vA, PUT tagB vB, then ASK
each tag). Before reading any lift, I tested the package's own precondition for
interpretability: an injection means something only if the organism's downstream
computation depends non-trivially on the state and on the ask.

2. WHAT I DID

Repository clone at origin/main 6ff2b2f8ad035d50aaf21d9f3b60e16c556683f2. Exported with
git archive into work/R-25/src: archaeon/wse (worlds.py, evolve.py, interventions.py,
controls.py), proteus/foundry (vm.py, prng.py), archaeon/campaign2/c2base.py, and the
committed specimens archaeon/campaign3/C3-SFE-01/rows.json (final elite manifests). All
code ran from the export, with GIT_* unset.

Specimens: every SHELF-level final elite in C3-SFE-01 rows.json, de-duplicated by manifest:
19 unique organisms (11 "fresh", 8 "shelf" arm). Battery: 64 W2_K2 4-bit episodes, train
family, my own seed and index (episodes_for(W2_K2, 20260928, "train", 2525, 64)). No
held-out family was used. Scoring: per-ask credit, the same VM and evaluator conventions as
the campaign (vm rng seed 5).

Scripts (in work/R-25): probe.py (python3 probe.py 64 -> probe_results.json, probe64.log)
and probe2.py (-> probe2_results.json). Arms:
- RAW.
- KEY COUNTERFACTUALS (the mechanism precondition): re-run each ask with the ask's tag
  replaced by the other stream's tag (KEYSWAP) or by an unseen tag (KEYNOVEL). Measure the
  fraction of outputs that change.
- STORE LOCATION: the register or tape cell whose pre-ask value equals the organism's
  answer in at least 95% of episodes (found for 17 of 19 organisms).
- STORE DEPTH, key-blind (OWN_OTHER): once, before the asks, write the value of the stream
  the organism does NOT remember into its own store location. This checks that the
  location is causal.
- STORE DEPTH, harness-keyed (OWN_ORACLE): before each ask, write the asked stream's value
  into the store location. The harness performs the keying here, so this is a counterfeit
  upper bound and is reported as one.
- STORE DEPTH, spare location (SPARE): write the second stream's value into one other
  location (every register and every non-code tape cell, one at a time; 1,705 placements
  in total) and keep the best score.
- STORE DEPTH, keyed two-slot layout (BOTH_KEYED): write tagA, vA, tagB, vB into four spare
  tape cells.
- DECODABILITY (probe2): is each stream's value held in a consistent location before the
  asks (at least 95% of episodes)? Are both tags present anywhere in the state?
- POSITIVE CONTROL of the instrument (probe2): the hand-written keyed reader POS_TABLE
  (controls.py). I erased its second table entry before the asks (a representation lesion
  with the mechanism intact), then re-injected it at store depth, and also injected a
  corrupted value. The mechanism lesion was simulated by making the reader key-blind.

3. RESULT

Instrument positive control (POS_TABLE, 64 episodes, per-ask):
  raw 1.000; second entry erased 0.500; erased + store-depth re-injection 1.000;
  corrupted injection 0.500; intact table + key-blind read 0.578 (chance with 4-bit
  collisions). The two-depth design does discriminate when one side is present.

Shelf organisms (n = 19 unique):
  RAW per-ask reward             0.531-0.586 (mean 0.574; 0.5 plus 4-bit collisions)
  KEYSWAP outputs changed        0.000 in 19/19 organisms
  KEYNOVEL outputs changed       0.000 in 19/19
  both tags present pre-ask      0.000 in 19/19 (at most one tag word; never both)
  second value held consistently 3/19 (fresh s3, s10, s11 hold both values in fixed
                                  registers); 16/19 hold one value only
  OWN_OTHER (key-blind store inj) 0.570-0.578; outputs follow the injection in 42-84% of
                                  asks. The location is causal, but the score only flips
                                  which stream is right.
  OWN_ORACLE (harness-keyed)     0.984-1.000 (counterfeit: the harness supplies the keying)
  SPARE (1,705 placements)       0 placements lifted the reward by >= 1/32; best = raw
  BOTH_KEYED (11 organisms with tape) 0.453-0.586; no lift, one organism damaged
Two organisms (fresh s3, s11) answer differently on the two asks of an episode (84%), but
by ask POSITION, not by key: their outputs are still key-invariant.
CPU: about 75 s in total.

Plain conclusion: on the W2_K2 shelf the ask-tick computation of every specimen does not
depend on the key at all. No specimen stores both tags. So no injection at store depth can
raise the score unless the harness itself selects by key, and that makes it the
counterfeit "answer into the readout register" case the package warns about. Where the
second value is present (3/19), nothing uses it. Where it is absent (16/19), injecting it
anywhere is ignored. The failure is on the mechanism side (key binding plus keyed
selection) in every specimen, and in 16/19 the second value is also missing. The upper
bound becomes non-trivial only when both a keyed store and a keyed reader are supplied,
and at that point the organism contributes nothing: it is the hand-written control.

4. DID IT RESOLVE THE QUESTION

Partly. For the W2_K2 shelf the answer is clean and cheap: this is a mechanism ceiling, and
the two-depth decomposition is degenerate there. It is not badly engineered; it is badly
posed for these specimens, because the precondition (downstream computation that depends
non-trivially on the state and the key) fails in 19/19. So the shelf is the cheapest
place to RUN the injection, but it is not an informative place to apply it. The
engine-ranking question stays open. The first-ranked candidate (Apollo) meets the
precondition by construction, because a parse feeds a non-trivial scorer. The committed
fixture (roles/Lexis/handoff/state_injection_fixture.json@9962f6bd4) and the E9 scorer
are present. I did not run it because it awaits the operator's authorisation. The
evolution-engine specimens that would meet the precondition, the two-value organisms
evolved under all-or-nothing credit (campaign 3, experiment 08: held-out episode credit
equal to per-ask credit, 0.44-0.65), are not usable: their manifests are not committed
(rows.json carries summaries only).

5. CONSEQUENCES

- A false premise: the package's option (2) assumes the shelf organisms have an "own read
  location" for the second key whose filling could reveal a representation gap. They have
  no key-conditioned read at all, so filling any location either does nothing or, if the
  harness keys it, counterfeits the answer. This is a reproduction and a sharpening of the
  earlier shelf anatomy (one-value memory; no single edit supplies keying), now with a
  causal, state-level test: key-swap changes 0% of outputs.
- New small positive facts: 3/19 shelf specimens already carry BOTH values in fixed
  registers (so the second value was not the whole missing piece for them), and 2/19 use
  an ask-position heuristic. Both are useful to whoever pursues the W2_K2 summit through a
  changed organism or search (the campaign-4 "C4-3" line): the missing primitive is key
  binding plus keyed selection, not value storage.
- Method rule for any engine (worth adopting as a gate): run a key or ask counterfactual
  before any state injection. If outputs are invariant to the query, the injection is
  uninterpretable. The POS_TABLE lesion/re-injection is a ready-made positive control for
  the instrument in WSE.
- A small reproducibility gap: the C3-SFE-08 two-value elites should have their manifests
  committed. They are the only evolved WSE specimens where a state-injection split could
  be informative.
- Who should know: Archaeon (the WSE owner and shelf specimens), the owner of the Apollo
  task (its injection design remains the best-posed candidate and is blocked only on
  authorisation), and the operator (for that authorisation decision).

6. COST

About 1 hour of my own time. About 75 CPU-seconds of computation, one process at a time,
well under 1 GB RAM. I did not run the Apollo arms (not authorised). I did not build a
genome-level splice of a witness READ block into the shelf genomes: with key-invariant
readers and no stored tags, the splice can only succeed together with an injected keyed
store, which is the hand-written control. I did not examine the Ares carrier option
(ranked low value in the package).
