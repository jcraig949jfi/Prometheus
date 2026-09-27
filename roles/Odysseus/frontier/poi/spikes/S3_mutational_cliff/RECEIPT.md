# S3 -- mutational cliff: D7 eligibility of the 0/5,472 census

Odysseus POI frontier, disposable spike worker, 2026-09-27. Pure
re-tabulation of committed rows; nothing re-run, nothing modified outside
this directory. Not committed.

## Question

The "0 of 5,472 single edits improved a parent" (C4-01, cited via
8f1a82ced / DAMAGE_GEOMETRY_MAP; HEPH-32 "the C4 cliff"):
(1) how many edits were ELIGIBLE to improve (parent non-degenerate,
parent below max on its own environment, edit actually applied)?
(2) among eligible: fraction improved / neutral / deleterious / lethal?
(3) 95% upper bound on the improvement rate with the eligible n?
(4) cliff (few neutral) or plateau (many neutral)?
Readings under test: I4 TH-I4-04 (headroom artefact) vs E6-17/18
(encoding cliff; split into neutral / deleterious / lethal).

## Data (all in git; per-edit rows ARE committed)

- repo HEAD at run: e82bf231171775474a27ef3b1f637081332af943
- rows: archaeon/campaign4/C4-01/attempts/a02/children.json.gz
  (blob 04437f2d4ada..., committed in 9542fa37a0c9, "C4-01 ... attempt
  a02 of record"). 5,586 rows = 5,472 edits + 114 controls, raw evaluate()
  dicts per environment. Decompressed sha256 770390365b2f2459...63db
  VERIFIED against CHILDREN_DIGEST.json (blob bce6d6d43f9e...).
- definitions: archaeon/campaign4/C4-01/DESIGN.md (blob b2e52add803e...)
  and DECISIONS.md D4-003 (band 1/16, floor 3/16), D4-004 (parent env per
  stratum). READOUT.md blob d97341ff731e....
- Note: 8f1a82ced is the campaign-4 CLOSE commit (C4-10 + map); the
  census rows themselves entered in 9542fa37a.

## Command

    cd /home/jcraig/Prometheus-worktrees/odysseus-base-role
    python3 roles/Odysseus/frontier/poi/spikes/S3_mutational_cliff/probe.py

Stdlib only, 1.5 s. Output: s3_result.json (sha256 85f48fa635ee...).

## Definitions used (C4's own constants)

- eligible: parent_degenerate == False AND parent_reward + 1/16 < 1.0
  (room for a D7 on the parent environment) AND applied == True.
  The loose rule "parent_reward < 1.0" gives the same set here.
- on the parent environment, reward_per_ask r vs parent p:
  improved r > p + 1/16 (= D7); lethal = D2 (no / one constant answer)
  or r == 0; neutral |r - p| <= 1/16; deleterious = the rest (viable-
  worse D4 plus low-but-nonzero D3). There is no crash class: the
  interpreter is total (D4-002), so "lethal" = behaviourally dead.

## Numbers

Funnel over 5,472 edits:

    parent at ceiling (1.0)      2,496  (w0_solver 1,440 on W0;
                                         delay_general 1,056 on W1_d4)
    parent degenerate            1,152  (gen0_random, reward 0 / 0.0625)
    could not apply (eligible parent, operator noop)   256
    ELIGIBLE (applied)           1,568  (all 19 shelf parents, W2_K2,
                                         parent reward 0.531 or 0.688)

So 3,648 of 5,472 (66.7%) could not improve by construction; 1,568
(28.7%) could. (Delegate's inference was 2,339 ceiling + 1,035
degenerate from APPLIED counts incl. controls; the true per-draw counts
are 2,496 + 1,152, direction confirmed.)

Outcomes among the 1,568 eligible:

    improved       0   0.000   (Wilson95 upper 0.0024)
    neutral      967   0.617   (966 exactly unchanged; 961 displacement 0)
    deleterious   74   0.047
    lethal       527   0.336
    (D labels: D5 948, D2 409, D3 141, D4 40, D6 30)
    + 30 of these are D6 exaptive (better on ANOTHER env).

Upper bound on the improvement rate: 0/1,568 -> rule of three 0.0019
(one-sided Clopper-Pearson 0.0019; two-sided Wilson 0.0024). The pooled
claim "0/5,472" implied 3/5,472 = 0.00055; the honest bound is 3.5x
looser.

For contrast, all applied non-degenerate edits incl. ceiling parents
(n = 3,855): neutral 2,041, lethal 1,711, deleterious 103, improved 0.

Neutral fraction by operator (eligible): reference_redirection .93,
operand_perturbation .83, config_perturbation .71, region-level edits
(randomization .45, splice .48, region_swap .48) lowest.

## What changed vs the two readings

- Headroom reading (I4 TH-I4-04): CONFIRMED in part. Two thirds of the
  census had no possible improvement; the headline denominator is
  wrong. But it does not dissolve the null: 0/1,568 on the eligible
  shelf parents still bounds the single-edit improvement rate below
  ~0.2%.
- Encoding-cliff reading (E6-17/18): the "all-lethal cliff" version is
  NOT supported. 62% of eligible edits are neutral (mostly bit-silent),
  a PLATEAU, not a cliff; lethal is 34%, deleterious-but-viable only
  5%. The distribution is bimodal (neutral-or-dead, little graded
  worse), which is the real "cliff" C4 described (displacement), not
  an absence of neutral neighbours.
- Net: BOTH, re-scoped. The 0/5,472 is mostly a headroom/degeneracy
  artefact in its denominator; what remains is a large neutral plateau
  with no one-step uphill from these 19 shelf parents, plus a sharp
  neutral/lethal dichotomy. Per E6-18's own criterion (neutral fraction
  predicts evolvability) the substrate is drift-capable; the open
  question is whether the plateau connects to better programs (C4-05).

## Avida comparison (CITED, NOT VERIFIED)

raw/E6 gives no Avida NEUTRAL fraction. It cites only "roughly 20-40%
lethal for evolved genomes" (E6-17 item 6), itself marked UNVERIFIED in
E6. Prometheus eligible lethal = 33.6% sits inside that cited range. No
neutral-fraction comparison is possible from committed sources.

## Limits

- Eligible set is ONE stratum (19 shelf parents, one env W2_K2, K=2);
  the bound says nothing about other parent classes at non-ceiling
  reward. Edits are not independent (8 draws x 12 ops per parent), so
  the effective n is smaller than 1,568 and the true bound looser.
- 16 CRN episodes per env; band 1/16; D3/D4 counts move with the floor.
- "Lethal" here is behavioural degeneracy/zero score, not failure to
  replicate (Avida's sense); the interpreter cannot crash.
- Ceiling parents could still show improvement on held-out/other envs
  (D6); that is exaptation, excluded from "improve" by design.
- Radius 1 only; the grammar's own operators; one frozen substrate.
