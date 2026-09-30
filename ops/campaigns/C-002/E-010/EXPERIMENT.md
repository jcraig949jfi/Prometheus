# E-010 -- Steering lesion: does rcv_str's super-additivity need energy-coupled aim?

Campaign: C-002. Thread: TH-007 (thr-10216c7f001e). Authority: MWO-0004 G4 + operator CWO 2026-09-30 (Aether NEXT,
rank 1 in Aether/AETH-03/FOLLOWUP_RANKING_2026-09-30.md). This file is the preregistration. It was committed and pushed
BEFORE any E-010 unit ran.

Claim under test: the E-006 cause probe says rcv_str works by "activity re-routing activity via ENERGY-STEERED AIM". That
claim is observational. This is the first intervention on it.

Intervention: law rcv_sfx (aeth03.rcv_sfx.lesion0; Aether/observatory/aeth03_variants.py at 607fbe65c50d) is rcv_str with
its aim term (energy >> 6) replaced by a static per-site offset in 0..3. The offset comes from a domain-separated hash of
(seed, coordinates), is fixed for the whole run and is identical in both twins. The aim distribution stays roughly
uniform (tested); the coupling between aim and energy dynamics is cut. Everything else is rcv_str.

Design:
- rcv_sfx, seeds 4-7 (the E-009 seeds), arm OFF, slice 0:32, n=128, warmup 1500, ticks 400; 4 units, 128 origins.
- Code pinned: 607fbe65c50d10dd25471d6e8c005072cf269670.
- Comparisons use the E-009 units on the same seeds (rcv 4/128, str 0/128, rcv_str 15/128), which are not re-run.
- Regression gate (runs with the lesion units): rcv_str seed 4 re-run at 607fbe65c50d must reproduce E-009's
  result_sha256 6d56b9b28a07c8ee... exactly. If it does not, the code change altered an existing law: STOP, report
  DIVERGED, and make no lesion verdict.
- Reducer: aeth03_combinations_reduce.py law statistics (P_sust as in Block D), computed over the 4 rcv_sfx units.

Decision rule, fixed now. S = rcv_sfx P_sust over 128 origins. Components (seeds 4-7): rcv 4/128, str 0/128.
- **STEERING_NOT_REQUIRED** if S satisfies Block D's N1 against (rcv, str): S >= max(0.10, 2 x 4/128) AND S > 4/128,
  i.e. S >= 13/128. Super-additivity survives without energy-coupled aim, so the cause probe's mechanism statement is
  wrong or incomplete.
- **STEERING_REQUIRED** if S <= 6/128 (rcv's level + 2 origins). The lesion abolishes the effect; the cause probe's
  mechanism is supported by intervention.
- **PARTIAL** otherwise (7 to 12 of 128). The effect is reduced but not abolished. This is reported as partial, and
  no further seeds are run because of it.
- Per-seed rcv_str vs rcv_sfx counts are reported as description only.
- One run. A unit that fails to execute is re-run unchanged. Fabric first; MWO-0004 R3 native fallback if Fabric
  cannot host it.
