# THESEUS-25: reproducibility of the amended run driver (2026-10-08)

Question: after amendment 1 (sorted coalition pools), is a run determined by
its master seed alone, independent of PYTHONHASHSEED?

Command (branch theseus/loop48-2026-10-08 at 3d85e1df4 = origin/main, code
of amendment 1):
  PYTHONHASHSEED=0   python -m theseus.synth.run_v0 --tag repro_h0   --smoke --workers 4
  PYTHONHASHSEED=777 python -m theseus.synth.run_v0 --tag repro_h777 --smoke --workers 4

Comparison: sha256 over {parentIds, executableRepresentation, state, viable,
generation} for every entity; REPORT.json compared with "compute" removed.

Result: 125/125 entities identical, same id set; REPORT.json identical
except compute timings. PASS.

Limits: smoke configuration (7 generations, per_cell 1, arms of 12), not a
full 30-generation rerun of v0_1; v0 itself (pre-amendment) remains
unreproducible and is recorded as such. Kept: entities and REPORT.json of
both runs (theseus/entities/repro_h*.jsonl, theseus/runs/repro_h*/). All
other files of the two runs were discarded as duplicate scratch.
