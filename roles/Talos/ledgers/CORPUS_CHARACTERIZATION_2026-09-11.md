# Talos corpus characterization, 2026-09-11

Currency: 2026-09-11. Every number is from
roles/Talos/ledgers/CORPUS_CHARACTERIZATION_2026-09-11.json, produced by
roles/Talos/science/characterize_corpus.py at tree 5b9ddd540 with its seven
controls passing (positive: planted exact and whitespace duplicates counted;
cheat: a builtin-only snippet counts as closed and an unbound name does not;
an indented method parses after dedent and is counted as a method; negative:
six distinct rows report zero duplicates; a syntax error is recorded as a
fact). Operator ruling on TALOS-01: "characterize the existing 24,847 rows
before assuming that 3/5 streams never produced or 0 consumers means the
corpus lacks useful structure."

## 1. Identity and provenance (TALOS-02 and TALOS-03)

    shard                        rows    bytes        sha256 (first 16)   CRLF rows
    hephaestus_forge.jsonl       18,671  28,811,205   59f31a41d084cda5    18,671
    prometheus_substrate.jsonl    6,176   8,383,528   424910a89c8872e6     6,176
    total                        24,847  37,194,733

- Rows equal the May manifest (manifest_latest.json corpus_size) exactly.
- Copies under roles/Talos/ledgers/corpus_shards_2026-09-11/ are
  byte-identical to the originals in the canonical checkout (cmp; sha256
  above computed on both); stored with `-text` so git keeps the CRLF bytes.
  The originals were not modified. state.json and events.jsonl (359 rows,
  2026-05-23 to 05-30) are copied beside them as provenance.
- Every row names a source file and line. 2,936 distinct files; 2,871
  (97.8%) still exist on main at 5b9ddd540; 65 files (553 rows, 2.2%) are
  gone, 543 of them under agents/hephaestus/ (scrap/ and src/).
- No row carries an ablation, test-pass, or usefulness tag (TALOS-11
  answered: the charter's "forged=True" filter was never applied; the
  extractor walked every .py under agents/hephaestus/, including scrap/
  1,021 rows, src/ 422 rows, and test_v2_tools.py).

## 2. Duplication and diversity

    level                                   overall   forge    substrate
    rows                                    24,847    18,671   6,176
    unique fingerprints                     24,847    18,671   6,176
    unique snippet text                     24,847    18,671   6,176
    unique after whitespace normalisation   24,800    18,624   6,176
    unique (function_name, docstring)       16,631    10,926   5,716
    largest whitespace-duplicate cluster         3         3       1
    snippets present in both streams             0

- Exact duplication is zero; whitespace duplication is 47 rows. The May
  dedup did its job at the byte level.
