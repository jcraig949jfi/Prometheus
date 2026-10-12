# Local code benchmark on M2 -- HumanEval+ (PAN-33)

Currency: 2026-10-09 (frozen runs 17:59Z-18:41Z, date -u / pan.run receipts).
Protocol frozen before any model ran: pan/tests/codebench_prereg.json (6bb3dbd9d),
amendment A1 before any model result (2e758ec03: HumanEval/32 excluded -- its test
star-unpacks the candidate's float return and cannot be passed). Rows: pan.code_bench
(one row per model x task, response kept) and roles/Pan/reports/codebench/ (controls,
per-task export). GPU lease lse-b3dea75dd6d4, released 18:41Z.

CAVEAT stated before running: HumanEval (2021) is very likely in every model's
training data. Read ranks and speeds, not absolute capability.

## Controls (all pass after A1)

    canonical solutions        163/163   (POSITIVE: the harness can see a pass)
    stub body (`pass`)           0/163   (CHEAT: the tests discriminate)
    prompt only, no body         0/163   (NEGATIVE)

## Frozen result (greedy pass@1, no thinking, 1,024-token budget)

    model               passed   pass@1   Wilson 95%      tok/s   truncated   wall s
    gpt-oss:20b         139/163  0.853    [0.790, 0.899]   88.7       19       956
    qwen2.5-coder:14b   139/163  0.853    [0.790, 0.899]   43.6        0       513
    qwen3:8b            127/163  0.779    [0.709, 0.836]   75.2        0       266
    gemma3:12b          126/163  0.773    [0.703, 0.831]   48.4        0       851

Preregistered comparison rule (intervals must not overlap): NO pair is separable.

## Exploratory (not preregistered; cannot change the verdict above)

- 19 of gpt-oss:20b's 24 failures were truncated at the 1,024-token budget; the other
  three models had no truncations. Its tie with qwen2.5-coder is likely a budget effect.
- Paired per-task (McNemar exact, uncorrected for 6 comparisons): qwen2.5-coder vs
  qwen3:8b p = 0.043, vs gemma3 p = 0.024; gpt-oss vs gemma3 p = 0.041, vs qwen3:8b
  p = 0.050; the top pair are identical in count (13 / 13 discordant).
- 7 tasks defeat all four configurations: HumanEval/76, 91, 130, 132, 145, 154, 163.
- Successor run (post hoc, chosen AFTER seeing the truncations; lease lse-3610c68559ea,
  18:42Z-19:05Z): gpt-oss:20b at a 4,096-token budget passed 148/163, pass@1 0.908,
  Wilson [0.854, 0.943], 88.6 tok/s, 9 still truncated, 1,380 s. Paired with its 1,024
  run: 9 tasks newly passed, 0 lost. Its interval clears qwen3:8b's and gemma3's upper
  bounds -- but because the configuration was added after the results, it is reported
  as exploratory and does not enter the frozen comparison.

## Reading for the program

For a code-mutation operator on this card: gpt-oss:20b with a token budget of about
4,096 is the strongest measured (0.908, ~89 tok/s, 13 GB; exploratory configuration);
qwen2.5-coder:14b is the most budget-robust (no truncation at 1,024, 0.853, 44 tok/s);
qwen3:8b is the fast small option (75 tok/s, 5.2 GB) at a lower but not separably
lower rate. Budget the tokens: truncation, not capability, set gpt-oss's first score.
