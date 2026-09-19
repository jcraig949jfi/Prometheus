# Atlas sources -- where experiment data lives (survey of 2026-09-19)

Currency: 2026-09-19, from four read-only survey passes on M1 (SKULLPORT)
at origin/main 74b09076d. Counts are snapshots; the engines were running.
This is the map the harvesters in atlas/harvest/ are built against. When a
harvester misses something, fix this file first, then the harvester.

## Machines (comms/environments.json; roles/Herakles/journal/2026-09-17.md)

    M1  SKULLPORT  192.168.1.202  canonical Postgres (prometheus_fire), NPE, comms
    M2  SPECTREX5  192.168.1.191  SFE (:8811), Vivarium, Archaeon, PEW service
    M3  GANDALF                   Nyx, Techne, Harmonia F
    M4  (Aphrodite's host; not yet surveyed)

Machine evidence inside artifacts, strongest first: an explicit hostname
field; an instance tag prefix (m1-, m2-, gandalf-); an engine base_url IP;
a worktree/data path drive root (D:\Prometheus-worktrees = M2 in
Archaeon receipts; F:\Prometheus-worktrees and C:\Users\jcrai\lab = M1).

## SFE (Serendipity Foundry Engine) -- driven by Archaeon, Vivarium, Daedalus

- Engine ids: `<prefix>_<24hex>` minted by sfe/ids.py (exp_, obs_, hyp_,
  wld_, wrk_, ...). Engine instance eng_906356f7fb1da180131f9290 (M2).
- Archaeon campaigns on main: archaeon/campaign{1..6}/<EXP>/ with
  PREREG.json/.md, RECEIPT.json (of record), ATTEMPTS.json,
  attempts/aNN/RECEIPT.json, rows.json, RECORD.md, READOUT.md, DESIGN.md,
  addendum.json. Campaign roots: CAMPAIGN_REPORT.md, LEDGER.jsonl
  (friction rows), DECISIONS.md, JOURNAL.md, FUNNEL.json.
  Experiments: SFE-01..10 (cmp1), C2-SFE-NN, C3-SFE-NN, C4-NN, C4-REH-1,
  C5-NN; campaign6 is calibration only so far (G6-0, observatory/).
- CAMPAIGN MEMBERSHIP COMES FROM THE PATH. RECEIPT.campaign is wrong for
  all of cmp3 and some cmp5 ("cmp2", runner reuse); cmp1 receipts carry no
  campaign/attempt/engine fields. campaign_seed: 20260917 cmp1, 20260918
  cmp2, 20260920 cmp3, 20260921 cmp4, 20260922 cmp5.
- Lineage: PREREG.parents[] and PREREG.ancestry (declared);
  ATTEMPTS.json of_record/resumed_from; addendum.json; decisions D5-008
  style; archaeon/campaign4/SUPERSESSION_2026-09-18.md (prose).
- Receipts carry engine.{base_url, engine_instance_id, engine_source_hash},
  workspace.{base_sha, branch, worktree_path, dirty}; no hostname field.
- DEEP FRONTIER (archaeon/frontier/): registry/LINEAGES.jsonl (LIN-xxxxxxxx,
  transformations T*), registry/EVENTS.jsonl (RUN events carry run_ref
  chunks + provenance.run_id/parent_run), queues/*.jsonl, digests/.
  runs/ and logs/ are GITIGNORED and live on M2 only.
- Earlier: archaeon/wse/ledgers/{wse-survey-v01,ssf-c1..3}/.
- Engine storage (local, machine-specific): SQLite engine.db (schema 9)
  + blobs/ + backup/. M2: C:\Prometheus-data\sfe. M1 copies:
  D:/Prometheus-data/sfe/ (engine.db 292 MB, sfengine.log 64 MB),
  F:/Prometheus/SerendipityFoundry/SerendipityFoundryEngine/var/.

## NPE (Nestor Primordial Engine) -- driven by Nestor on M1

- primordial/ is NOT on origin/main. Best ref: LOCAL branch
  nestor/sidequest-graphworld-2026-09-14 (M1 only; origin copy stops at
  b22a09b19, 2026-09-17). Nestor commits to it continuously.
- Rounds r2..r8, lanes A-H,P,Q,R,T,U,W: receipts primordial/ledger/<Lane>.jsonl
  (exp_id, claim, controls, git, lane, tag, status, supersedes, rerun_of,
  parent_*); rows primordial/ledger/rows/<Lane>/<exp_id>.jsonl; QD
  primordial/ledger/qd/cells.jsonl; round summaries
  roles/Nestor/sidequests/graphworld/epochs/ROUND_rN.json.
- CW01 campaign roles/Nestor/campaigns/cw01-2026-09-17/: CAMPAIGN_STATE.json
  (experiments[] e01..e10), experiments/cw01-eNN/{PREREGISTRATION.md,
  WORLD.json, VERDICT_CONTRACT.json, RESULT.json, rows/, RUN_STATUS.json},
  loop/{TRAJECTORIES,PERTURBATIONS,STATE,EVIDENCE}.jsonl, DEFECTS.jsonl,
  experiments/cw01-loopN|arch4/P-xxx/PREREG.json.
- Local off-repo store (M1): C:/Users/jcrai/lab/pm-data (1.2 GB, per-lane
  dirs, epoch-logs/), C:/Users/jcrai/lab/ncu-user (Nsight), run logs
  under the nestor-sidequest-graphworld worktree (git-ignored).

## PEW (Mnemosyne's evidence wiki) -- schema ew on M1 prometheus_fire

- ew.campaign_observations (CO-..., campaign_id cmp1..cmp5, ssf-c1..3,
  wse-survey-v01; harness_id = experiment id; attempt_id; source_commit,
  source_path, reader_version). Reader evidence_wiki/ew/campaign_ingest.py.
- ew.experiments (X-...), claims, evidence; REST on :8377.
- viv.research_experiment_queue (sfe_experiment_id, family_id,
  replication_of, pew_reference) and viv.execution_attempt
  (parent_attempt_id): Vivarium's own queue on M1.
- Connection: evidence_wiki/ew/db.py connect() (identity guard). Atlas
  reads these with SELECT only and records filters, not rows.

## Other runners (engine-agnostic model; not all harvested yet)

Bellerophon toolbox (prometheus/toolbox/, backends local/sfe/npe),
Vivarium (vivarium/viv/), Proteus (proteus/), Herakles EVCA (herakles/),
Ludus worlds/bench (ludus/), Ergon (ergon/), Theophrastus, Aphrodite
benchmark (roles/Aphrodite/science/benchmark/), Harmonia rulers
(roles/Harmonia/science/*_ruler/), alien_circuitry, Techne/Nyx fossils.

## Commit conventions usable by a classifier

Subject prefix `Seat[instance]:` or `Seat-Lane[instance]:`; NPE lane rows
`E[m1-xxxxxxxx]: rows E-R8-...`; `Bellerophon overnight C110:`;
Archaeon `CMP4-03`, `archaeon c5`, `archaeon frontier`; trailers
`Claude-Session:`, `Harmonia-Instance:`. Lineage words in subjects:
PREREG, CORRECTION, AMEND, v2, SUPERSEDED, replica, RETRACT, withdrawn.
