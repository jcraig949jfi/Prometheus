# E-012 -- Frozen-energy lesion: does rcv_str need DYNAMIC aim-energy coupling, or only aim-energy correlation?

Campaign: C-002. Thread: TH-007 (thr-10216c7f001e). Authority: MWO-0004 G4 + operator CWO 2026-09-30 (Aether NEXT after
E-010/E-011). This file is the preregistration. It was committed and pushed BEFORE any E-012 unit ran.

Background: E-010 replaced rcv_str's aim term (energy >> 6) with a static random offset, and the effect vanished (4/128
= rcv level). That lesion removed two things at once: the tick-by-tick tracking of energy, and any correlation between
aim and energy. It also changed the aim distribution. This experiment separates them.

Intervention: law rcv_sfz (aeth03.rcv_sfz.lesion0; code at 1b4fb4523ea7).
- During warm-up it IS rcv_str, bit for bit (tested).
- At the end of warm-up the assay freezes each site's energy into a snapshot, which both twins inherit. From then on,
  the aim term is (snapshot >> 6), not (current energy >> 6).
- Aim therefore stays correlated with where energy was, with the same distribution as rcv_str's at that moment, but
  no longer follows energy.
- Because warm-up is identical, rcv_sfz's post-warm-up world and origin list equal rcv_str's for the same seed. The two
  differ only in the followed ticks. That pairing is tighter than E-010's.

Design:
- rcv_sfz, seeds 4-7, OFF, slice 0:32, n=128, warmup 1500, ticks 400; 4 units, 128 origins.
- Code pinned: 1b4fb4523ea764eefca1c073b75df59f070fda49.
- Comparisons use the E-009 units on the same seeds (rcv 4/128, str 0/128, rcv_str 15/128) and E-010 (rcv_sfx 4/128),
  which are not re-run.
- Regression gate: rcv_str seed 4 re-run at 1b4fb4523ea7 must reproduce E-009's result_sha256 6d56b9b28a07c8ee...
  exactly. This covers the edited assay module as well. Otherwise STOP, report DIVERGED, and make no verdict.

Decision rule, fixed now. S = rcv_sfz P_sust over 128 origins. Components: rcv 4/128, str 0/128.
- **DYNAMIC_COUPLING_NOT_REQUIRED** if S satisfies Block D's N1 against (rcv, str), i.e. S >= 13/128. A static,
  energy-correlated aim is enough; E-010's collapse came from losing the correlation or the distribution, not the
  dynamics.
- **DYNAMIC_COUPLING_REQUIRED** if S <= 6/128 (rcv level + 2). Aim must keep tracking energy as it changes; this is the
  strict reading of "activity re-routing activity".
- **PARTIAL** otherwise (7 to 12 of 128). This is reported as partial, and no further seeds are run because of it.
- Per-seed rcv_str / rcv_sfx / rcv_sfz counts are reported as description only.
- One run. A unit that fails to execute is re-run unchanged. Fabric first; MWO-0004 R3 native fallback if needed.
