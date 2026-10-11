# In-house code benchmark on M2 -- the program's own functions (PAN-34)

Generated 2026-10-11T01:21Z by `python -m pan repobench report` from pan.code_bench rows; numbers are not
typed. Protocol: pan/tests/repobench_prereg.json (1e5276818; A1 5bea01bb9; A2 d17d33d52).

## Task set

    tree 8bda1de0f; 1381 test files -> 755 pass the static filter -> 491 pass in the sandbox
    -> 365 candidates examined (seed 34): 0 flaky, 103 unseen by their tests, 102 capped
    -> 160 tasks; A2 primary set 142 (the 18 tasks a `pass` body satisfies are secondary only)

## Result (primary set, greedy pass@1, Wilson 95 percent)

    configuration                        passed  pass@1  Wilson          failure shapes
    qwen2.5-coder:14b @1024              59/142   0.415  [0.338, 0.498]  test failed 83
    gpt-oss:20b @4096                    53/142   0.373  [0.298, 0.455]  empty response 54, test failed 29, syntax error 6
    qwen3:8b @1024                       50/142   0.352  [0.278, 0.434]  test failed 89, test timeout 2, syntax error 1
    gemma3:12b @1024                     35/142   0.246  [0.183, 0.323]  test failed 99, syntax error 8
    gpt-oss:20b @1024                    21/142   0.148  [0.099, 0.216]  empty response 104, syntax error 15, test failed 2

## Comparisons (primary: Wilson intervals apart; secondary: exact McNemar, Holm over 10 pairs)

    gemma3:12b@1024 vs gpt-oss:20b@1024: discordant 29 / 15, p = 0.0488, Holm keeps; Wilson overlap
    gemma3:12b@1024 vs gpt-oss:20b@4096: discordant 15 / 33, p = 0.0133, Holm keeps; Wilson overlap
    gemma3:12b@1024 vs qwen2.5-coder:14b@1024: discordant 4 / 28, p = 0.0000, Holm rejects; Wilson apart
    gemma3:12b@1024 vs qwen3:8b@1024: discordant 9 / 24, p = 0.0135, Holm keeps; Wilson overlap
    gpt-oss:20b@1024 vs gpt-oss:20b@4096: discordant 0 / 32, p = 0.0000, Holm rejects; Wilson apart
    gpt-oss:20b@1024 vs qwen2.5-coder:14b@1024: discordant 8 / 46, p = 0.0000, Holm rejects; Wilson apart
    gpt-oss:20b@1024 vs qwen3:8b@1024: discordant 9 / 38, p = 0.0000, Holm rejects; Wilson apart
    gpt-oss:20b@4096 vs qwen2.5-coder:14b@1024: discordant 18 / 24, p = 0.4408, Holm keeps; Wilson overlap
    gpt-oss:20b@4096 vs qwen3:8b@1024: discordant 20 / 17, p = 0.7428, Holm keeps; Wilson overlap
    qwen2.5-coder:14b@1024 vs qwen3:8b@1024: discordant 20 / 11, p = 0.1496, Holm keeps; Wilson overlap

Tasks no configuration solved: 61 of 142; solved by all 5: 6.

## Precommitments (written before any model ran)

    P1: HOLDS  {"measured": 5, "of": 5, "lost_on": [], "gaps": {"ollama:gpt-oss:20b@nothink1024": 0.705, "ollama:qwen2.5-coder:14b@nothink1024": 0.438, "ollama:gemma3:12b@nothink1024": 0.527, "ollama:qwen3:8b@nothink1024": 0.427, "ollama:gpt-oss:20b@nothink4096": 0.535}}
    P2: LOST  {"beaten": [["ollama:gemma3:12b@nothink1024", "ollama:gpt-oss:20b@nothink1024"], ["ollama:qwen3:8b@nothink1024", "ollama:gpt-oss:20b@nothink1024"]]}
    P3: HOLDS  {"values": {"ollama:gpt-oss:20b@nothink1024": 0.148, "ollama:gpt-oss:20b@nothink4096": 0.373}}
    P4: PENDING  {}

## Note added by hand (2026-10-11, not generated)

    P4 (the size arm, A3) shows PENDING above because no run of it succeeded. It is NOT RUN, not pending:
    qwen2.5-coder:32b at num_ctx 8192 needs 22 GB on the 16 GB card, ran 35 percent on the CPU and took
    14 GB of M2's RAM; the host reached 89 percent RAM and the run was stopped (prereg amendment A4,
    QUESTIONS.md Q-013). P4 has no verdict.
