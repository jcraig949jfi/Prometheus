# RESULT -- regate_v01: A8-repaired battery, known-answer re-gate + exploratory unplanted

Currency: 2026-09-28. Fresh worker (did not write the battery or the cold-start). Pure ASCII.
Prereg: PREREG.md (written 11:04Z, before any run; inputs pinned in inputs.sha256).
Amendment: AMENDMENTS_v01.md A1 (the unplanted stop was made stricter; no rule changed).
Code: world_v01.py, battery_v01.py (copies of ../world.py, ../battery.py with additions only),
run_regate.py. Data: gate_v01.json, unplanted_v01.json, gate.log, unplanted.log.
Host: shared 4-core laptop, 1 process, Python 3.14.4, stdlib. Gate 384 s wall, unplanted 366 s.
n = 20 worlds per arm (seeds 1000..1019), per-world salted probe seeds (A6), delta = .05.

## 1. Gate verdict: PASS (13/13 criteria)

Repaired rules (PREREG s2): R0 += PASS(H_hist) AND PASS(E0); R3 += PASS(H_hist)
AND PASS(D_episode) AND D_episode >= .5 D1. H_hist = different-history twin
(same world, S*-30 rerun under a different physics/event stream, minus the
same stream with other organism coins; mismatch of recently written cells).
E0 = the R0 decoder applied to the own record from 50 generations earlier.

    arm     rung  rung   D0          H_hist       E0          D1          Dp          Dr          D_episode    expected  ok
            v01   orig
    P       R3    R3     .594        .681[.59,.76] .597       .470        .489        .461        .450[.36,.54]  R3      yes
    P4      R3    R3     .549        .412         .542        .411        .420        .424        .361          R3      yes
    N_a     R0    R0     .606        .706         .591        0           0           0           0             <=R0    yes
    N_b     none  none   -.018       -.747        .031        .051 ns     .071 ns     .040 ns     .078 ns       <=R0    yes
    C       R2    R2     .224        .447         .215        .460        0           0           0             R2,!R3  yes
    P_sigma R0    R0     .629        .700         .584        .041 ns     .041 ns     .031 ns     .080 ns       R0      yes
    P_cb    R3    R3     .374        .475         .335        .583        .623        .558        .331          R3      yes
    P_cal   R3    R3     .568        .506         .519        .531        .570        .543        .540          R3      yes
    T       none  R3(!)  .073        .003[0,.009] .005        .380        .462        .355        .000          no R0   yes
    CAL     none  R3(!)  .141        .000[0,0]    .019        .311        .440        .322        .381[.23,.53] no R3   yes
    DECOY   R2    R3(!)  .353        .212[.17,.26] .267       .381        .462        .349        .000          R2      yes

  ("rung orig" = the frozen ../battery.py decide() on the same data; "ns" = not PASS;
   D2 = D1 in every planted arm, as in the original; A/A CI contains 0 in all 11 arms.)
  Other criteria: P INSTALLED vs P_sigma (A2 3-way also INSTALLED); P not R4/R5;
  secondary P4 R4: NOT awarded (as in the fixture run 2; R4 detection stays unvalidated).
  G0 identity: the v01 code reproduces all 6 x 840 = 5040 original per-world
  values of ../known_answer.json exactly (0 mismatches), and the original
  decide() gives the fixture's rung and tests dict for every original arm.

## 2. Cheats: which were caught, and by which clause

  T (nest tag, cold-start): CAUGHT. Old battery: R3. Now: H_hist .003, E0 .005,
    D_episode 0 -> R0 fails (so highest none) and R3 fails on both A8 clauses.
    Under the A3 (independent rungs) reading T still earns R1 and R2 (a static
    label is read and used) and fails R0 and R3 -- which is the correct
    description.
  CAL (calendar tag, new; clock-driven tag, 4 phases, epoch 50, offset 25):
    CAUGHT, and only by H_hist at R3. Consumer D_episode .381 [.229, .530]
    PASSES (the cheat defeats the episode test, as designed); Dp, Dr pass;
    H_hist exactly 0 in all 20 worlds (every history gives the same tag). At
    R0 E0 (.019) also catches it (the LOO decoder learns old tag -> current
    site). Old battery: R3.
  DECOY (decoy cell, new; static tag in cell 0 is what readers use, a genuine
    found-site record in cell 1 nobody reads): H_hist .212 PASSES (defeated;
    per-cell H: cell0 .003, cell1 .422), D0 and E0 pass -> R0 awarded
    (correctly: cell 1 is history-specific and persists). CAUGHT at R3 by
    consumer D_episode = .000. Highest R2, as preregistered. Old battery: R3.
  So the two A8 clauses are complementary, each necessary on this set: CAL
  shows D_episode alone is insufficient, DECOY shows H_hist alone is
  insufficient. Every prediction in PREREG s5 held in direction and
  approximate size (T H .003 predicted ~.003; DECOY H .21 within .2-.4).

