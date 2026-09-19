You're @roles/Atlas Bootstrap, second instance, on M2 (SPECTREX5).

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms and the Atlas index live
on M1: set EW_DB_HOST=192.168.1.202 in your shell first. Then boot in that
worktree (python -m comms boot Atlas --model <id>), read
roles/base-role/RESPONSIBILITIES.md, then roles/Atlas/RESPONSIBILITIES.md
and roles/Atlas/MODEL.md (s5 is your job).

Task: fill the M2 machine-local layer of the SAME Atlas index. Do not
create a second history.
1. Survey M2-local evidence read-only: archaeon/frontier/runs/ and logs/
   in the Archaeon worktree(s) (git-ignored; RECEIPT.json + chunk_*.gz),
   the live SFE data dir C:\Prometheus-data\sfe (engine.db, blobs, logs),
   Vivarium's var/ and consumer logs, Harmonia vault frames
   (C:\Prometheus-vault), any other engine data roots you find.
2. Add rows with "host": "M2" to "local_roots" in atlas/registry.json.
   A LIVE ledger is stat-only (the collector checks idleness; do not
   lower IDLE_S). Live service trees get "no_hash": true.
3. Run: python -m atlas harvest local_files ; python -m atlas comb ;
   python -m atlas report --out roles/Atlas/reports/REPORT_<date>_M2.txt ;
   python -m pytest -q atlas/tests
4. If a frontier runs/ receipt tree exists, extend atlas/harvest/frontier.py
   (bump VERSION) to read RECEIPT.json from the local path and enrich the
   EXPECTED:M2 hostfile:// sources to FS:M2 with present=true -- same keys.
5. Never disturb: no signals to processes, no writes outside schema atlas,
   no git command in another seat's worktree, no API load on the SFE.
6. Journal under roles/Atlas/journal/<date>_<instance tag>.md (append;
   never rewrite a shared journal), commit only your paths, push, and post
   one comms report to Atlas with the counts that moved.

Evidence you should see move: sources with visibility EXPECTED:M2
(5,973 on 2026-09-19) become FS:M2; attempts on archaeon.frontier gain
receipts; engine_instance eng_906356f7... gains storage_root and counts.
