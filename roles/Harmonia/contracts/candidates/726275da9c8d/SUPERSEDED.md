SUPERSEDED 2026-09-18 (Harmonia[m2-ca1148a0], HARM-43).

This candidate (build sha256:726275da..., ledger eng_8a37a5d3 on M1, schema 8)
was staged 2026-09-14 (#256, Harmonia[m2-54a6d694]) for promotion in a
Daedalus deploy window. It was never promoted. The operator re-ruled the SFE
onto M2 on its own ledger (eng_906356f7, #329), and Daedalus regenerated and
landed the contract against the live engine at a1dd1458c (build 4dbcd3fd),
fbfcfb276 (schema 9) and 2983bd548 (9.0.1, build 699ca0f9). None of this
candidate's pre_deploy.promote_only_when conditions was met or can be met.

Gated 2026-09-18 for the record: against its own base (M1 :8811) UNREACHABLE
(exit 2); against the M2 engine DRIFT on engine_instance_id (exit 1). See
roles/Harmonia/contracts/verify_landed_2026-09-18/README.md.

Nothing in this directory is edited; the files stay as staged.
