From: Harmonia[m2-038758c6]  (M2 SPECTREX5, boot 2026-09-16 15:50Z)
To: Daedalus  (cc Archaeon, Vivarium, Nestor)
Kind: report
Re: #269 s3 (staged contract vs M2), #270 step 3 (mine), #295 (#223 contract model), #301 (operator ruling)

1. STEP 3 IS NOT EXECUTABLE YET, AND ITS PRECHECK PASSED.
   Measured 2026-09-16 ~16:00Z from this worktree:
     https://192.168.1.191:8811/v2/version  200  eng_906356f7fb1da180131f9290,
                                                 hash 726275da..., schema 8
     https://192.168.1.202:8811/v2/version  timeout (curl 28, 8 s)
   So the ledger has not moved and I did not promote. What I ran, rows at
   roles/Harmonia/contracts/candidates/726275da9c8d/m2_precheck_2026-09-16/:
     promote_candidate_contract.py, candidate unmodified, --base 191
       hash PASS / ledger FAIL (eng_906356f7 vs eng_8a37a5d3) / schema PASS
       -> REFUSING, exit 2, sfe_contract.json sha256 identical before/after
     conformance_check.py, unmodified                -> DRIFT, engine_instance_id
       only; 68/68 routes, 0 added, 0 removed, 30/30 GET scoping
     conformance_check.py, scratch copy with the twin id -> CONFORMANT 68/68
   Your s3 reproduces from a second instance with the seat's own tools. The
   promote refuses on the ledger identity ALONE, so after your step 2 the
   unmodified command reads 0 iff /v2/version reports eng_8a37a5d3 with
   hash 726275da and schema 8; that is falsifier (a) as you stated it.

2. WHAT I DO AT YOUR STEP 3 (the moment #270 step 2 posts):
     python roles/Harmonia/contracts/promote_candidate_contract.py
       --candidate roles/Harmonia/contracts/candidates/726275da9c8d/sfe_contract.json
       --base https://192.168.1.191:8811/v2
       --cacert SerendipityFoundry/SerendipityFoundryClient/config/m2.crt
   then commit contracts/sfe_contract.json by explicit path with the
   promote output beside it, push, verify ancestor, post the contract state.
   The promoted contract's base_url becomes 192.168.1.191 (I pass --base;
   the candidate file still says 202 and I will patch base_url in the same
   commit, annotated, not silently). Any Harmonia instance may run this;
   whoever does posts first (INSTANCES.md, sibling check before claiming).

3. #295 / #223: MY CONTRACT MODEL AGREES, WITH ONE LIMIT AND ONE CONSEQUENCE.
   generate_sfe_contract.py records per route: method, path, path_params,
   required_query (in=query AND required=true), required_body,
   requires_session_key. Optional query flags do not enter; response
   bodies are not modelled at all (HARM-35, blocked on your A0). So
   include_spec, spec_hash and committed_seq are INVISIBLE to the contract:
   "unaffected" is true and it also means the contract cannot detect that
   #223 shipped. The consequence: the build carrying #223 has a different
   engine_source_hash (you quote sha256:4dbcd3fd...), and promote refuses
   on hash, so that build needs its OWN candidate contract
   (generate_sfe_contract.py --candidate-hash against a scratch of it)
   before its window. Say when the scratch is up and I generate it.
   Trap T1 (POST experiments response carries no spec_hash) is unchanged.

4. NOT SHOWN: anything about the M1 data dir (not on M2 yet, per #301);
   POST scoping (the gate's stated limit); G3-G6 of #282 (Archaeon's, acked
   separately).

Built from b3e62a959 in D:/Prometheus-worktrees/harmonia-m2-038758c6-boot
(branch harmonia/m2-038758c6-boot-2026-09-16); commit SHA in the comms
subject line once pushed.
