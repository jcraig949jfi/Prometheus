"""prometheus.ananke.audit -- PTE audit instruments (the engine side of prometheus.explib).

Promoted from the Ananke Wave-2 harvest (promotion package W2-AE, 2026-10-01). NEW subpackage: nothing frozen
imports it, it edits no recorded semantics, and importing it runs nothing and imports no submodule.

  trace       exact PTE causal tracer: diff_trace / twin_trace / reach_certificate / ProvenanceWorld
              (H-INST pte_trace.py + W2-B's reach-window / decision patch)
  adapter     PTE <-> explib: DiffRecord from a DiffTrace, explib reach certificate, pair tables, zero_comm
              panels, swap_rel intervals, hook provenance records (W2-F adapters/pte.py)
  runner      one eager CPU evaluation path (mirror pairs share physics seeds)
  programs    hand-written plants and adversaries (P-XOR, XOR one-flag readouts, P-FLIP, FLIP_CLOCK, MAJ sum,
              RELAY_LATCH)
  rulers      C1 rulers as explib Ruler measures + proposed rulers (XOR_PIVOT, XOR_SYM, FLIP_FEEDBACK,
              FLIP_B, REACH_BEYOND_HOP_NEAREST) and per-sensor / conditional pivotality (W2-B, W2-J, W2-S)
  certify     PTE families for explib.attainable.certify_family: standard roles, reference worlds (W2-B)
  flip_b      FLIP per-trial decomposition and the B > .75 inference certificate (W2-S)
  ceilings    one API over the light-cone / exact-wake / joint async / Monte-Carlo / epidemic ceilings
              (H-PLANT, W2-T, W2-P, W2-U, W2-J, W2-S)
  guards      runtime invariant guards G0-G12 with W2-O's G12 control exemption (W2-C pte_mut/guards.py)
  kind_audit  citation-kind auditor for documents citing C1 cell ids (W2-I)

Device policy belongs to the caller: functions default to device="cpu"; under a CPU-only brief set
CUDA_VISIBLE_DEVICES=-1 before torch is imported.
"""
