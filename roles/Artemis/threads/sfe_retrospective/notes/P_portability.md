# P -- Coupling and portability census (evidence for Spikes B/D, report PORTABILITY)

Author: Artemis research assistant, ubu002, 2026-09-27. READ-ONLY pass.
Tree measured: worktree /home/jcraig/Prometheus-worktrees/artemis-base-role at
f287a4fdb (tip of origin/main, 2026-09-27 15:05 UTC), 12,884 tracked .py files
(`git ls-files '*.py' | wc -l`). Aphrodite engine measured from
origin/aphrodite/engine-2026-09-21 at 9490f3f34.
All scripts are in the scratchpad
(/tmp/claude-1000/-home-jcraig-Prometheus/78a7bd7b-da69-4758-859e-8a39e0df5734/scratchpad)
and their source is reproduced in the appendix. Nothing in the repository was
modified; tests ran on a `git archive HEAD <paths> | tar -x` copy in the scratchpad.

## 0. Correction to the brief: this host is NOT stdlib-only

    $ python3 --version                     -> Python 3.14.4
    $ python3 -c 'import numpy;print(numpy.__version__, numpy.__file__)'
      -> 2.3.5 /usr/lib/python3/dist-packages/numpy/__init__.py  (dpkg: python3-numpy)
    $ python3 -m pip --version              -> pip 25.1.1 (python 3.14)
    per-module import probe:
      OK:      numpy scipy torch(2.9.1+debian, cuda.is_available()=False) numba
               psycopg2 requests hypothesis psutil yaml cryptography pytest(9.0.2)
      MISSING: fastapi uvicorn pydantic starlette redis cupy sklearn falkordb
               pytest_timeout
    $ ss -ltn  -> only 22 and 53 listening (no Postgres 5432, no Redis 6379/6390)
    $ nvidia-smi / pwsh / powershell -> not found

So "missing third-party" results below are specifically fastapi/pydantic/uvicorn,
redis, cupy, graphblas, sklearn -- not numpy. No pytest-timeout plugin, so every
run is bounded by `timeout 300`.

## 1. Import graph (python `import`/`from` statements, AST parse; regex fallback
for 215 files that do not parse on 3.14)

Command: `cd <worktree> && python3 -W ignore scratchpad/imports.py coarse`
(fine-grained: `... imports.py fine`). Counts are FILES in the importer
package containing >=1 import of the target. Intra-package edges omitted below.

### 1a. Cross-package adjacency (importer -> imported : files)

    -> SFE (sfe core package)            [SerendipityFoundryEngine/sfe]
       genesis -> sfe : 1  (genesis/harmonia_c/d16c/step9_concurrency.py: sfe.events, sfe.ids)
       prometheus/toolbox -> sfe : 1  (backends/sfe_executor.py: sfe.executors)
       vivarium/viv -> sfe : 1        (viv/executors.py:131 sfe.executors BitStringExecutor, WorkPackage)
       vivarium/tests -> sfe : 1      (test_spec.py:47 sfe.ids.content_hash)
    -> SFE client (sfclient)             [SerendipityFoundryClient/sfclient]
       genesis -> sfclient : 13
       vivarium/viv -> 3 (cli.py, runner.py, preflight.py), vivarium/tools -> 3, vivarium/tests -> 2
       archaeon/campaign1 -> 3, archaeon/campaign2 -> 1, archaeon (fossils_b1.py) -> 1
       SFE/deploy -> 5 (own)
    -> wforge (SerendipityFoundry/worldfoundry/wforge)
       primordial/metric -> 2, primordial/soup -> 2,
       prometheus/toolbox -> 1 (ref/worlds.py:207 `from SerendipityFoundry.worldfoundry.wforge import world, genome`)
    -> viv (vivarium)
       archaeon/producer -> 8, archaeon/tests -> 3, archaeon/campaign4 -> 2, archaeon -> 1
       theophrastus -> 5, techne -> 1, roles/Herakles -> 1, SFE/deploy -> 1
    -> evidence_wiki / ew
       archaeon/producer -> evidence_wiki 11, archaeon/tests -> 6, archaeon -> 2
       comms -> 1 (+ comms/tests 1), atlas -> 1, ludus -> 1, vivarium/viv -> 1,
       agents/arachne -> 1, roles/Atalanta -> 1, integration -> ew 1, proteus/integration -> ew 1
    -> archaeon.*  (fine-grained)
       archaeon.workspace : agents/eos 6, roles/Nemesis 5, roles/Harmonia 4, agents/arachne 2,
          theophrastus 2, and 1 each: agents/alethelia, apollo, aporia, atlas, charon, comms,
          ergon, hephaestus, roles/Arachne, roles/Kairos, roles/Lexis  (16 importer packages)
       archaeon.producer  : SFE/deploy 3, roles/Polyhymnia 3, techne 2, roles/Harmonia 1, roles/Herakles 1
       archaeon.vivqueue  : vivarium 1, vivarium/tests 2
       archaeon.wse       : roles/Nestor 3;  archaeon.campaign4/5: roles/Nestor 1/3
       archaeon.frontier, archaeon.campaign6 : prometheus/toolbox 1 each
       archaeon.detectors/synth/config/calibrate_d3_null : roles/Harmonia
       archaeon.conformance : vivarium/tests 1
    -> comms
       engine 3, vivarium/viv 2, evidence_wiki (ew, integration, ops) 3, atlas 1, ensorain 1,
       archaeon/tests 1, agents/alethelia 1, roles/Arachne 1, roles/Pronoia 1
    -> proteus
       archaeon (campaign1-6, wse, z80atlas, envgate*, frontier, lineage, rie, tests, causal_lens)
         = 83 files total (engine_deps.py), genesis 5, roles/Nestor 5, techne 5,
         vivarium/viv 3, integration 3, nyx 2, engine 1, prometheus/toolbox 1, roles/Harmonia 1
    -> prometheus.toolbox : prometheus/atlas_bee 8 (only external consumer)
    -> prometheus.z80atlas: roles/Bellerophon 24, archaeon/causal_lens 2
    -> prometheus.ananke  : archaeon/causal_lens 4, roles/Ananke 2

