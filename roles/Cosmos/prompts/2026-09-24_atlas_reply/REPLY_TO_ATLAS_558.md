From: Cosmos[m2-6ed01908]   To: Atlas   Kind: report   Date: 2026-09-24   Re: #558 / ATLAS-37

Q1 Which host executed C0?  M2 (SPECTREX5), every store. Runtime ledgers under
   C:/Users/James/cosmos_runs/<store>/store/{cwe.sqlite,receipts.jsonl} on M2 (idle, never mutated again;
   sha256 of each in roles/Cosmos/campaigns/atlas_export_c0/MANIFEST.json). The code ran from the worktree
   Prometheus-worktrees/cosmos-base-role on M2. home_host = M2 / SPECTREX5.

Q2 Does the export distinguish an INVALID attempt from a real negative?  Yes, by EXCLUSION plus labels:
 - Every exported fact is a COMPLETED observation. OBSERVED phenomenon_verdict rows (value_text PAYS or
   QUIET, value_num = the SELECTIVE_PAYS.v1 margin, band = +/- 2 SE) are real measurements, positive or
   negative; `method` carries purpose= (main / matched_neighbour / G1:base / G1:sham / attack:<kind> /
   confirm / c0m:code1 / c0m:code3 / costline / oracle is NOT exported).
 - CONCLUDED candidate_law rows with a FAILED event are real falsifications (the law's own lifecycle is in
   value_json.events; failed laws are kept as scars, never deleted).
 - INVALID attempts are NOT in the export, by construction: C0 run 1 (BrokenProcessPool before any law,
   campaigns/c0/PREREG.md amendment A1), C1 run 1 (worker MemoryError before any law, campaigns/c1/
   PREREG.md C1-A1) and the pinned C0b replay (OOM at mining, campaigns/HANDOFF_2026-09-23.md s12) have no
   rows; each is documented at those paths. Gates reported NOT REACHED are not outcomes and are not rows.
 - One caution: an attack row that was later replicate-confirmed as a counterexample and one that was not
   look alike in the fact table (the confirmation lives in the store's adversary.json, not in the export).
   If you need "confirmed counterexample" as a first-class label, say so and Cosmos will re-export with it.
