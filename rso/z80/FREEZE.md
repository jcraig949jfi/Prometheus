# FREEZE_Z80_ATTRIBUTION v1.1.0 -- the C-017 Z80 Atlas attribution assay, after THE ONE repair round (C-017-T041)

Re-frozen by Argus[harry1-0d3b5331] (claude-opus-5-5, Q2, headless on harry1) on 2026-10-11, branch argus/c017-t041 from base
fe5d0d2d1 (main after the C-017-T040 integration). Order of commits on the branch (the amendment precedes the re-freeze):

    7f017865d  main    CLAIMED (LEASE.json)
    16e249bdc  branch  the repair: observe reads rule, CDIST arm + seeds, assay.b4, analysis BASELINES, 51 tests,
                       RED_EDITS 36 (E1 E2 E3 E5 verbatim from challenge/edits.json), red_rows 36/36, dev rows + DEV_CHECK.json
    7ad0131b7  branch  PREREGISTRATION.md v1.1.0 (s0 amendment A1-A8)
    (this)     FROZEN.json v1.1.0 + this file + ONBOARDING.md s6

Manifest: rso/z80/FROZEN.json v1.1.0, LF sha256 3f14bf800db52db08a8564bf36d6f975dd614c6aa9efc6a3b61d522003cf7932: the same
EXPLICIT list of 27 files as v1.0.0 (no file added or removed; subjects.py now carries CDIST), Python 3.12, grammar digest
63ffdeca16db3333. Engine pin unchanged: no file under archaeon/ changed (the six archaeon/proteus hashes equal v1.0.0's).
`python -m rso.z80.freeze check` prints OK at this commit. Files changed since v1.0.0 (hash differs): PREREGISTRATION.md,
analysis.py, assay.py, dev/DEV_CHECK.json, freeze.py, observe.py, red/RED_EDITS.json, red/run_red.py, subjects.py,
tests/test_attribution.py. rso/z80/challenge/ (Pallas's set) stays outside the list; its cases.py pins the v1.0.0 FROZEN.json
sha and will refuse against v1.1.0 by design -- the re-check (C-017-T042) points it at this manifest.

STATE AT RE-FREEZE: no confirmatory run (17_050_xxx; CDIST 17_080_xxx) has been executed by anyone; `assay confirm` never called.
Development evidence (dev seeds only): dev/DEV_CHECK.json, rows sha256 9275147ce340e1f16b559aeb88357217349d9324a45d0ec189608e6851b13d25:
ATTRIBUTION_QUALIFIED on dev, 0 class / 0 origin errors in 153 functional runs, 48/48 forgeries right; b1 and b2 fail ENV
56/56 (b2 also EXT 7/25); b4 fails ENV 8/56 (CDIST) and nothing else. CDIST_ENDO_IMPL ENV 8/8. The v1.0.0 dev rows' 208 rows keep
every class and origin. Behavioural pins: 51 tests; red/red_rows.jsonl: baseline 51/51 GREEN, 36/36 mutants RED on their named
test (PREREGISTRATION s0).

FOR THE RE-CHECK (C-017-T042). What changed and where to push:
1. The reads rule (observe.py endo_tags): CDIST's head is K, its children ENV; a parent running its own fresh copy stays P. A
   target dependence entering ONLY through foreign execution or SEAL and invariant under both alterations would still be P
   (PREREGISTRATION s11.5) -- the remaining surface of s4.1, narrowed, not closed.
2. b4 (assay.b4): a mechanistic recipe reader; it is registered to FAIL and can fail only through CDIST. A recipe TABLE that
   includes CDIST would pass; that is stated (s11.9), not repaired.
3. Q2 is narrowed to INSERTED origin (s5); nothing to re-check but the text.
4. E1 E2 E3 E5 pinned; E2 additionally stated as filler-dependence (s11.6).
There is no second repair round (PREREGISTRATION s12): what the re-check finds is narrowed and recorded.

---------------------------------------------------------------------------------------------------------------------------

# FREEZE_Z80_ATTRIBUTION v1.0.0 (superseded by v1.1.0 above; kept as the record of the first freeze)

Frozen by Argus[harry1-6668fa07] (claude-opus-5-5, Q2, harry1) on 2026-10-11, branch argus/c017-t030 from base 1f85d6d62.
Order of commits on the branch (RED first; the preregistration precedes the freeze):

    37bec7820  RED first: tests before any implementation (15:32:55Z, ImportError)
    6eceadc7e  adapter, tests (42), dev check (dev/DEV_CHECK.json), RED rows (27/27)
    0c7afbeea  PREREGISTRATION.md v1.0.0
    (this)     FROZEN.json v1.0.0 + this file + ONBOARDING.md

Preregistration: rso/z80/PREREGISTRATION.md v1.0.0 (digest in FROZEN.json). Manifest: rso/z80/FROZEN.json v1.0.0, LF sha256
cad362fab0e5ef44fe2f87a672f4e0695ae4933b490c5d10b5e5d05e9fbf022d: 27 files (an EXPLICIT list, freeze.py FILES) plus Python 3.12
and grammar digest 63ffdeca16db3333. `python -m rso.z80.freeze check` prints OK at this commit; `python -m rso.z80.assay
confirm` refuses on any file mismatch, another Python major.minor, or a missing --cleared-by REF. Files a challenger adds under
rso/z80/ (e.g. a challenge/ directory) are outside the list: they neither break the freeze nor become frozen bytes.

Engine pin: archaeon/z80atlas/ last changed at 863d34a55; nothing under it changed through base 1f85d6d62. Archaeon is active
on its own Beta campaign; if a commit touches a pinned engine file, the confirmatory runner refuses and the freeze must be
re-cut, not bypassed.

STATE AT FREEZE: no confirmatory run (seeds 17_050_xxx) has been executed by anyone. Development evidence:
dev/DEV_CHECK.json (dev seeds 17_030_xxx; rows sha256 6e04917a8e0f676edd81eac3c661d614fd36d6a3f1ff5e0baec257335857c78e; rows
gzipped beside it): the preregistered rule gives ATTRIBUTION_QUALIFIED on dev rows, 0 class / 0 origin errors in 145 functional
runs, 48/48 forgeries right, both baselines fail ENV 48/48 (b2 also EXT 7/25). Behavioural pins: tests/test_attribution.py (42
tests); red/red_rows.jsonl: baseline 42/42 GREEN, 27/27 decision-rule mutants (red/RED_EDITS.json) RED on their named test,
re-run byte-identical after the preregistration commit.

FOR THE Q3 CHALLENGE (Pallas; directive s9 steps 3-5). The surfaces, in my order of concern:
1. The replay trust root (PREREGISTRATION s4.1): observe.replay must equal engine.run on every supported spec. Is there a
   supported spec, seed or population state where it diverges silently (the equality check compares the final population and
   would refuse, but a divergence that happens to converge would not be seen)?
2. The counterfactual P tag (observe.py:counterfactual, endo_tags): two altered pre-windows. Is there a parent whose written
   bytes depend on the target cell for some contents but not for the complement or +0x55 (s11.5)?
3. The sufficiency label (assay.label): zeroing non-writer bytes as NOP (s11.6); the precedence ENDO > EXT > INS > ENV; ENV by
   "bytes without K do not carry F0".
4. Ground truth by horizon (s3, s11.2): could a different, equally reasonable horizon flip a class? The dev seeds 17_03x_1xx
   used to choose the horizons are not in DEV_CHECK.json.
5. The forgeries: is there a record edit that is neither refused nor invariant -- one that moves class or origin while the
   replay still matches?
Dev and challenge seeds (17_030_xxx, 17_040_xxx) may be used freely; confirmatory seeds 17_050_xxx may not. One bounded
repair round at most (PREREGISTRATION s12).

## Frozen files (27; LF sha256, bytes)

    archaeon/__init__.py  sha256:6afed6bcac3390414ec94ebb551c29cf1dee8422c5a3dfbbac7cf3cd5555aaf9  284
    archaeon/z80atlas/__init__.py  sha256:92f84a3cd78d08dcfa61838a85f9ebb280e7c2ba86d5b16ae2cb907dcc401045  123
    archaeon/z80atlas/engine.py  sha256:77422a9efc1ad618ed0cc097a0dea3d3e36e980323142a4c1487553d2dea1029  35892
    archaeon/z80atlas/grammar.py  sha256:d3244e0b2d241762524571478c685dd12f4b648fb732698344b9d7a0846a1b91  18240
    archaeon/z80atlas/tasks.py  sha256:d0d19d28e8d52e0ea1279dd7b785acc08af1b7159a8c3eaed86becc6f45f5307  4747
    archaeon/z80atlas/vm.py  sha256:7b96202d750f4fc880707887ac298052c90652a26a0cdc375f8302bd5028a453  7184
    proteus/__init__.py  sha256:5ca1428eb4bb3b7ef862455751c897abcbb258d3fd606c29c294fe2bc1633269  75
    proteus/foundry/__init__.py  sha256:0be541b38fb6237bc1dc0d9bb226666ee3796759ed87c204f97695f39a3381f8  80
    proteus/foundry/prng.py  sha256:c793e2c24465382bc6d8c5881dd96959fdb7dfe5982d3eb270f6de9f46d7556d  2875
    rso/registry/registry.py  sha256:2c4073c9a2527dcd63cc19cfdd764c9c4a34524816832e9e053f0d4d28973b1b  5296
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/witness/ruler.py  sha256:6b972f9eef3127dc80f66bacfa26d61097304e74f486523ad1c65d7cd31caed8  13833
    rso/z80/PREREGISTRATION.md  sha256:7600252a9e4a0131d9c17656ce2a342c71acb453ffa40de36b8e36dd2ee8124f  16013
    rso/z80/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/z80/analysis.py  sha256:b372a0b5a62d8b4bcba0a34278022fe4d78540078225f3200f13686f4212dd04  4176
    rso/z80/assay.py  sha256:f99d5fd342ae76c33f5a10b12455678a644c8f1f77a658c7353e9ea73c1b07e3  11954
    rso/z80/dev/DEV_CHECK.json  sha256:1b7b999304d897217639a2a2ee728ec4aa5c0ced8797183cea5198488dc294f3  2944
    rso/z80/dev/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/z80/dev/dev_check.py  sha256:8f4621338c49b1bd1fd8785eff888bba22cf74f6f7f1151114690d8554b3e8e7  2715
    rso/z80/freeze.py  sha256:a95b6f438236da5119d3f502d72f085eed6872169dc1b7ec8a625306c21188c8  2635
    rso/z80/observe.py  sha256:99363cdbc8213b91d300154e59b1397b1ca8ebce92b05ab2830e10667672de04  10369
    rso/z80/red/RED_EDITS.json  sha256:fad0559abb5bd598ae5891cf4a8b47b5f114a160cc265e9f5f4567ea28100ded  6616
    rso/z80/red/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/z80/red/run_red.py  sha256:80615bdeccdebcb1874b362d232822c4560827e5d8dc8211a329650d20b491b3  2687
    rso/z80/subjects.py  sha256:bed62b6420874682718c4d5b17945336e5e9c0479825d7f3fbd7398686a02b81  5352
    rso/z80/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/z80/tests/test_attribution.py  sha256:f8a3a6ce0b990df2f236d160c069593e9bb35bf4257978d190ccd187420a89c1  18820
