# Delegation, 2026-09-10 — the first controlled cycle in which earlier
# experience changes later solving

Source: the operator's "Chimera review and next delegation brief"
(2026-09-10), committed beside this file as CHIMERA_BRIEF_2026-09-10.md.
Archaeon verified its three corrections before routing them (Appendix A
reproduces exactly: SE(I)/SE(G) = sqrt(6) with equal marginal variances;
exchangeable correlation gives sqrt(2) at every rho tried; sfclient.register()
keeps the token and discards the engine-issued client_id; single-port XOR
injection from an all-zero reset creates at most one live cell, so the
annihilation proof applies).

    TRACK A  close the shared exchange path, then H1 and H0
      Daedalus + Vivarium (Archaeon accounting; Mnemosyne references)
        1 land/reconcile loader + engine/client on ONE development build;
          drop Vivarium's copy of herakles/evca
        2 register() retains the engine-issued client_id; client passes the
          expected-digest read parameter; exercise against the dev engine
        3 one joint receipt: real artifact consumed, reservation/debit/retry
          reconciled with Archaeon's producer receipts (archaeon/producer/
          costs.py: attempt_id + stage), interrupted work, idempotent publish
        4 refreshed CANDIDATE_BUILD.json for the operator (no restart)
      Vivarium + Proteus (Archaeon issues; Harmonia analyses)
        5 cegis_boolean_v1: loop sealed inside the kind; exhaustive over 8;
          NOT = XOR x, ONE
        6 declared source-failure input contract + explicit optional/EMPTY
          component-library input for H0; one solver runtime
        7 H1 alpha three arms (Archaeon issues)
        8 H0 alpha four cells with the permitted small library fixtures
          (Archaeon issues); no synergy claim
    TRACK B  first spatial corpus
      Vivarium lands ca_density_v0 on main and confirms the RUNNING consumer
      has it; Archaeon issues C3 (campaign_c3.py: 150 rows, 600 obs, one
      seed_root -> four shared IC samples); Herakles owns conventions;
      Harmonia declares the paired analysis before issue; operator admits
    TRACK C  finite H5 alpha
      Vivarium wraps eca_rule_eval_v1; Archaeon issues the fixed-decoder
      comparison and computes the exact 4,096 x 12 neighbourhood reference;
      Harmonia scopes
    TRACK D  retention replay
      Archaeon: offline replay on the first complete stream (B or A); Techne:
      pyribs adapter once the stream format exists
    TRACK E  independent substrate and analysis work
      Daedalus NK kind (after A.1-A.4); Harmonia sizing correction + HA-1 +
      X1 + actual-L calibration; Herakles D-18 versioned amendment (alt 1;
      alt 4 corrected); Mnemosyne reconcile D-15 against migration 011;
      Techne land tools; H4 loop later

    CORRECTIONS KEPT LOCAL
      Harmonia   SE(I) = sqrt(2) SE(G) is conditional; estimate both
                 separately on a disjoint pilot; required_blocks() is a
                 precision calculation, label it so; effect threshold is a
                 decision, not derived from noise
      Daedalus/Vivarium  reconcile the two tested configurations (schema-7
                 dev slice vs schema-8 candidate); fix client_id retention
      Herakles   alternative 4 does not conserve live cells from all-zero;
                 alternative 1 remains the D-18 candidate with relaxation AND
                 driven-response measured before the horizon is fixed

    RESOURCE ENVELOPE (host-measured): CPU only; 16 cores; ~12-13 GiB free;
    at most two concurrent research jobs, one thread each, 2 GiB where
    enforceable, 60 s guard, 16 MiB input / 8 MiB trace; one alpha comparison
    <= 10 min. Memory is MEASURED, not enforced; the loader's wall guard is
    between repeats. Heavy tool work uses its own profile.

    OPERATOR DECISIONS (unchanged, not treated as approved): B1 credential;
    B2 v8; admissions; D-6; D-15 reconcile; D-17 (packet says dev-only, no
    export; status file says no campaign use until pinned -- the STRICTER
    stands until the operator says otherwise); D-18; P1; R-1.
