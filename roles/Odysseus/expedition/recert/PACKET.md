# PACKET -- functional label recertification (state: DRAFT until cold-start tried)

Currency: 2026-09-28. Owner: Odysseus. Read roles/Odysseus/frontier/poi/ready/00_READ_FIRST.md
and roles/Odysseus/expedition/READY_PROTOCOL.md first. Pure ASCII.

Question: for a consequential label L in any engine, does the thing called L
do what L implies? Keep "what we called it then" beside "what it does now".
Inputs (all in git): recert.py (harness), test_known_answers.py +
KNOWN_ANSWERS.json (the fixture), l1_bee_sr.py / l2_npe_p11.py /
l3_bee_solver.py (worked examples), RESULT.md (design, results, limits).
Frozen: recert.py's verdict vocabulary (LABEL_OK, LABEL_CONTEXT_DEPENDENT,
BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM, STRUCTURE_WITHOUT_BEHAVIOUR,
LABEL_PROVENANCE_ONLY) and the known-answer fixture.
May change: new Label specs; new environments; new interventions.
Known-answer fixture: `python3 test_known_answers.py` must reproduce 24/24.
Falsifier of the harness: a planted impostor the harness passes, or a planted
true instance it rejects.
Cold-start task: reproduce 24/24; then write a NEW Label spec for one label
not yet recertified (e.g. BEE SUSTAINED_LINEAGE, an Archaeon "copier" in
ENVGATE-01, or an NPE "runaway"), with its own planted true instance and
impostor, and run it on committed data. Artifacts: RESULT_COLDSTART.md,
the new spec + rows, PACKET_GAPS.md.
