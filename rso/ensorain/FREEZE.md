# FREEZE_ENSORAIN v1.1.0 -- the C-016 Ensorain native assay after THE ONE repair round (C-016-T041)

Re-frozen by Argus[harry1-b2f16d20] (claude-opus-5-5, Q2, harry1) on 2026-10-11, branch argus/c016-t041 from base
a387bbb5a. Supersedes FREEZE_ENSORAIN v1.0.0 (code 93623a03a, FROZEN.json b198ab8f; challenged by Pallas in
C-016-T040, rso/ensorain/challenge/REPORT.md). Order of commits on the branch (the amendment precedes the freeze):

    6fff93af9  v1.1.0 code, tests, development check (repair_v110/DEV_CHECK.json)
    030f1746f  PREREGISTRATION.md v1.1.0 (amendment A1-A11) + repair_v110/red_rows.jsonl
    (this)     FROZEN.json v1.1.0 + this file + ONBOARDING.md s5

Preregistration: rso/ensorain/PREREGISTRATION.md v1.1.0 (digest in FROZEN.json). Manifest: rso/ensorain/FROZEN.json
v1.1.0, LF sha256 fcfe67ce98d0ac59ed01cc807af6ecf8c5395bd6055ae4b02a04f4375048c7ab, 34 files plus the version set
{host harry1, Python 3.12.10, numpy 2.4.3}. `python -m rso.ensorain.freeze check` prints OK at this commit;
`python -m rso.ensorain.assay confirm` refuses on any file mismatch, another Python/numpy version, a missing
--subjects/--cleared-by, or N != 400. Of rso/ensorain/challenge/ only the files the assay imports are pinned
(__init__.py, subjects_c.py: the Q-d and Q-e controls); Pallas's report, set and rows stay outside the manifest so
the T042 re-check can write beside them without breaking the freeze (freeze.py CHALLENGE_DEPS).

Ensorain pin: ensorain/ last changed at 7b1d549c8; `git log 7b1d549c8..a387bbb5a -- ensorain/ roles/Ensorain/` is
empty. Ensorain's WTP-05 DEEP (ubu006) may still land a commit. If it touches a frozen ensorain file, the
confirmatory runner refuses, and the freeze must be re-cut, not bypassed.

STATE AT FREEZE: no confirmatory lifetime (seeds 16_330_001..16_330_400) has been executed. No endpoint of any
searched subject has been computed (preflight only). Development evidence for v1.1.0: repair_v110/DEV_CHECK.json
(seeds 16_300_001..400, N = 400, 26,400 rows, rows sha256
b54c751b0796bc58d6dd04f4ddd69deaba879e5f4925757ecf8aab3e85e0f830, rows in DEV_ROWS.jsonl.gz); Q-a..Q-e hold.
Behavioural pins: tests/test_repair_v110.py (14 tests); repair_v110/red_rows.jsonl: baseline GREEN 33/33, and Pallas's
E1 E2 E3 E4 E6 (applied verbatim from challenge/edits.json) and this round's R1-R6 (R3 = P1) each RED on its named
test.