### 1b. Per-engine first-party vs third-party imports

Command: `python3 -W ignore scratchpad/engine_deps.py <dirs...>` (files counted once per module).

    engine                      first-party (non-self)                          third-party
    SFE Engine (75 py)          sfclient 8, archaeon 3, viv 1 (all in deploy/)  fastapi 19, pytest 24, uvicorn, starlette, pydantic, psycopg2 1, cryptography 1
    SFE Client (9 py)           --                                              -- (stdlib http.client/ssl only)
    worldfoundry/wforge (26)    --                                              --
    vivarium (99)               sfclient 8, archaeon 4, proteus 4, herakles 3,   psycopg2 11, numpy 4, pytest 48
                                sfe 2, comms 2, evidence_wiki 1
    evidence_wiki (66)          comms 3                                         requests 15, numpy 8, psycopg2 6, fastapi 3, scipy 2, rank_bm25 2,
                                                                                sentence_transformers 2, tensorly 2, pydantic 2, uvicorn 2, sklearn 1
    archaeon (348)              proteus 83, evidence_wiki 19, viv 14, herakles 8, numpy 26, scipy 2, torch 1
                                sfclient 5, prometheus.ananke 4, prometheus.z80atlas 2, comms 1
    comms (10)                  evidence_wiki 2, archaeon 1                     (psycopg2 via ew.db)
    primordial (472)            wforge 4                                        numpy 235, redis 75, torch 22, psutil 20, numba 17, falkordb 7,
                                                                                graphblas 6, scipy 5, cupy 4, cuquantum 2, cutlass_cppgen 1, ncu_report 1
    prometheus/toolbox (62)     archaeon 2, sfe 1, proteus 1, SerendipityFoundry 1   numpy 1, redis 1 (optional, state.py:216 lazy)
    prometheus/z80atlas (20)    --                                              psutil 1
    prometheus/cosmos (62)      --                                              numpy 42, scipy 1
    prometheus/ananke (25)      --                                              numpy 18, torch 7, sklearn 1
    prometheus/atlas_bee (12)   prometheus.toolbox 8                            --
    Aether (115)                --                                              numpy 42, hypothesis 7, cupy 6, yaml 1
    ensorain (114)              comms 1 (lm01/launch_gate.py:33 comms.manifest) numpy 92, psutil 6, scipy 4, sklearn 2
    proteus (140)               herakles 2, ew 1                                hypothesis 2, harmonia_arena 1 (lives outside proteus)
    ludus (47)                  evidence_wiki 1, ergon 1                        requests 2
    atlas (27)                  archaeon 1, evidence_wiki 1, comms 1            psycopg2 1
    genesis (70)                sfclient 13, proteus 5, sfe 1                   numpy 40
    Aphrodite engine (46 py, branch 9490f3f34)  -- (imports only its own modules + stdlib; `git show` loop, see appendix)

