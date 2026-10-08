# Paused for an operator demo on BUCKKEEP (2026-10-08 ~14:42 EDT)

**State:**
- All experiment processes are stopped. Nothing is running; no files are half-written. Each row file is written only
  after its run completes.
- Results kept: everything committed up to this point.
- X-REDISCOVER-SUPPLY: 4 of 12 runs done. The 4 in-flight runs (~30 min in) were discarded; they restart from scratch.

**Resume (after the operator's all-clear), in this order; jobs whose row file exists are skipped:**

    cd roles/Nestor/campaigns/npe-fh48-2026-10-08
    python -B runqueue.py X-REDISCOVER-SUPPLY X-DISTRIB-GAME X-DIR-LONG X-REPUTATION X-ONTAPE-7AE3

Launch it detached: PowerShell `Start-Process python ... -WindowStyle Hidden`.

**Window:** 48 h from 2026-10-08 01:04:48 EDT. The pause downtime counts against the window unless the operator rules
otherwise. Precedent: on 2026-09-25 (Q1), the window was extended by the downtime.