FOR THE T042 RE-CHECK (Pallas, Q3; directive s9 step 7). The repaired surfaces, in my order of concern:
1. The noise arm (assay.py:noise_matched, eta -> 1e-9 on the full arm's draws) as K1's second comparator, and the
   intersection-union p (analysis.py:subject_stats). Is there a non-learner that passes BOTH K1f and K1n?
2. The whole-life `revised` endpoint (analysis.py:revised). Is there a fixed or timer policy that is majority-correct
   on both halves without revising? (noswitch is the descriptive probe; clock_hybrid shows 399/400.)
3. The five witnesses W1-W5 and B1/S5/P3 under the new rule (DEV_CHECK.json has B1 jitter, S5 learns_pre, P3
   innate_zero, B2 innate_max, P2 clock_hybrid at N = 400 on development seeds).
4. G_R5's 9/10 bound and family S from structure (A6, A7).
Development and challenge seeds may be used freely; confirmatory seeds 16_330_xxx may not. There is no second repair
round: a defect found now is narrowed and recorded as a limitation (PREREGISTRATION s11.12).

## Frozen files (34; LF sha256, bytes)

    ensorain/wtp3/collider.py  sha256:7dd701bdf3e0853810ff72a8538feeb6e05050055fb246eb4d0314bc7ec296e5  14756
    ensorain/wtp5/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    ensorain/wtp5/certify.py  sha256:be5a1dd30394c372e9f8877c3cf08322a81b0ca0629e0450b3e3365894ffdad7  5307
    ensorain/wtp5/mutate.py  sha256:b8d6b934b7adae9a29ee527a7b9adeedb6180bc6575bf1eef9d5b9ec6e89c4be  10586
    ensorain/wtp5/nulls.py  sha256:f4a8610ac3eb15df49c9dd38e53b497f7fc84dc5bf2f6527f96cbea901b6c2c5  7044
    ensorain/wtp5/planted.py  sha256:3c09e56a608847cacad11fdaaf1c276661c6eeae36c7c46a2a9d2dc461860386  4694
    ensorain/wtp5/search.py  sha256:559466649974119d13978ce358d65b80c16bc147f5db959b976336c137f5d254  10690
    ensorain/wtp5/tape.py  sha256:6a3243b8273facc1389d53eb757ab8cd434a9b4444c5589a086dbfb5ad391122  14647
    ensorain/wtp5/worlds.py  sha256:73512224a16e5563841c5e6b00a2add0eff6e2660d2418a039868144abdcd71c  11975
    rso/ensorain/COMPATIBILITY.md  sha256:224a30632c99175cd99bad97d1e076322915d2ec516a8897f802ea573e6216fe  16845
    rso/ensorain/DEV_QUALIFICATION.json  sha256:75552067eb4934d70c3180791c8e56aa3a47b0533a349687ee54c1e531b634b9  2600120
    rso/ensorain/PREREGISTRATION.md  sha256:61062bb2bd62f198b48abc1858d50dc1d90c76723d8a811b2db8b73724e63d75  27964
    rso/ensorain/SUBJECTS.json  sha256:ede439d0575359ee0dcaa67825ef147f7cc1a64bfa576a073df322c608dd6e4b  11328
    rso/ensorain/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/analysis.py  sha256:5f8215377a11afe4bdf18596d64c7515d58a7cc2251cb4ce78f19663cd5b5eea  10343
    rso/ensorain/assay.py  sha256:ce3dc25558a98617a6ab813bd7b51c3932e390827fb272b2e0303a518d9ea482  11886
    rso/ensorain/challenge/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/challenge/subjects_c.py  sha256:d9efe4e868931511b99741e1b95f0ee1477dc3851f54ee1ff0e659ec45ffa9c7  4761
    rso/ensorain/freeze.py  sha256:9a3f965e7858d9d7eba7201a3aa79c3fff627b98269dd4c3086755423bf59a62  2932
    rso/ensorain/repair_v110/DEV_CHECK.json  sha256:9ca8ec60bffed1a73770b127782edf3f2e9bb9f08c32f61a36534f1101f774e3  16240
    rso/ensorain/repair_v110/RED_EDITS.json  sha256:76984ac798d6b3a7bc15885304ca244fbd886519802bd5f2075085f7b4454a55  2906
    rso/ensorain/repair_v110/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/repair_v110/dev_check.py  sha256:d965ab299e7c2c0fbe4325e947f6a0558f762c830c2b8494bf3c36e12d6c1b3f  3583
    rso/ensorain/repair_v110/run_red.py  sha256:fe044a641e03750a86632ec1352cfbd58f19121bfd3171e353b21fd23c5dccfd  3763
    rso/ensorain/rerun_c_demand.py  sha256:3089771c76e049d05b60333b4fb320ec90563b7e591577debcf5973b115c082d  3062
    rso/ensorain/rerun_c_demand_result.json  sha256:c0c275f5f21d412342c55af0fb96acb6507c2f1e7845480715f69eb5e37500b3  1237
    rso/ensorain/subjects.py  sha256:2c220e8667f4a9765bb7bd6d82374e16091b2091472f37b72f4e68a4a552fec1  6652
    rso/ensorain/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/tests/test_assay.py  sha256:5780168efbce2edf298bfb6817e8278315cfe786aba6e66c204d556031029b25  6502
    rso/ensorain/tests/test_repair_v110.py  sha256:b2b96f243671c6ee3a833e592d6f13bef39d7eaebeca1e09c906201e521feefb  7509
    rso/reach/stats.py  sha256:1185ffc430ab54b77e28e47ce313d8b2e23303f3713a8be34c16b28f0666d396  3999
    rso/registry/registry.py  sha256:2c4073c9a2527dcd63cc19cfdd764c9c4a34524816832e9e053f0d4d28973b1b  5296
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/witness/ruler.py  sha256:6b972f9eef3127dc80f66bacfa26d61097304e74f486523ad1c65d7cd31caed8  13833
