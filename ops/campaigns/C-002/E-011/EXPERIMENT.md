# E-011 -- Trace lesion: does rcv_add's super-additivity need relay writes that accumulate?

Campaign: C-002. Thread: TH-007 (thr-10216c7f001e). Authority: MWO-0004 G4 + operator CWO 2026-09-30 (Aether rank 2 in
Aether/AETH-03/FOLLOWUP_RANKING_2026-09-30.md). This file is the preregistration. It was committed and pushed BEFORE any
E-011 unit ran.

Claim under test: the E-006 cause probe says rcv_add works by "persistence of activity traces". Under add, a winning
write ADDS to the target (commit = old + incoming), so later writes do not erase an earlier difference. Under rcv, a
site that just received a write emits once (a relay). The hypothesis is that the two compound: relay activity leaves
traces that accumulate and persist.

Intervention: law rcv_adr (aeth03.rcv_adr.lesion0; Aether/observatory/aeth03_variants.py at 0fd9e6ca1196) is rcv_add,
except that a write won by a RELAY (a receipt-activated site that is not itself a WRITE site) commits by REPLACEMENT, as
in rcv. Writes won by WRITE sites still add, as in add. Each mechanism acts on its own writers, but they no longer
compound. With no receipts, rcv_adr equals rcv_add bit for bit (tested).

Design:
- rcv_adr, seeds 4-7 (the E-009 seeds), OFF, slice 0:32, n=128, warmup 1500, ticks 400; 4 units, 128 origins.
- Code pinned: 0fd9e6ca1196986eb7b93316a6abd19de34589af.
- Comparisons use the E-009 units on the same seeds (rcv 4/128, add 1/128, rcv_add 22/128), which are not re-run.
- Regression gate: rcv_add seed 4 re-run at 0fd9e6ca1196 must reproduce E-009's result_sha256 0ac4a1cec53a3c22...
  exactly; otherwise STOP, report DIVERGED, and make no verdict.

Decision rule, fixed now. S = rcv_adr P_sust over 128 origins. Components (seeds 4-7): rcv 4/128, add 1/128.
The lesion keeps BOTH mechanisms active, only without compounding, so its null expectation is ADDITIVE: rcv + add =
5/128. (This differs from E-010's rcv-only threshold, and deliberately so.)
- **TRACE_NOT_REQUIRED** if S satisfies Block D's N1 against (rcv, add): S >= max(0.10, 2 x 4/128) AND S > 5/128, i.e.
  S >= 13/128. Super-additivity survives without compounding relay traces.
- **TRACE_REQUIRED** if S <= 7/128 (additive level + 2 origins). Stopping relay writes from accumulating abolishes the
  effect; the cause probe's mechanism is supported by intervention.
- **PARTIAL** otherwise (8 to 12 of 128). This is reported as partial, and no further seeds are run because of it.
- Per-seed rcv_add vs rcv_adr counts are reported as description only.
- One run. A unit that fails to execute is re-run unchanged. Fabric first; MWO-0004 R3 native fallback if Fabric
  cannot host it.
