# Consumer search for the Talos corpus (TALOS-10), opened 2026-09-11

Currency: 2026-09-11 16:05 UTC (4 answers, all NONE; 4 seen without reply; Hephaestus and Kairos, online at asking, have not seen #50 -- OPEN by protocol). Operator ruling on TALOS-01:
"Survey the live 2.0 ecosystem for actual consumers of (spec ->
implementation) pairs or transformations thereof. Ask for concrete
consumption contracts, not expressions of interest. ... IF NO CONSUMER
EXISTS, DO NOT INVENT ONE."

## Protocol (declared before any answer)

- A consumer COUNTS only if its owning seat answers all five contract
  fields (representation; consuming experiment named as a lane item;
  baseline; falsifying observation; additional production) in a
  committed reply posted to Talos. Interest, "could be useful", or a
  Talos-authored fit does not count.
- A NONE is recorded as a result with the seat and message id.
- No reply is recorded as NO_REPLY with the seat's last sync time; it is
  not read as NONE and not read as interest.
- The search closes when every seat that was online in `comms who` at
  the time of asking has replied or has synced twice without replying,
  or when the operator closes it. Then: at least one contract -> the
  matching items in ARCHAEOLOGY are re-premised from that contract
  (ruling step 3); zero contracts -> the six items stay
  CONSUMER-CONTINGENT DORMANT and Talos moves to other backlog work
  (ruling step 4).

## Reading survey (done by Talos, 2026-09-11, tree 5b9ddd540)

Read: roles/Archaeon/H0H5_STATUS.md (iteration 1 table, independent
alphas, decisions pending), archaeon/docs/h0h5/H3_STREAM_FORMAT.md,
roles/*/STATUS.md for every seat with one, and a grep over roles/,
archaeon/docs/ and the SFE tree for fine-tune / LoRA / training corpus /
code corpus / spec->implementation.

- No live lane item on main names a code corpus, code pairs, or a
  fine-tuned model as an input. The matches for those words are all
  historical (Ergon's June LoRA findings and surveys, Agora April, the
  base role's own rule text, Daedalus's sprint packets in an unrelated
  sense).
- Lanes that consume streams or corpora of candidates: H3 (archive
  policies over a candidate stream in Archaeon's v0 format; first real
  stream is C3, 132 rows; a generated 1,024-candidate development stream
  was proposed). The format needs assay_ref, score, descriptors,
  byte_size, replay_ref. The Talos rows have no assay and no score; they
  could carry descriptors and byte_size. Whether an unscored, non-SFE
  stream is admissible is Archaeon's / Techne's to say -- asked.
- Lanes that consume programs: Techne's library-learning tools (Stitch,
  DreamCoder) are pinned as tools, with DreamCoder smoke BLOCKED (DEV-T7).
  No lane item consumes a Python function corpus -- asked.
- Hephaestus 2.0 (mint queue) is the successor of the May forge whose
  17,141 rows dominate the corpus -- asked whether the archaeological
  record of Gen-1 forging has a use in its controls.
- Every other seat: no visible fit; asked to say NONE.

## Asked

- comms #50, 2026-09-11, Talos -> * (question), body
  roles/Talos/prompts/2026-09-11_consumer_search/QUESTION_ALL_SEATS_consumption_contracts.md,
  sha256 cda1e6daad70609f9810fa9a7d5a8a1912d12682200676ef7b726ba752ea49a9.
- Online at the time of asking (`comms who`, 30-minute window):
  Archaeon, Arachne, Nyx, Hephaestus, Kairos (and Talos). Every other
  seat receives #50 at its next sync.

## Answers (one row per seat; empty until they arrive)

    seat        | message id | answer (CONTRACT / NONE / NO_REPLY) | contract summary or reason
    ----------- | ---------- | ----------------------------------- | --------------------------
    Nyx         | #54        | NONE                                | body 447f02e5c roles/Nyx/prompts/2026-09-11_talos10_reply/REPLY_TALOS_contract_NONE.md (sha256 efa2f704...). The Chop Shop consumes machinery as specimens, not function-fragment corpora; items 3 and 4 have no honest answer. One CONDITIONAL READ, not a contract: when NYX-21 (May forge / Hephaestus gauntlet dissection) opens and only if Hephaestus agrees, Nyx would read the hephaestus_* rows as they sit in the ledger as T1-LOCAL provenance evidence. No production required; nothing changes in the corpus. Also noted: DreamCoder's compression organ returned an empty library on Prometheus's real solved corpus, so a large corpus is not automatically a positive abstraction-learning input.
    Eos         | #57        | NONE                                | Eos is BLOCKED on its own re-premise; its lane is external acquisition, not internal corpora.
    Archaeon    | #60        | NONE                                | H0-H5 consume Vivarium candidate streams (rule tables, boolean programs) under sealed specs; a May (spec -> implementation) corpus from a different pipeline has no consumer as they stand; Archaeon will not invent one. THE DOOR (a contract shape, not a contract): H1 beta needs a task family whose later tasks share parts of earlier solutions (Nyx #53: the current H1 split has zero eligible input for the H0 library cells). If the rows show spec->implementation pairs with shared sub-programs on a SMALL BOOLEAN / BIT-VECTOR GRAMMAR, that is a candidate family: fields = (spec as an executable checker, implementation as a program over a declared grammar, both hashable); experiment = H0 four-cell with the library cheat beside it; baseline = same tasks with shared parts removed; falsifier = library-on == library-off on the eligibility count; extra production = none. "Report the characterisation first; nothing else requested." Recorded as NONE; the door is measured, not entered, in TALOS-24 stage D.
    Hermes      | #64        | NONE                                | no contract.
    Coeus       | --         | NO_REPLY (seen #50 11:29 local)     | protocol: not read as NONE, not read as interest
    Polyhymnia  | --         | NO_REPLY (seen #50 11:50 local)     | same
    Arachne     | --         | NO_REPLY (seen #50 11:51 local; online at asking) | same; closing needs a reply or two syncs without one
    Pheme       | --         | NO_REPLY (seen #50 11:52 local)     | same
    Hephaestus  | --         | UNSEEN (no receipt; online at asking, last sync 10:16 local, before #50) | closing condition NOT met
    Kairos      | --         | UNSEEN (no receipt; online at asking, last sync 10:13 local, before #50) | closing condition NOT met
    every other seat | --   | UNSEEN                              | receives #50 at its next sync

## Disposition

OPEN. Six items (ARCHAEOLOGY T02, T05, T06, T07, T09, and T08/T10 as their
dependents) are CONSUMER-CONTINGENT DORMANT per the ruling until this
table closes. Closing condition as of 16:05 UTC: NOT MET (Hephaestus and
Kairos, online at asking, have no receipt for #50; Arachne one sync
without reply). Contracts received: 0 of 4 answers. Operator directive
(2026-09-11, second): silence and adjacent interest are not demand;
Nyx's conditional read stays NONE unless its conditions occur; if the
search closes at zero the negative result is preserved as evidence.
