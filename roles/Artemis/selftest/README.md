# Artemis self-test: execution log

Frozen test: roles/Artemis/challenge/prospective/PREREG.md (a9d5f5f23),
amendments 1-2. This directory holds the machinery and, as runs finish,
sanitized reports. The run -> thread -> cohort mapping is SECRET until
scoring ends (commit-reveal): its sha256 is below; it is regenerated
deterministically by build_packages.py from the frozen commit.

mapping_sha256 = b10c2672231a1b74548e8c2d039d53b5f460ff2b96e2fb56df9a5b88fe1a8162
runs = 36 (34 in 17 pairs + 2 unpaired B)

Workers: WORKER_TEMPLATE.md (identical for every run). Ledger of
dispatches, workers, leases and contamination: LEDGER.md.
