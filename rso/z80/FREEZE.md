# FREEZE_Z80_ATTRIBUTION v1.0.0 -- the C-017 Z80 Atlas attribution assay (C-017-T030)

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
