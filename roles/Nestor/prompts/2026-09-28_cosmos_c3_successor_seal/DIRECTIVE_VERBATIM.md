NESTOR — COSMOS C3 SUCCESSOR-SEAL DIRECTIVE

You are acting as holdout custodian, not scientific reviewer.

Your task is to make the original Cosmos holdout record durable and create a fresh opaque successor holdout that Cosmos cannot inspect before committing its predictions.

1. Original seal

Merge the original seal into main using a merge commit.

Do not:

* rebase;
* squash;
* rewrite;
* regenerate;
* modify the sealed files;
* change their original hashes.

Preserve the original record exactly.

Once on main, regard its previously hidden world set as exposed. Do not reuse it as the successor holdout.

2. Build a fresh successor seal

Construct a newly drawn hidden world set without consulting:

* Cosmos’s law;
* Cosmos’s current predictions;
* unpublished C3 conclusions;
* anything that would let the hidden set be optimized against the law.

The successor should provide:

* a fresh hidden set;
* a public cryptographic commitment;
* encrypted or otherwise opaque payload;
* a decryption/reveal key that does not reach M2/Cosmos;
* a deterministic runner interface;
* enough provenance to reproduce the draw and verify integrity after reveal.

Do not reveal hidden identities, coordinates, metadata, distributional summaries, or other information that could influence Cosmos’s prediction.

3. Runner protocol

Build the runner so that the ordering is enforced:

1. successor seal already exists;
2. firewall audit passes;
3. Cosmos commits predictions;
4. only then can the designated independent runner obtain what is needed to execute D;
5. result artifacts are preserved without revealing them prematurely to Cosmos;
6. Harmonia can later adjudicate from a complete evidence package.

Include negative tests proving that premature execution/reveal is refused.

4. Coordinate with Odysseus

Odysseus will independently audit the coordinate/firewall layer.

Give Odysseus only what is necessary to audit:

* protocol;
* code;
* synthetic fixtures;
* public commitments;
* firewall behavior.

Do not give Odysseus Cosmos’s law or scientific interpretation.

5. Resource discipline

If substantial compute is required, use the shared lease convention. Queue if busy.

Routine resource contention is not a HITL issue.

6. Deliverable

Return when the successor seal is ready for independent firewall audit.

Report:

* original-seal merge commit;
* successor commitment;
* generation method;
* integrity checks;
* key custody/location;
* runner protocol;
* negative leak tests;
* anything that could have contaminated the holdout.

Do not tell Cosmos anything about the hidden worlds beyond the public commitment and protocol.

Your role ends at trustworthy custody and controlled reveal. Do not assess whether Cosmos’s law is good.
