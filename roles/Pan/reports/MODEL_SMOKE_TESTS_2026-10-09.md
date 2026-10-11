# Local model smoke tests on M2 (PAN-19, charter C5 "run locally and tested")

Currency: 2026-10-09T14:18Z (commit 042d832b8 receipt; first typed as 14:20Z without a clock read). Host M2 (SPECTREX5), RTX 5060 Ti 16 GB,
Ollama 0.35.0, temperature 0, seed 1. Fabric lease lse-d045e7a2eb61
(spectrex5:gpu0), released 14:17Z. Rows: pan.model_bench (every response kept;
any check can be re-run). Command: `python -m pan modelbench MODEL... [--think
--budget N]`; harness pan/modelbench.py, controls pan/tests/test_modelbench.py.

THIS IS A SMOKE TEST, NOT A BENCHMARK: 15 probes (6 code with hidden tests run in
a fresh `python -I` subprocess, 6 exact-integer math, 3 JSON shape). A pass rate
of 13/15 has a 95 percent interval of roughly 0.62-0.96. Read it as "loads on this
card, runs at this speed, follows basic instructions", not as a ranking.

## Results (after the answer-key correction below)

    model (Ollama tag)      config        pass  code math json  trunc  tok/s  load s  size   licence (HF)
    gpt-oss:20b             think 4096    15/15  6/6  6/6  3/3    0     90.1   11.3   13 GB  apache-2.0
    gpt-oss:20b             nothink 1024  15/15  6/6  6/6  3/3    0     87.3   16.5   13 GB  apache-2.0
    qwen3:8b                think 4096    15/15  6/6  6/6  3/3    0     71.4    5.3  5.2 GB  apache-2.0
    gemma3:12b              nothink 1024  15/15  6/6  6/6  3/3    0     47.9   20.2  8.2 GB  (not in catalog)
    qwen3:14b               think 4096    15/15  6/6  6/6  3/3    0     42.9    7.7  9.3 GB  (not in catalog)
    qwen3:14b               nothink 1024  14/15  6/6  5/6  3/3    0     43.6    7.6  9.3 GB
    qwen3:4b                think 4096    13/15  4/6  6/6  3/3    2    114.5    3.5  2.5 GB  apache-2.0
    granite3.3:8b           nothink 1024  13/15  5/6  5/6  3/3    1     73.5    4.6  4.9 GB
    qwen3:8b                nothink 1024  13/15  6/6  4/6  3/3    0     73.4    6.8  5.2 GB  apache-2.0
    deepseek-r1:8b          think 4096    13/15  4/6  6/6  3/3    1     71.8    5.2  5.2 GB
    phi4-mini               nothink 1024  12/15  5/6  4/6  3/3    0    130.2    3.6  2.5 GB
    qwen2.5-coder:14b       nothink 1024  12/15  6/6  3/6  3/3    0     43.6   14.7  9.0 GB
    deepseek-r1:8b          nothink 1024   8/15  4/6  1/6  3/3    6     71.3    -    5.2 GB
    qwen3:4b                nothink 1024   4/15  0/6  4/6  0/3  (12)*  118.5   24.4  2.5 GB  apache-2.0
    * first pass ran before TRUNCATED flagging; eval_tokens = 1,024 on 12 of 15 probes.
    All models ran 100 percent GPU-resident (`ollama ps`). Licence column from
    pan.hf_model where the mapped HF repo is catalogued; blank = not in the catalog.

## Readings

- gpt-oss:20b passes everything in both configurations at ~90 tok/s and fits the
  card (13 GB): the strongest general local model measured here. qwen3:8b with
  thinking also passes everything at ~71 tok/s in 5.2 GB: the best small one.
- Thinking cannot be switched off for some models under this runtime: qwen3:4b
  ignored think=false and reasoned in plain text until the token cap (4/15),
  and deepseek-r1:8b always reasons (6 truncations). With thinking and a 4,096
  budget both reach 13/15. For a mutation operator in an evolutionary loop,
  budget the tokens for the configuration that actually runs.
- Every model that passed 6/6 code did so on HIDDEN test inputs; the cheat
  control (a solution hard-coded to the prompt's example) fails those tests.

## Instrument defects found and fixed in this run (calibration ledger)

1. WRONG ANSWER KEY: math_system expected 49; the correct value is 45 (x=4, y=5).
   Found because every model "failed" the same probe (0/14). Fixed, an
   independent derivation of every math key added to the controls, and the 14
   stored math_system responses re-scored (11/14 pass). Rows carry the note
   "[rescored 2026-10-09: key 49 -> 45]".
2. THINK SWITCH IGNORED (above): the harness now labels configurations
   (@nothink1024, @think4096) and flags TRUNCATED responses.
3. A transient refused connection to M1 ended the first run after 3 models;
   connections now retry at connect only (3 attempts).

## Calibration of the intake's 16 GB fit estimate (added 2026-10-09 after the run)

The 9 models' HF repos were fetched explicitly (`pan.frontier.hf.fetch_repos`)
and their Ollama Q4 file sizes divided by the safetensors parameter counts:
median 0.630 bytes/param (0.600 qwen2.5-coder... 0.673 gemma3). The estimator
had assumed 0.5625 (4.5 bits) and so under-estimated file size by about 11
percent; it now uses 0.63 (pan/frontier/hf.py). Recomputed over 1,510
catalogued models: 8 fits_16gb_q4 verdicts changed (borderline 23-26B models).
All 9 tested models were predicted to fit and did (100 percent GPU) -- these
are positives only; no predicted non-fit was loaded.

## Not measured (candidates)

Lean provers (Goedel-Prover-V2-8B, Kimina, Pythagoras-Prover-4B) need a Lean
toolchain as the verifier -- a prover smoke test without a proof checker would
be scoring the model's self-report. Embedding models: measured separately
(bge-small 1,050 chunks/s, Qwen3-Embedding-0.6B 34 chunks/s at 512 tokens).