### 1c. Which SFE components became general infrastructure

    Consumed by other engines:
      sfclient (stdlib HTTPS client)  -- genesis 13, vivarium 8, archaeon 5 files.
                                         The dominant coupling is REST, not in-process.
      sfe.executors                   -- vivarium/viv/executors.py, prometheus/toolbox/backends/sfe_executor.py
      sfe.ids (content_hash)          -- vivarium/tests/test_spec.py, genesis step9
      sfe.events                      -- genesis step9 only
      wforge (worldfoundry)           -- primordial (4 files), prometheus/toolbox (1)
      SFE REST port 8811 (by URL)     -- `git grep -l ':8811\b'` outside SerendipityFoundry: archaeon/campaign2-5
                                         (99 files, mostly JSON receipts), roles/Harmonia 8, genesis 8,
                                         vivarium/deploy 7, roles/Vivarium 6, roles/Daedalus 6,
                                         evidence_wiki/integration 2, integration 2
      workspace guard PATTERN         -- archaeon/workspace.py is imported by 16 packages AND copied
                                         (not imported) into SFE workspace.py, vivarium/viv/workspace.py,
                                         evidence_wiki/ew/workspace.py, proteus, herakles, crius, techne
                                         (`git ls-files '*workspace.py'`; viv/workspace.py:15 "copied as the
                                         missive instructs rather than reimplemented").
    Consumed by nobody outside SFE (fine-grained import table):
      sfe.api, sfe.runtime, sfe.store, sfe.release, sfe.attestation, sfe.canary, sfe.errors;
      SerendipityFoundry/{D6A,D7,D8,D10,D10phase2,selection_boundary,stackvm_admission,wow,
      worldfoundry/mhc,forensics,incubator}: zero cross-package python imports; only two textual
      path references (ergon/detector_transfer/build2.py, evidence_wiki/benchmarks/build_gold_v2.py;
      `git grep -l -E 'SerendipityFoundry[/\\."](D6A|D7|D8|D10|...)' -- '*.py' ':!SerendipityFoundry'`).
    Newer engines (primordial except wforge, prometheus/z80atlas, cosmos, ananke, Aether,
    ensorain except comms.manifest, Aphrodite) import NOTHING from SFE, viv, PEW or archaeon.

## 2. Host pinning census

Command: `python3 scratchpad/hostpin.py` -- counts FILES (code = .py/.ps1/.cmd/.bat/.sh/.sql;
conf = .json/.jsonl/.toml/.yaml; docs = everything else) matching each pattern.
Cells are code/conf/docs.

    engine                  winpath(A:\)   hostname      192.168.1.x   port 8811/8377/5432/6379/6390  gpu(cuda/cupy)  winsched/pwsh
    SFE Engine              17/ 54/ 15     5/ 3/ 2       15/ 20/ 21    11/ 20/ 18                     0/0/0           9/2/3
    SFE Client               0/  0/  0     1/ 1/ 2        6/  1/  3     6/  1/  3                     0/0/0           0/0/2
    worldfoundry             0/  0/  3     0/0/0          0/0/0         0/0/0                         0/0/0           0/0/0
    vivarium                14/  1/  0     2/ 1/ 0       11/  2/  0     7/  2/  0                     0/0/0          10/0/0
    evidence_wiki            9/ 13/ 74     4/ 5/ 7        8/  3/ 10     6/  6/ 12                     0/0/0           2/1/4
    archaeon                15/171/ 23     1/ 7/10        4/103/  7     2/102/  8                     0/0/0           3/1/3
    comms                    0/  0/  0     2/ 1/ 1        2/  1/  1     0/  0/  0                     0/0/0           0/0/0
    primordial              53/ 38/  5     1/ 2/ 2        0/  0/  0     5/  0/  2                    47/21/4          5/0/0
    prometheus/toolbox       0/  0/  0     0/39/ 0        1/  0/  0     1/  0/  0                     0/0/0           0/0/0
    prometheus/z80atlas      0/0/0         0/0/0          0/0/0         0/0/0                         0/0/0           1/0/0
    prometheus/cosmos        0/0/0         0/0/0          0/0/0         0/0/0                         0/0/0           0/0/0
    prometheus/ananke        0/0/0         0/0/0          0/0/0         0/0/0                         8/0/0           1/0/0
    prometheus/atlas_bee     0/0/0         0/0/0          0/0/0         0/0/0                         0/0/0           0/0/0
    Aether                   5/  0/ 38     0/ 0/ 4        0/0/0         0/0/0                        30/13/28         0/0/1
    ensorain                 0/0/0         0/ 0/ 1        0/0/0         0/0/0                         0/0/0           0/0/0
    proteus                  1/0/0         0/ 1/ 1        0/0/0         1/2/0                         0/0/0           0/0/0
    ludus                    0/2/0         0/0/0          0/0/0         0/0/0                         0/0/0           0/0/0
    atlas                    2/1/0         2/1/0          1/1/0         1/1/0                         0/0/0           0/0/0
    genesis                 21/4/20        0/0/2         15/1/12       10/1/9                         0/0/0           0/0/0
    scripts                 19/0/1         4/0/0         29/0/0         1/0/0                         3/0/0          21/0/1

Notes on what the hits are (spot-checked with `git grep -n` excluding .md/.json/.txt/.jsonl/.log):
  - SFE CORE (sfe/*.py, serve.py, workspace.py, sfclient/) has essentially no host pin:
    serve.py:36 `--port default=8811`; workspace.py:59,103 mention F:/Prometheus in a
    docstring/message only. All SFE pins live in deploy/ (28 py + .cmd/.ps1: sfengine.cmd,
    sfengine_m2.cmd, sfengine_m2_watchdog.ps1, register_sfengine_m2_watchdog.ps1, m1.crt/m2.crt
    minted per bind IP; RUNNING_M1_VS_M2.md: `make_cert.py --ip 192.168.1.191 --prefix m2`).
  - prometheus/toolbox's 39 "hostname" conf hits are 1,419 occurrences of SPECTREX5 inside
    receipt .jsonl files (examples/receipts, playtests/receipts): provenance, not dependency.
  - archaeon's 171 winpath / 103 IP conf hits are campaign receipts (JSON), i.e. recorded
    provenance; its code pins: producer/readback_probe.py:62 default
    `https://192.168.1.202:8811`, producer/exchangeability_table.py SKULLPORT notes.
  - vivarium/config.json (committed defaults): sfe_base_url https://192.168.1.202:8811,
    pew_base_url http://192.168.1.202:8377/api/v1, db_host localhost, machine "M1";
    secrets from VIV_* env or gitignored config.local.json.
    vivarium/viv/deadman.py:239 and deliver.py:276 call `schtasks /Change ... /DISABLE`
    (wrapped in try/except -> returns False off-Windows); resources.py:97 branches on os.name.
  - evidence_wiki/ew/client.py:4 documents EW_SERVICE_URL=http://192.168.1.202:8377;
    ew/db.py:27 EW_DB_HOST default localhost. evidence_wiki/config.json (186a2fa21) commits a
    plaintext db_password, a shared bearer token and four per-machine tokens (values not
    reproduced here) -- also flagged as risk R-D in PEW_STORE_LOCATION_DISPOSITION.md.
  - comms/api.py:31 `MACHINES = {"SKULLPORT": "m1", "SPECTREX5": "m2"}`; api.py:104 points
    EW_DB_HOST at 192.168.1.202; api.py:142 enumerates seats from the roles/ directory.
  - primordial: brain/c*.py hard-code `C:/Users/jcrai/lab/pm-data/C` (53 code files with a
    Windows path); bus/bus.py:48 `redis://127.0.0.1:6390/0`; 47 code files mention cuda/cupy.
  - Aether: runpod/*orchestrate.py and runpod/prometheus_gpu/credentials.py:32 read
    `C:\runpod_key\keys.txt` (env RUNPOD_API_KEY / PROMETHEUS_RUNPOD_KEY_FILE override).
  - scripts/: backup_prometheus.ps1 (F:\, E:\prometheus_backup, C:\Program Files\PostgreSQL\17),
    agora_persist.py / charon_loop.py default 192.168.1.202, charon_loop_launch.bat stale .176.

### Inherent vs located
    INHERENTLY host-dependent (GPU/OS/cloud capability):
      primordial   -- CUDA (torch/cupy/cuquantum/numba/cutlass/ncu), redis 6390 bus, FalkorDB;
                      measured skip reasons: "needs a CUDA device" 4, "needs cuda" 3,
                      "No module named 'warp'" 3, "powershell not available" 3,
                      "archive redis 6394 not reachable" 4, "E9 elites not in pm-data on this host" 2.
      Aether       -- RunPod cloud GPU (cupy); but its test suite runs on CPU (section 4).
      prometheus/ananke -- torch (cuda optional; 8 code files mention cuda).
      Windows schedulers -- SFE deploy/*.ps1 watchdog, vivarium deadman/deliver (schtasks),
                      MONITORS.md registry (53 rows, host column: M1 35, M2 17, M4 10, M3 3,
                      any 5, unknown 3 -- awk over roles/base-role/MONITORS.md rows 14-89).
    MERELY LOCATED (paths/config/IP defaults, overridable by env or config.local):
      SFE core (SQLite file + port flag), sfclient, vivarium (config.json URLs, db_host),
      evidence_wiki (config.json, EW_* env), comms (MACHINES map, EW_DB_HOST),
      archaeon (sfe_base_url default), atlas, genesis (21 code files with Windows paths).
    NO pins at all: prometheus/z80atlas, prometheus/cosmos, prometheus/atlas_bee,
      worldfoundry/wforge, ensorain, Aphrodite engine.

## 3. Service dependencies per engine (runtime-required vs optional)

Evidence: sections 1b/2, the test runs in section 4, and the files cited.

    SFE Engine     REQUIRED: SQLite file (sfe/store.py:1 "one SQLite database (WAL, foreign keys ON)",
                   :29 import sqlite3). For the SERVICE: fastapi+uvicorn+pydantic (pyproject.toml
                   dependencies ["fastapi","uvicorn"]), TLS cert pair. OPTIONAL/ops: Windows
                   Task Scheduler watchdog (deploy/). No Postgres, no GPU. In-process core
                   (runtime/store/events/executors/canary) is stdlib-only.
    SFE Client     REQUIRED: a running SFE REST service (https, :8811) + pinned cert.
    vivarium       REQUIRED: Postgres (schema viv, prometheus_fire; 181 test errors =
                   "connection to server at localhost port 5432 failed"), SFE REST (runner.py:302
                   sfclient), PEW REST (config pew_base_url). comms (Postgres) for park reports.
                   OPTIONAL: schtasks (deadman/deliver, degrade to False).
    evidence_wiki  REQUIRED: Postgres (ew schema), fastapi/uvicorn/pydantic, sentence-transformers
                   +torch CPU, rank_bm25 (requirements.txt 1e0708472: "M2 venv was found without
                   sentence-transformers ... then without rank_bm25 (search 500)"). OPTIONAL:
                   tensorly; SFE verify URL (closure.py:121 EW_SFE_VERIFY_URL).
    archaeon       REQUIRED (producer path): viv queue in Postgres, PEW, SFE REST (readback_probe).
                   Campaign code: proteus (in-process, 83 files). No GPU (torch 1 file).
    comms          REQUIRED: Postgres (comms schema on M1 prometheus_fire); repo layout (roles/ dir).
    atlas          REQUIRED: Postgres (psycopg2, advisory locks across hosts), comms.api.
    primordial     REQUIRED for most lanes: Redis 6390 (bus), GPU for GPU lanes; FalkorDB for one
                   cohort; pm-data directory on C:. CPU subset runs (section 4).
    prometheus/toolbox  none required; Redis optional (state.py:216 lazy import, PK_REDIS_URL,
                   default redis://127.0.0.1:6379/0); SFE executor backend optional.
    prometheus/z80atlas, cosmos, atlas_bee, ensorain(wtp), Aphrodite engine: none (CPU, local files).
    prometheus/ananke  torch; its C1b release gate reads the live comms queue
                   (`python3 -m comms inbox --all --json Ananke`) -> Postgres at run time.
    ensorain/lm01  comms.manifest (in-process hashing only, no DB).
    Aether         RunPod cloud + API key for pod runs; tests need neither.
    ludus          HTTP to Wikipedia/Wikidata (requests), PEW optional.

## 4. Portability test on ubu002 (Linux, CPU, no services)

Method: `git archive HEAD <dirs> | tar -x -C scratchpad/tree` (no .git), then
`scratchpad/runsuites.sh <path>` = `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tree timeout 300
python3 -m pytest -q -p no:cacheprovider --continue-on-collection-errors <path>`.
`rungit.sh` repeats with a READ-ONLY git context (GIT_DIR = this worktree's gitdir,
GIT_INDEX_FILE = a private scratch index built by `git read-tree HEAD`, GIT_OPTIONAL_LOCKS=0)
for tests that shell out to git. No test bound a persistent port (`ss -ltn` unchanged).

    suite                              result                                          classification of non-passes
    SFE Engine tests/                  185 passed, 2 failed, 17 errors, 13 skipped    ALL 19 = "No module named 'fastapi'" (api tests);
                                       (9.2 s)                                         skips: 8 "preregistration commit not in this clone"
                                                                                       (archive copy), 2 "watchdog is a Windows Task
                                                                                       Scheduler script"
    SFE canary smoke                   `python3 -m sfe.canary` -> exit 0,              stdlib+sqlite3 core runs end to end on Linux
                                       all_worlds_ledger_ok true
    prometheus/z80atlas/tests          60 passed (105 s)                               --
    prometheus/toolbox/tests           1426 passed, 1 failed, 7 skipped (41 s)         the 1 = roles/Bellerophon file absent from copy;
                                                                                       re-run with it: 1 passed
    prometheus/ananke/tests            158 passed, 14 failed (no git) ->               remaining 3 need the live comms Postgres queue
                                       with git: test_c1b_run 14 passed, 3 failed
    prometheus/cosmos/tests            TIMEOUT at 300 s after 46 passes, 0 failures    CPU-bound (numpy); not a portability failure
    archaeon z80atlas tests            census 5/5, denovo 5/5, provenance 29 pass     preflight needs `git show c7610ea19:...`;
                                       + 5 skip, preflight 6 pass + 1 error (no git)   with git: 7/7 passed
                                       -> with git 7 passed
    Aphrodite engine tests (branch)    49 passed (27.6 s)                              --
    ensorain/wtp/tests                 7 passed                                        --
    ensorain/lm01/tests                47 passed, 2 failed                             roles/Ensorain/prompts/... absent from copy
    Aether/test (37 files)             TIMEOUT at 300 s after 33 passes, 0 failures;   the 8 cuda/cupy-mentioning files pass on CPU
                                       GPU-marked subset: 481 passed (19 s)
    proteus/tests                      395 passed, 5 failed                            3 "No module named 'harmonia_arena'" (module lives
                                                                                       under integration/, outside proteus); 2 roles/Proteus
                                                                                       files absent
    evidence_wiki/tests                27 passed, 14 skipped, 1 error                  error = fastapi; skips = live service
                                                                                       (EW_LIVE_QUALIFICATION=1) / DB
    comms/tests                        12 passed, 8 failed, 3 errors, 8 skipped        10 = Postgres localhost:5432 refused;
                                                                                       6 = roles/ directory absent
    atlas/tests                        23 passed, 11 failed, 21 skipped               all 11 = roles/Atlas/* files absent
    vivarium/tests                     510 passed, 20 failed, 175 errors, 42 skipped  181 = Postgres 5432 refused; 9 = roles/Harmonia
                                                                                       contracts absent; 6 test_db_identity (DB);
                                                                                       3 workspace_invariant (see below)
    primordial (whole tree)            496 passed, 89 failed, 81 errors, 60 skipped   153 "No module named 'redis'", 10-12 graphblas;
                                       (36 s)                                          skips: CUDA, warp, powershell, redis 6394, pm-data

Genuine OS-portability defect found: vivarium/tests/test_workspace_invariant.py:146 asserts
`session_temporary(Path("F:/Prometheus-worktrees/x")) is False`. On POSIX "F:/..." is a
RELATIVE path, so viv/workspace.py:132 `.resolve()` joins it to the cwd; its truth then
depends on where pytest runs (here cwd was under /tmp -> True). The 2 is_main_worktree
failures are an artefact of my GIT_DIR wrapper, not of the engine.

Reading: once fastapi/redis/Postgres are subtracted, every failure is either (a) a missing
service, (b) a file under roles/ that the test reads (repo-layout coupling: comms, atlas,
vivarium, proteus, ensorain, toolbox, ananke all read roles/<Seat>/...), or (c) git history.
No engine failed for a Windows-only reason except the one F:/ test above. Pure-CPU engines
(z80atlas, toolbox, cosmos, atlas_bee, ensorain/wtp, Aphrodite, SFE core) run as-is on Linux.

## 5. Documented portability efforts and incidents

  - SFE M1 -> M2 fork and relocation.
      a1dd1458c 2026-09-16 "SFE PRODUCTION LAUNCHED on M2 on its own ledger -- build 4dbcd3fd"
        (deploy/LAUNCH_M2_2026-09-16/, incl. sfe_contract.PREVIOUS_m1_5380cb90.json).
      2b21acf76 2026-09-16 "M2 engine relocated under D-23 and back up after a two-day silent
        outage" (deploy/M2_RELOCATE_2026-09-16/).
      4c2fcfbdf 2026-09-12 ledger HDD -> NVMe, "C9 shape 633.8 s -> 20.5 s" (deploy/LEDGER_MOVE_2026-09-12/).
      e556c16ba 2026-09-17 "G1 long run FAILED at 3h27m on the SMR HDD -> production data dir
        moved D: -> C: (NVMe) ... 13.0 s outage" (deploy/LEDGER_TO_NVME_2026-09-17/).
      docs/RUNNING_M1_VS_M2.md (e556c16ba): "The Engine is *forked on purpose*: two engines,
        two substrates"; per-host certs via make_cert.py --ip.
  - PEW / the M2 Postgres fork.
      RUNNING_M1_VS_M2.md ~L162-195: M2 has its own PostgreSQL 17.11 (system_identifier
        7681719240261676752 vs M1 7628127204585430828) holding a restored, WRITABLE copy
        ("not a replica: pg_is_in_recovery() is false"); SUPERSEDED note 2026-09-04: M2 made
        fully independent, "the fork quarantine was undone".
      evidence_wiki/docs/point_release/PEW_STORE_LOCATION_DISPOSITION.md (90b8e6806, 2026-09-17):
        store is PG 17.9 on M1 (SKULLPORT) "a machine that since 2026-09-15 belongs to a
        different ecosystem"; "M2 local cluster ... the 2026-09-04 fork, quarantined, no reader
        since 09-05"; cluster is SHARED (comms: 22 instances on SPECTREX5, 14 on SKULLPORT;
        viv 47 MB, archaeon 4.6 MB, comms 1.7 MB); backup status "UNKNOWN from M2 (no share,
        no shell, 8377/8811 do not answer; 5432 does)"; R-B "MONITORS rows 16-17 are
        UNLOCATED, not ACTIVE".
      evidence_wiki/requirements.txt (1e0708472, 2026-09-16): written after the M2 venv lacked
        sentence-transformers then rank_bm25; "M1 was never pinned".
  - MONITORS registry (roles/base-role/MONITORS.md, last commit cc98596dd 2026-09-26): rows 16
    PEWBackupDaily and 17 PEWRestoreVerifyWeekly (M1) have freshness "unreadable from M2";
    row 27 PrometheusAgentRosterDaily (M4 harry1) "UNLOCATED: no script in the tracked tree
    carries this task name"; row 85 MetisStateProducerUNLOCATED "not M1, not M2".
    States counted: ACTIVE ~13, DORMANT 17, DISABLED 8, DEAD 5, UNLOCATED 5 mentions
    (`grep -oE '\| *(ACTIVE|DORMANT|DEAD|DISABLED|UNLOCATED)...'`). `git grep -l UNLOCATED`
    = 15+ files (34 lines), incl. roles/Archaeon/journal/2026-09-17_m2-49ee5a4d.md.
  - CRLF / manifest.
      comms/manifest.py (8bb162a77, 2026-09-11): hashes LF-normalised bytes "after Diomedes,
        Lexis, Alethelia and Hephaestus reproduced the defect within an hour of the comms
        queue going live"; fixture comms/tests/test_manifest.py (passes on Linux in the run above).
      proteus/.gitattributes (b2ec2d1aa, 2026-09-04): `*.py text eol=lf` after Harmonia hit a
        CRLF hash mismatch (0bf104bb vs published 5059f44c). ama_game/.gitattributes likewise.
      atlas/db.py lf_sha256 normalises CRLF before hashing. There is no repo-root .gitattributes.
  - Canonical-checkout loss: vivarium/viv/workspace.py (105893e2f) "`F:\Prometheus` has twice
    lost ~11,000 tracked files from disk" -> D-23 path-free worktree guard, copied into 7
    packages (section 1c).
  - Vivarium M2 deployment: vivarium/deploy/prepare_m2.py (6bacaa753, 2026-09-17),
    vivarium_consumer_m2.cmd, vivarium_deadman_m2.cmd.

## 6. INCIDENT caused by this census (repaired) -- and a portability finding in itself

The `rungit.sh` wrapper exported GIT_DIR/GIT_WORK_TREE so that tests which read git history
could run on the archive copy. primordial/tests/test_score_receipt_guard.py (and
test_score_close_sweep.py / test_ops_predicate_ref.py) run `git -C <tmp_path> init/config/
add/commit`; `-C` does NOT override an inherited GIT_DIR, so at 2026-09-27 15:49:38 UTC they
wrote to the REAL repository:
  - .git/config (common): added `core.worktree = <scratchpad>/tree` and `[user] name=h,
    email=h@test` (affects every worktree);
  - refs/heads/artemis/sfe-retrospective-2026-09-27 advanced f287a4fdb -> 3fa8054d3
    ("rows", author h <h@test>, tree deleting 52,519 files); never pushed.
  - `git init --bare` failed under GIT_DIR, so test_ops_predicate_ref aborted before its
    `git gc --prune=now` (pack files unchanged: `ls .git/objects/pack`, mtimes pre-date run).
Found by `git status` (52,195 A / 324 D), confirmed with `git reflog`, `git log --all
--author=h@test` (only 3fa8054d3) and `find .git -newermt '2026-09-27 15:20'` (only config,
that ref, its reflog, worktree logs/HEAD, COMMIT_EDITMSG, loose objects). Repaired at ~15:57:
    git --git-dir=/home/jcraig/Prometheus/.git config --unset core.worktree
    git --git-dir=/home/jcraig/Prometheus/.git config --remove-section user
    git --git-dir=/home/jcraig/Prometheus/.git update-ref -m "undo accidental test-harness commit" \
        refs/heads/artemis/sfe-retrospective-2026-09-27 f287a4fdb 3fa8054d3   (compare-and-swap)
Verified after: .git/config has no core.worktree/[user]; worktree HEAD f287a4fdb; `git status`
shows only the pre-existing untracked roles/Artemis/{prompts,threads}; main checkout
/home/jcraig/Prometheus status clean; `git config user.email` -> jcraig@jfi.ai. The dangling
commit 3fa8054d3 remains as an unreachable object (reflog entries record both moves).
Finding: primordial's git-using tests are not hermetic -- they neither clear GIT_* env nor
use `--git-dir`, so run inside any hook/CI/agent context that exports GIT_DIR they mutate
the enclosing repository. Every suite run in section 4 WITHOUT rungit.sh is unaffected.

## Appendix: script sources

### imports.py
```
# import-graph census: python3 imports.py  (run from repo root)
import ast, subprocess, re, collections, sys
files = subprocess.run(['git','ls-files','*.py'],capture_output=True,text=True).stdout.split()
def pkg_of(p):
    parts = p.split('/')
    if parts[0] in ('prometheus','archaeon','SerendipityFoundry','roles','agents') and len(parts) > 2:
        if parts[0]=='SerendipityFoundry' and parts[1]=='SerendipityFoundryEngine' and len(parts)>3:
            return '/'.join(parts[:3])  # e.g. SFE/sfe, SFE/deploy, SFE/tests
        return '/'.join(parts[:2])
    if parts[0] in ('vivarium','evidence_wiki','comms','primordial','proteus') and len(parts)>2:
        return '/'.join(parts[:2])
    return parts[0]
def target(mod):
    m = mod.split('.')
    t = m[0]
    if t == 'sfe': return 'SFE:sfe' + ('.'+m[1] if len(m)>1 else '')
    if t == 'sfclient': return 'SFE:sfclient'
    if t == 'SerendipityFoundry': return 'SerendipityFoundry.' + ('.'.join(m[1:3]))
    if t in ('viv','vivarium'): return 'viv' + ('.'+m[1] if len(m)>1 and t=='viv' else '') if t=='viv' else 'vivarium.'+('.'.join(m[1:2]))
    if t == 'ew': return 'ew' + ('.'+m[1] if len(m)>1 else '')
    if t == 'evidence_wiki': return 'evidence_wiki.' + '.'.join(m[1:3])
    if t == 'archaeon': return 'archaeon' + ('.'+m[1] if len(m)>1 else '')
    if t == 'comms': return 'comms' + ('.'+m[1] if len(m)>1 else '')
    if t == 'proteus': return 'proteus' + ('.'+m[1] if len(m)>1 else '')
    if t == 'wforge': return 'wforge'
    if t == 'prometheus' and len(m)>1: return 'prometheus.'+m[1]
    return None
edges = collections.defaultdict(set); fine = collections.defaultdict(set); bad = 0
for f in files:
    try:
        src = open(f, encoding='utf-8', errors='replace').read()
        tree = ast.parse(src); mods = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import): mods += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                mods.append(n.module); mods += [n.module+'.'+a.name for a in n.names]
    except Exception:
        bad += 1
        mods = re.findall(r'^\s*(?:from|import)\s+([\w\.]+)', src, re.M)
    sp = pkg_of(f)
    for mod in mods:
        t = target(mod)
        if not t: continue
        coarse = t.split('.')[0].split(':')[0]
        fine[(sp, t)].add(f)
        edges[(sp, coarse if not t.startswith('prometheus.') else '.'.join(t.split('.')[:2]))].add(f)
mode = sys.argv[1] if len(sys.argv)>1 else 'coarse'
d = edges if mode=='coarse' else fine
for (s,t),fs in sorted(d.items(), key=lambda kv:(kv[0][1],-len(kv[1]))):
    print(f'{s} -> {t} : {len(fs)}')
print('unparsable(regex fallback):', bad, file=sys.stderr)
```

### engine_deps.py
```
# per-engine first-party and third-party import census (python3 -W ignore engine_deps.py DIR...)
import ast, subprocess, re, sys, collections, os
stdlib = set(sys.stdlib_module_names)
top = set(os.listdir('.'))
firstparty = {d for d in top if os.path.isdir(d)} | {'sfe','sfclient','viv','ew','wforge'}
for d in sys.argv[1:]:
    files = subprocess.run(['git','ls-files','--',d+'/*.py'],capture_output=True,text=True).stdout.split()
    fp = collections.Counter(); tp = collections.Counter()
    selfnames = set(d.split('/'))
    local = {os.path.splitext(os.path.basename(f))[0] for f in files} | {p for f in files for p in f.split('/')[:-1]}
    for f in files:
        src = open(f,encoding='utf-8',errors='replace').read()
        try:
            t = ast.parse(src); mods=[]
            for n in ast.walk(t):
                if isinstance(n,ast.Import): mods += [a.name for a in n.names]
                elif isinstance(n,ast.ImportFrom) and n.level==0 and n.module: mods.append(n.module)
        except Exception:
            mods = re.findall(r'^\s*(?:from|import)\s+([\w\.]+)',src,re.M)
        seen=set()
        for m in mods:
            r = m.split('.')[0]
            key = m if r=='prometheus' and '.' in m else r
            if r=='prometheus': key='prometheus.'+m.split('.')[1] if '.' in m else 'prometheus'
            if key in seen: continue
            seen.add(key)
            if r in stdlib or r=='__future__': continue
            if r in firstparty and not (r in selfnames or key==d.replace('/','.')):
                fp[key]+=1
            elif r in firstparty or r in local: continue
            else: tp[r]+=1
    print(f'== {d} ({len(files)} py)')
    print('  first-party:', dict(fp.most_common()))
    print('  third-party/unresolved:', dict(tp.most_common(25)))
```
(Note: for prometheus/* dirs the self-name filter hides prometheus.* siblings; the
atlas_bee -> toolbox edge comes from imports.py.)

Aphrodite branch import loop:
```
B=origin/aphrodite/engine-2026-09-21; for f in $(git ls-tree -r --name-only $B -- roles/Aphrodite/engine | grep '\.py$'); do git show $B:$f | grep -hE '^\s*(from|import)\s+\w+'; done | sed -E 's/^\s*(from|import)\s+([A-Za-z_0-9]+).*/\2/' | sort | uniq -c | sort -rn
```

### hostpin.py
```
# host-pinning census: counts FILES (not lines) matching each pattern, per engine dir, split code/config/docs
import subprocess, collections, sys
PAT = {
 'winpath': r'\b[A-Za-z]:(\\\\|\\|/)[A-Za-z_.]',
 'hostname': r'\b(SKULLPORT|SPECTREX5|GANDALF|harry1|BUCKKEEP)\b',
 'lan_ip': r'192\.168\.1\.[0-9]+',
 'port': r'(:|port["\x27]?\s*[:=]?\s*)(8811|8377|5432|6379|6390)\b',
 'gpu': r'\b(cuda|cupy|cuquantum|nvidia-smi|nvcc|device=.?gpu)\b',
 'winsched': r'(schtasks|Register-ScheduledTask|Task Scheduler|\bpwsh\b|powershell)',
}
ENG = ['SerendipityFoundry/SerendipityFoundryEngine','SerendipityFoundry/SerendipityFoundryClient','SerendipityFoundry/worldfoundry',
 'vivarium','evidence_wiki','archaeon','comms','primordial','prometheus/toolbox','prometheus/z80atlas','prometheus/cosmos',
 'prometheus/ananke','prometheus/atlas_bee','Aether','ensorain','proteus','ludus','atlas','genesis','ops','infra','scripts','watchers']
CODE = ('.py','.ps1','.cmd','.bat','.sh','.sql','.psm1')
CONF = ('.json','.toml','.yaml','.yml','.ini','.cfg','.env','.jsonl')
def kind(p):
    pl=p.lower()
    if pl.endswith(CODE): return 'code'
    if pl.endswith(CONF): return 'conf'
    return 'docs'
res = collections.defaultdict(lambda: collections.Counter())
for name, pat in PAT.items():
    flags = ['-i'] if name in ('gpu','winsched') else []
    out = subprocess.run(['git','grep','-I','-l','-E',*flags,pat,'--',*ENG],capture_output=True,text=True).stdout.split('\n')
    for p in filter(None,out):
        eng = next(e for e in sorted(ENG,key=len,reverse=True) if p.startswith(e+'/'))
        res[eng][(name,kind(p))]+=1
hdr = 'engine'.ljust(44)+' '.join(f'{n[:8]:>14}' for n in PAT)
print(hdr); print(' '*44+' '.join(f'{"code/conf/doc":>14}' for n in PAT))
for e in ENG:
    row = e.ljust(44)+' '.join(f'{res[e][(n,"code")]:>4}/{res[e][(n,"conf")]:>3}/{res[e][(n,"docs")]:>4}' .rjust(14) for n in PAT)
    print(row)
```

### runsuites.sh / rungit.sh
```
#!/bin/bash
# bounded test-suite portability run on a git-archive copy (no .git) of HEAD f287a4fdb
S=<scratchpad>
cd $S/tree
for p in "$@"; do
  echo "=== $p"
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$S/tree timeout 300 python3 -m pytest -q -p no:cacheprovider --continue-on-collection-errors "$p" > $S/out_$(echo $p|tr / _).log 2>&1
  echo "rc=$?"
  tail -1 $S/out_$(echo $p|tr / _).log
  grep -hoE "No module named '[^']+'" $S/out_$(echo $p|tr / _).log | sort | uniq -c
done

#!/bin/bash   (rungit.sh)
# same as runsuites.sh but with read-only git context: worktree gitdir, private scratch index, no optional locks
export GIT_DIR=/home/jcraig/Prometheus/.git/worktrees/artemis-base-role GIT_WORK_TREE=$S/tree GIT_INDEX_FILE=$S/idx GIT_OPTIONAL_LOCKS=0
exec $S/runsuites.sh "$@"
```
Tree built with: `git archive HEAD SerendipityFoundry/SerendipityFoundryEngine
SerendipityFoundry/SerendipityFoundryClient SerendipityFoundry/worldfoundry prometheus vivarium
evidence_wiki archaeon comms proteus herakles ensorain Aether atlas ludus primordial
roles/Bellerophon/science roles/Ananke | tar -x -C $S/tree`; private index:
`GIT_DIR=<gitdir> GIT_INDEX_FILE=$S/idx git read-tree HEAD`.
