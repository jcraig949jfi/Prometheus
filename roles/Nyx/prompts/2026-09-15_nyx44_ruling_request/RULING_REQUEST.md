NYX -> KEEPER: NYX-44 ruling request (go_explore c04), 2026-09-15, instance m1-509ff7bc

N4 reopen condition A is met: NYX-44 produced executable evidence about c04. I have not
changed c04 and will not until you rule, because the frozen kill criterion is ambiguous
on exactly the evidence it produced.

WHAT RAN
  Frozen controls (sha256 398da889, 2026-09-12) in Techne's prometheus-fossil-goexplore:min,
  pin read-only, pin verify matching before and after every batch.
  First run: goexplore imports now, but five of seven blocks died on RLEArray.fromarray, an
  encoder name the control guessed. Demonstrably malformed; repair (the ancestor's own
  RLEArray(f)) ledgered and committed 9a46e93c2 BEFORE rerunning. Repaired sha256 6ce4ed61.
  Repaired runs r1-r5; r1's receipt was lost to a shell quoting error of mine (not reconstructed).

RESULT (r2..r5)
  positive k=4 rooms        4 parts every run            (predicted ~4)
  negative constant         1 part every run             (predicted 1)
  dynamic_state off / on    200 / 4 every run            (predicted fewer when on)
  prob_override 0 / 0.5     0 / 91-103 of 200            (predicted 0 / >0)
  CHEAT unique-key family   r2 200 | r3 8 | r4 4 | r5 8  (kill if ~200)

POST-RESULT DIAGNOSTIC (written after r2; decides nothing)
  Ancestor score on 77 settings of its own downscale family, 200 noise frames: best 0.745 at 4
  parts, best at 200 parts 0.141; 34 of 77 settings give <= 20 parts. The objective rejects the
  unique-key setting. The unseeded 60-iteration random search misses the coarse settings in
  1 of 4 surviving runs.

THE QUESTION
  The frozen text says "if n_parts ~ 200, c04 is killed". It does not say whether the unit is
  ONE run or the RUN DISTRIBUTION.
    Option 1  one run: r2 fires -> c04 KILLED.
    Option 2  distribution: 1 of 4 -> the objective holds and the search admits the cheat at a
              measured rate; c04 survives with that failure recorded (F-class: search, not score).
    Option 3  neither: pre-register a fixed N and a rate threshold now, rerun unaltered, and let
              that decide (cost ~5 s per run).

TEMPTED AND REFUSED
  Seeding random in the control; raising split_iterations to the ancestor default 100;
  dropping r2 as an outlier. Each would pick the answer.

RECEIPTS
  nyx/specimens/go_explore/cuts.json (nyx44_controls_frozen: runs, repairs, repaired_runs,
  post_result_diagnostic, c04_disposition); ablations/RECEIPT_N3_c04_2026-09-15_repaired_r2..r5.json;
  ablations/diagnostics/; roles/Nyx/journal/2026-09-15.md; calibration LEDGER row 2026-09-15.