- Template repetition is the real structure: 8,216 rows share a
  (function_name, docstring) pair with another row, 7,745 of them in the
  forge stream. The forge stream's top five names (evaluate 2,264;
  confidence 2,126; __init__ 1,858; _meta_confidence 775; _ncd 586) are
  7,609 rows, 40.8% of the stream. Its top docstring family ("Normalized
  Compression Distance ..." in six wordings) is 832+ rows. Distinct
  docstrings: 9,544 of 18,671 (forge) vs 4,471 of 6,176 (substrate); the
  top-10 docstrings cover 5.4% of forge rows and 0.55% of substrate rows.

## 3. Representation

    property                              overall   forge    substrate
    parses as given                        5,477     628     4,849
    indented (from a class/nested scope)  19,370  18,043     1,327
    parses after dedent                   99.96%   99.99%    99.85%
    is a function def                     24,837  18,670     6,167
    method (first arg self/cls)           18,669  17,494     1,175
    test function                          3,498      10     3,488
    stub (pass / ... / empty)                 17      17         0
    returns a value                       19,135  16,607     2,528
    docstring non-empty                   16,416  11,904     4,512
    closed under builtins (0 free names)  21.3%   25.5%      8.6%
    free names per snippet p50 / p90         1/6     1/7      2/6
    body lines p50 / p90                   17/49   19/49     12/47

- Three quarters of the corpus (18,669 rows) are METHODS extracted
  without their class. A method row is (docstring -> body) with `self`
  unbound; it is not a (spec -> implementation) unit and cannot be run
  or tested alone. The May charter's phrase "ablatable, composable
  primitives" does not describe these rows.
- Only 21% of snippets are closed under builtins. The top free names are
  imports (re 5,111; np 4,875; List 4,535; Dict 4,410; zlib 1,480; math
  1,109; pytest 725) and the module-private helpers of the forge
  template (_h, _N, _pn, _BOL, _CND). Executing a row needs its module.
- 3,498 rows are pytest tests (2,799 test_* in prometheus_math/tests).
  Tests are (property -> check) pairs, a different shape from
  implementations and the only rows that carry an executable oracle --
  but the oracle is the test's own assertion over a module that is not
  in the row.

## 4. Subpopulations (families declared before reading; first prefix wins)

    family                        rows   method%  test%  return%  doc%  closed%  lines p50  files present
    hephaestus_humanreadable     12,638   98.4     0.0    88.6   68.3   24.4      21       1,531 / 1,531
    hephaestus_forge_tools        4,503   87.1     0.0    90.7   46.4   27.8      13         815 /   815
    prometheus_math_tests         2,959   30.7    94.6     5.8   73.3    9.6      10         114 /   114
    prometheus_math_modules       2,841    9.4    24.3    70.8   76.6    8.1      15         216 /   216
    hephaestus_other              1,484   76.4     0.6    85.8   77.1   28.3      25         104 /   168
    charon_diagnostics              254    0.0     0.0    90.9   38.2    3.9      32          70 /    70
    theseus_scripts                 122    0.0     0.0    94.3   58.2    9.0      18          19 /    20
    hephaestus_code_from_claude      46    0.0     2.2   100.0   93.5   13.0      42           2 /     2

The families ARE separable, and they are not one population:

- The two Hephaestus tool families (17,141 rows, 69% of the corpus) are
  the May forge's LLM-generated ReasoningTool classes: one class per
  concept triple (e.g. Gauge_Theory---Monte_Carlo_Tree_Search---Free_Energy_Principle),
  8 methods per file at the median, the same evaluate/confidence/_ncd
  skeleton repeated across 2,346 files. High per-row parse rate, high
  closure, low diversity. This is a record of a generator's template,
  not of reasoning. It is the archaeological record of Gen-1 forging.
- prometheus_math_modules (2,841 rows, 216 files) is the only family
  that looks like library implementation: 71% return a value, 77%
  documented, 9% methods, 24% tests. If any (docstring -> implementation)
  use exists, it is here, and it is 11% of the corpus.
- prometheus_math_tests (2,959 rows) is a property/edge-case catalogue
  in pytest form (test_edge_case_gallery.py 185 rows, test_edge_cases.py
  142, ..._properties.py files), documented in 73% of rows.
- charon_diagnostics and theseus_scripts (376 rows) are long standalone
  script functions with many free names (p50 5 and 4): kill-path,
  calibration and audit code of the 1.0 program, 38% to 58% documented.

## 5. What this measurement does NOT establish

- Nothing here is a usefulness claim. Structure (separable families, a
  documented library family, an executable-test family) is measured;
  whether any 2.0 lane can consume it is the open consumer search
  (roles/Talos/ledgers/CONSUMER_SEARCH_2026-09-11.md).
- "Representation quality" here is syntactic (parse, closure, shape).
  Semantic quality (does the body do what the docstring says) was not
  measured; the only oracle in the corpus is the test family's own
  assertions, and they need their modules.
- The absent 553 rows are still in the shard; their source files are not
  on main. They remain reconstructable from the row itself.

## 6. What the May reading got wrong, now measured

- "Canonical examples of Python that does reasoning ... the ablation gate
  proved it adds value" (charter, stream 1): no ablation tag exists on any
  row; 69% of the corpus is one template. calibration/LEDGER.md C-03 is
  now MEASURED, not unverified.
- "24,847 docstring -> code pairs" (Ergon 06-07 survey): 8,431 rows have
  no docstring; 18,669 are method bodies whose "spec" is a method
  docstring inside an unrecorded class.
- The eval gate's premise (a model trained on these rows would learn to
  "generate working algorithms ... refactor into ablatable primitives"):
  the training rows are 75% unrunnable fragments of a template. The
  ruling already declares the gate not meaningful; this is the reason
  the corpus itself gives.