## 3. Original verdicts preserved? YES

P R3, P4 R3, N_a R0, N_b none, C R2 (failing R3 on content: Dp = Dr = 0),
P_sigma R0 -- identical to known_answer.json run 2. Sensitivity (literal
consumer D_episode clause at R0, not decisional): N_a and P_sigma would
lose R0 (D_episode 0 / ns without working readers), as predicted -- the
reason E0 was used (PACKET_GAPS G1).

## 4. Unplanted (EXPLORATORY; gate passed first)

Configuration of ../unplanted.json (3000 gens, seeds 1000..1019). Ran U_sigma,
U_id, U_frozen, all 60 worlds (U_unread/U_norec not re-run: no record
statistics; R5 uses each arm's own no-record ceiling). Identity: 60/60
worlds reproduce all 41 original per-world values in ../unplanted.json exactly.

    arm       rung v01  D0              H_hist           E0               D1                D_episode         worlds H>.05 / D1>.05
    U_sigma   none      .031[-.011,.076] .044[-.023,.109] .024[-.029,.076] .005[-.003,.016]  .005[-.009,.020]  10/20 , 1/20
    U_id      none      .029[-.013,.072] .031[-.018,.078] -.007[-.051,.039] .007[-.001,.018] -.003[-.012,.003] 9/20 , 2/20
    U_frozen  none      -.005            -.010            .045[.001,.086]   -.094[-.187,-.009] -.102[-.192,-.018] 5/20 , 2/20
  Convention (A2): NO-BENEFIT (neither U_id nor U_sigma has a benefit).
  The original "none in every unplanted arm" is unchanged by the repair.

Seed 1016 (U_sigma, the outlier): D0 -.150 (intact .25 vs ablated .40),
  H_hist -.125 (alt .72, same .84 over all 8 cells), E0 .088, D1 .094,
  D2 .217, Dp .219, Dr .113, D_episode .122, reader fraction .72.
  Per-world, the consumer tests (D1, D2, Dp, Dr, D_episode) all exceed delta:
  the benefit follows content AND the episode test says the content is not
  static. But H_hist is NEGATIVE: the record is rewritten every generation
  and depends MORE on organism coins than on the environment stream, so the
  different-history twin cannot show history-specificity. Under the
  repaired rules 1016 is refused R0 and R3 (on H_hist and D0). Reading:
  1016 is not a nest-tag cheat (D_episode .122 rules that out) but its
  record is noise-dominated; it remains a one-world lead, not a result.

## 5. Remaining weaknesses (found here)

W1 H_hist is a DIFFERENCE of two sensitivities (environment stream vs
   organism coins). A record that is coin-dominated scores negative even
   if it also carries history (N_b -.75; seed 1016 -.125). It detects "the
   environment history moves the record more than organism noise does",
   not "history moves the record". A better statistic: condition on the
   organism coins (alt = different physics, SAME bio stream) vs a second
   independent physics stream, or report alt vs a no-history floor.
W2 H_hist is computed over all recently written cells, not over the cells
   the consumer depends on -> DECOY defeats it. Fix: weight cells by their
   per-cell deletion effect (S1 with that cell deleted), or declare X per
   cell.
W3 D_episode uses one lag (50). A tag cycling with a period that makes the
   50-back record informative-but-different passes it (CAL). It is also
   defeated by any slow label whose change coincides with the lag. Only
   H_hist stops those; together they close this set, not the class.
W4 A cheat that defeats BOTH: a record driven by the physics stream but not
   by the environment the consumer is rewarded on (e.g. a tag re-drawn by
   record noise that the environment bias is coupled to through physics)
   would pass H_hist and D_episode. Not built; the gate set is 3 cheats,
   not a proof.
W5 Thresholds: delta = .05 is used on H_hist's mismatch scale without
   justification; P's H ranges 0.00-0.88 per world (one P world scores 0).
W6 R4 detection remains unvalidated (P4 I not PASS at n = 20).
W7 D1 = D2 in all planted arms (clonal colonies): R2 is not separated from
   R1 in this sandbox (original critique C5, still open).

## 6. Not done

No change to ../battery.py or ../run_battery.py (the repaired battery lives
only here); no packet/ledger update; U_unread/U_norec baselines not re-run.
Nothing here is committed. All unplanted numbers are EXPLORATORY.
