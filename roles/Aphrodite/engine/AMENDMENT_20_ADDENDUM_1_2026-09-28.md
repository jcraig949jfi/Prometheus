# AMENDMENT 20 -- ADDENDUM 1 (infrastructure fix; no scientific change)

The first run of the C3 foundry failed on a file-path bug.
  CAUSE: stage_panel imported a19_c2 inside the function. That module's import-time
  settings redirected a18_c1's working directory (C.HERE) to engine/A19_C2/, so the
  panel file was written there.
  FIX: a19_c2 is now imported at module top, before a20 sets C.HERE / C.DATE. No rule,
  seed, threshold or verdict changed.
  Driver sha256 is now 1b705c7dffc07d451cef8d4cbe9e7fd475b678569d656d27cbe62272bb934821
  (was fb0d50ff...).
  CHECK: the deterministic panel stage re-run under the fix gives an IDENTICAL panel:
    SHAM_0 = ({H} + v)
    SHAM_1 = (v - (acc % {H}))
    SHAM_2 = (gcd(|acc|, |{H}|) + v)
    OFF_0  = gcd(|v // {H}|, |v|)
  The stray file in A19_C2 was removed. No C3 outcome existed at the time.
