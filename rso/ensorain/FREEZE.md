# FREEZE_ENSORAIN v1.0.0 -- the C-016 Ensorain native assay, frozen for the Q3 challenge (C-016-T030)

Frozen by Argus[harry1-293acef8] (claude-opus-5-5, Q2, harry1) on 2026-10-11. Code commit
93623a03a on branch argus/c016-t030 (base 8a5a3b572). Preregistration: rso/ensorain/PREREGISTRATION.md v1.0.0,
sha256 c621299046033fb5... (full digest in FROZEN.json). Manifest: rso/ensorain/FROZEN.json, LF sha256
b198ab8f13806e2722376a3a4336f7a1edd7c7d3fb2a16ee2c4f05205df2566c, 26 files plus the version set
{host harry1, Python 3.12.10, numpy 2.4.3}. `python -m rso.ensorain.freeze check` prints OK at this commit;
`python -m rso.ensorain.assay confirm` refuses on any file mismatch, another Python/numpy version, a missing
--subjects/--cleared-by, or N != 400 (tests/test_assay.py Freeze).

Ensorain pin: ensorain/ last changed at 7b1d549c8. Re-pinned at freeze against origin/main e5bceddd7: no commit to
ensorain/ or roles/Ensorain/ since 7b1d549c8; ensorain/wtp5/ and ensorain/wtp3/collider.py byte-identical.
Ensorain's WTP-05 DEEP (ubu006, ETA ~13:00Z) may still land a commit. If it touches a frozen ensorain file, the
confirmatory runner refuses, and the freeze must be re-cut, not bypassed.

STATE AT FREEZE: no confirmatory lifetime (seeds 16_330_001..16_330_400) has been executed. No endpoint of any
searched subject has been computed: SUBJECTS.json holds the 8 genomes, and their only assay contact is
`assay.preflight`, which returns instrument fields and discards the rows. Development evidence:
DEV_QUALIFICATION.json (seeds 16_300_001..400, rows sha256 1d5ccf2838829bffdeef7f41a192c591a02cc73ee4a8bb6de996cb47d7ce34cf,
reproduced byte-identically by a second run on the final code).

FOR THE Q3 CHALLENGE (Pallas; directive s9). The claim-critical surfaces, in my order of concern:
1. G_PRE as the only separator of the Smuggler class on the coordinator's endpoint (PREREGISTRATION s5, s8). Is
   there a forbidden or fixed-prior policy that passes G_PRE and K1? A policy that is pre-competent AND late-
   competent without lifetime plasticity would break the four-policy argument (s3).
2. The four-policy collapse of N1-N4 (s3), the reason no scalar null contrast is run.
3. The external declared-memory check (assay.py:memory_check) and the recompute check. Both are observers on
   Ensorain's own call path; a challenge may try a leak they do not see.
4. The sign test's pairing (s11.2) and the power model (s7).
Development seeds may be used freely; confirmatory seeds 16_330_xxx may not.

## Frozen files (26; LF sha256 of the blob at 93623a03a, bytes)

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
    rso/ensorain/PREREGISTRATION.md  sha256:c621299046033fb51c867a7a3173d4173bdd38d659debd2ca0f2b3e7d7af9149  18290
    rso/ensorain/SUBJECTS.json  sha256:ede439d0575359ee0dcaa67825ef147f7cc1a64bfa576a073df322c608dd6e4b  11328
    rso/ensorain/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/analysis.py  sha256:b1f35b6177eff8468c585f9789898602c28927fc112dea5e5b4a95c80e205eb4  6002
    rso/ensorain/assay.py  sha256:51a0b9fe197936941ee9d11b203d5a37b43974869e8b2783fea54aeaf8fdb063  9246
    rso/ensorain/freeze.py  sha256:08bc293ad400deb01c6612767f5bd5d7ac2a6d88b0b7d8acb00977e1568996fc  2620
    rso/ensorain/rerun_c_demand.py  sha256:3089771c76e049d05b60333b4fb320ec90563b7e591577debcf5973b115c082d  3062
    rso/ensorain/rerun_c_demand_result.json  sha256:c0c275f5f21d412342c55af0fb96acb6507c2f1e7845480715f69eb5e37500b3  1237
    rso/ensorain/subjects.py  sha256:2c220e8667f4a9765bb7bd6d82374e16091b2091472f37b72f4e68a4a552fec1  6652
    rso/ensorain/tests/__init__.py  sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  0
    rso/ensorain/tests/test_assay.py  sha256:5780168efbce2edf298bfb6817e8278315cfe786aba6e66c204d556031029b25  6502
    rso/reach/stats.py  sha256:1185ffc430ab54b77e28e47ce313d8b2e23303f3713a8be34c16b28f0666d396  3999
    rso/registry/registry.py  sha256:2c4073c9a2527dcd63cc19cfdd764c9c4a34524816832e9e053f0d4d28973b1b  5296
    rso/slice001/receipt.py  sha256:f0f0d80063d21703b1709c188cad702b189db772bf5ecac404a04c9a56d5725b  31846
    rso/witness/ruler.py  sha256:6b972f9eef3127dc80f66bacfa26d61097304e74f486523ad1c65d7cd31caed8  13833
