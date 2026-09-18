# HARM-43: independent re-verification of the landed SFE contract (schema 9, build 699ca0f9)

Author: Harmonia[m2-ca1148a0]. Date: 2026-09-18 ~01:20 UTC. Worktree
D:/Prometheus-worktrees/harmonia-m2-ca1148a0-boot at origin/main 80e0822ee
(+ this seat's commits). The contract under test is
roles/Harmonia/contracts/sfe_contract.json as landed by Daedalus[m2-d6ecd70b]
at 2983bd548 (9.0.1; previous landings fbfcfb276 schema 9, a1dd1458c build
4dbcd3fd). Backlog HARM-43 named the a1dd1458c landing; the item now covers
the 9.0.1 landing, which supersedes it (routes identical, 72).

Why this exists: the contract this seat's gate consumes was generated and
landed by the seat that owns the engine (Daedalus), under the operator's
clearance. A contract the audited party wrote is admissible only after the
auditor's gate has been run on it from an independent checkout. This is
that run. Nothing was regenerated; the file is gated as landed.

## Runs (all against https://192.168.1.191:8811/v2, CA m2.crt; outputs beside this file)

    file                                        consumer routes        exit  state
    ------------------------------------------  ---------------------  ----  -----------
    gate_plain.txt                              none                   0     CONFORMANT
    gate_archaeon_routes.txt                    archaeon/conformance   0     CONFORMANT
                                                .py (1 route)
    gate_vivarium_routes.txt                    vivarium/viv/          0     CONFORMANT
                                                conformance.py (30)
    gate_superseded_candidate_726275da.txt      none; the candidate's  2     UNREACHABLE
                                                own base (M1 :8811)          (M1 engine stopped
                                                                             ~09-15; expected)
    gate_superseded_candidate_726275da_vs_m2    none; --base M2        1     DRIFT on
    .txt                                                                     engine_instance_id
                                                                             (eng_906356f7 vs
                                                                             eng_8a37a5d3);
                                                                             hash/schema/4 routes
                                                                             ADDED

    checks on the landed contract, every run: reachable 200; source hash
    sha256:699ca0f9... EXACT; instance eng_906356f7fb1da180131f9290 EXACT;
    schema 9 = 9; science_profile warn; session_enforcement advisory;
    0 routes removed; 72 live = 72 contract, 0 added; session-scoping
    sample 33 GET routes all match.

The DRIFT run is the gate's negative control for this verification: the same
program, on a contract that describes a different ledger, refuses with exit 1
and names the field. A gate that passed both would have measured nothing.

## The candidate's promote conditions versus what landed

    candidates/726275da9c8d/sfe_contract.json pre_deploy.promote_only_when:
      "live /v2/version reports candidate_engine_source_hash
       (sha256:726275da...), the same engine_instance_id (eng_8a37a5d3...,
       M1) and the same schema (8)"
    landed block (sfe_contract.json .landed):
      by Daedalus[m2-d6ecd70b] 2026-09-17, authority operator PRE-CAMPAIGN-4
      REPAIR ORDER s1 (9.0.1); engine hash bc8d3a0c -> 699ca0f9; ledger
      eng_906356f7 (M2); schema 9; receipt SerendipityFoundry/.../deploy/
      RELEASE_9_0_1_2026-09-17/

    none of the three promote conditions was ever met, and none can be now:
    the build that landed is two point releases past the candidate, on a
    different ledger, at a different schema. The candidate was not promoted;
    it was superseded by regeneration under a later operator ruling (SFE on
    M2 on its own ledger, #329). promote_candidate_contract.py was never run
    for it on production (the m2_precheck_2026-09-16/ rows show the precheck
    refusing on ledger, exit 2, nothing written).

Annotation written: candidates/726275da9c8d/SUPERSEDED.md.

## Not done here

- The contract's `landed` block records the generation procedure ("after
  the restart against live + a loopback scratch probe of the same build");
  the scratch-probe scoping derivation was not re-run by this seat (it needs
  a scratch engine of build 699ca0f9; Daedalus's receipt directory carries
  its rows). The gate's session_scoping_sample (33 routes) is the live check
  of the same property and passed.
- HARM-35 (response surface) is unchanged: the gate still cannot see a
  removed response field.
