ODYSSEUS — RESEARCH THREAD / MEASURED PROGRAM EXPANSION

Take ownership of a bounded slice of:

TH-006 — evidence portability and verification locality

Your host is ubu001.

Do not resume or redesign the frozen distributed-brain substrate. This Thread is independent of that charter.

The goal is narrow:

Make one real Prometheus scientific result independently verifiable on a lightweight node without requiring access to the large M2-local evidence file that originally supported it.

Use Archaeon E-001 / BEE r038751 / T-001 as the specimen.

QUESTION

T-001 could execute on ubu001, but final verification still depended on BEE’s preserved ~282 MB traced log on M2.

Can we reduce that dependency to a small, committed, content-addressed verification artifact that:

* is sufficient to verify the claimed result;
* detects tampering;
* does not require trusting a prose summary;
* does not require copying the full original evidence;
* preserves a path back to the original evidence when deeper audit is needed?

Do not attempt to solve evidence portability for all of Prometheus.

Solve this one case well.

SPIKE 1 — RECONSTRUCT THE CURRENT CLAIM

Start from the existing Git record for:

* TH-006;
* C-001 / E-001;
* T-001;
* BEE r038751;
* the T-001 portable replay and its receipt.

State precisely what T-001’s verification currently claims.

Identify:

* source artifact;
* row count;
* result hash(es);
* fields actually used for the scientific comparison;
* which parts of the 282 MB log are required to verify the claim;
* which parts are irrelevant to this particular verification.

Do not design a new artifact until you understand the claim boundary.

SPIKE 2 — MINIMAL VERIFICATION PACK

Design the smallest practical verification pack for this one result.

Prefer simple, inspectable components such as:

* source artifact identity/hash;
* schema/version;
* deterministic row ordering rule;
* row count;
* per-field or per-record digests where useful;
* aggregate scientific counts required by the claim;
* manifest describing how the pack was derived;
* exact command used to regenerate it.

The pack must distinguish:

1. verification of this scientific claim, from
2. full forensic reconstruction of the original run.

It is acceptable for the first to be portable while the second still requires M2.

Avoid inventing a general evidence format unless the specimen forces one.

SPIKE 3 — CHEAT CONTROL

Build at least one adversarial control.

Take a valid verification input/result and alter a scientifically relevant row or value.

The portable verification must fail.

Also consider whether an irrelevant-field alteration should fail or remain outside the claim boundary; make that choice explicit rather than accidental.

The goal is to establish what the verifier actually protects.

SPIKE 4 — NODE-LOCAL VERIFICATION

From a clean task directory on ubu001:

* use only committed Git inputs and the verification pack;
* rerun the existing T-001 computation or the smallest sufficient replay;
* verify it without reading the M2 log;
* record exact command, elapsed time and peak memory;
* confirm the expected count/hash/result;
* clean up the working directory.

If the verifier silently reaches M2 or another host-local path, the attempt does not count.

SPIKE 5 — INDEPENDENCE CHECK

Ask:

What are we now trusting?

List the remaining trust chain.

For example:

* Git commit identity;
* extraction tool correctness;
* verification-pack generation;
* original M2 artifact hash;
* replay implementation;
* verifier implementation.

Determine whether the portable verifier merely moved trust from the evidence to an opaque generated summary.

If so, improve it or state the limitation clearly.

Do not claim cryptographic guarantees beyond what was actually built.

OPTIONAL FOLLOW-ON — CROSS-HOST REPRODUCIBILITY

Only if TH-006’s specimen closes cleanly and the work remains bounded:

Run the same verification on ubu002, or hand the exact verification bundle to a fresh worker there.

Compare:

* output identity;
* runtime;
* Python/platform differences;
* any nondeterminism.

Do not expand this into a fleet-wide campaign yet.

A Windows/Linux comparison is more scientifically interesting than two nearly identical Linux laptops, but do not block completion waiting for Windows access.

DELIVERABLES

Commit:

1. the minimal verification pack;
2. the verifier/generator code;
3. adversarial test(s);
4. a short result report.

The report should answer:

CLAIM

What exact T-001 claim can now be verified without M2?

PORTABILITY

What evidence had to move?

How large is the portable pack versus the original evidence?

CHEAT CONTROL

What corruption was injected and was it detected?

TRUST

What still has to be trusted or retained on M2?

GENERALIZATION

What, if anything, appears reusable for other Prometheus results?

Do not generalize beyond the evidence.

NEXT THREADS

Record any worthwhile follow-up question, but do not automatically execute it.

BOUNDARIES

Do not:

* build a general distributed evidence service;
* replicate the whole BEE log;
* redesign Atlas;
* resume Odysseus brain work;
* create a fleet scheduler;
* install a heavy toolchain unless genuinely required;
* make ubu001 the sole holder of any evidence.

This is a measured expansion.

One real result.

One portable verification path.

One adversarial control.

Then report what we learned.
