# Salvage assessment: what remains inside Atalanta after the failure asset is lifted

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. The operator's closing question on the ATALANTA-01
ruling: "tell me whether anything uniquely useful remains inside Atalanta
after the failure asset is lifted. If not, recommend clean retirement
rather than inventing a new mission."

Answer up front: NO. Nothing uniquely useful remains as code. Clean
retirement is the recommendation. Two things leave the building with the
seat, and both are already committed elsewhere in this pass.

The test applied to each candidate asset is UNIQUENESS, not quality: does
the program lose a capability it cannot cheaply reconstruct or already
have? A thing that is fine but replaceable is not salvage.

## Asset 1: aggregate_primitive_signals, high-reuse primitive counting

daemon.py:270-299. Named as salvage IP by the June dossier.

VERDICT: NOT UNIQUE. The capability already exists, in better form, inside
the producer.

apollo/scripts/inspect_population.py:69-75 already counts primitive
frequency across a surviving population:

    prim_counts = Counter()
    for org in population:
        for pc in org.primitive_sequence:
            prim_counts[pc.primitive_name] += 1

It is superior to Atalanta's version on three counts, all verifiable at
05b1134e6:

    it reads Apollo's real object model (PrimitiveCall.primitive_name),
      where Atalanta's version assumes primitives are bare strings in a
      JSON list that Apollo does not write;
    it runs against the real checkpoint population rather than against a
      container that has never existed;
    it adds a stratification Atalanta never had -- LLM-derived versus
      non-LLM organisms, lines 77-95 -- which is the comparison anyone
      mining primitive reuse would actually want.

Lifting Atalanta's version would mean importing a worse implementation of
a function the owning seat already maintains.

## Asset 2: the length-2 and length-3 unnamed-composite chain counter

daemon.py:281-285. The only part of asset 1 that Apollo's tool does not
have.

VERDICT: NOT UNIQUE, and its premise is untested.

The code is six lines of standard bigram and trigram counting:

    for i in range(len(seq) - 1):
        composite_counts[(seq[i], seq[i + 1])] += 1
    for i in range(len(seq) - 2):
        composite_counts[(seq[i], seq[i + 1], seq[i + 2])] += 1

That is an idiom, not intellectual property. Anyone who wants it writes it
in the time it takes to read this paragraph, and against the real
container rather than the imagined one.

Its premise is the part worth recording rather than the code: "a composite
chain that keeps being re-derived implies a missing primitive that should
be named and registered." That premise was never tested, at any point, by
anything. It rests on MIN_COMPOSITE_FOR_CANDIDATE = 3, a threshold chosen
before a single organism had been counted, with no attainable range and no
eligible count behind it (calibration ledger L-01, L-02). Lifting the code
would carry the untested premise along with it under the cover of being
"salvaged IP", which is how an unvalidated assumption acquires a
provenance it never earned.

If anyone ever wants the hypothesis, it is one sentence and it is written
here. It should be re-derived and tested, not inherited.

## Asset 3: the Type-E deep-research prompt template

CHARTER.md, with its evidence_organisms requirement and its
anti-gravitational-well clause ("a primitive proposal without organism IDs
in evidence_organisms is the failure mode").

VERDICT: NOT UNIQUE. The doctrine survives independently and in stronger
form.

The anti-gravitational-well clause says: anchor every proposal to concrete
evidence or do not make it. That is base rule 4 (evidence before verdict:
"record the features AND the rows WITH every verdict, and never ship a
verdict whose evidence cannot be independently reconstructed") and base
doctrine's "no LLM adjudicates". Both are constitutional today and neither
depends on this template.

The template's five mandated calibration patterns
(PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND,
PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT,
PATTERN_RANK_PARITY_LEAK) are May-era, were never re-checked against
current doctrine, and were never once cited by an actual report, because
no report was ever produced. Lifting them would be lifting five unaudited
labels.

## Asset 4: the specimen

VERDICT: UNIQUE, AND ALREADY LIFTED. This is the asset the ruling
identified and it is now committed as roles/Atalanta/DEAD_GATING_SPECIMEN.md,
roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md,
roles/Atalanta/PROPOSED_INVARIANT_2026-09-11.md, the executable reference
and controls in roles/Atalanta/reference/, and the raw rows in
roles/Atalanta/ledgers/.

It does not require the daemon to exist. The daemon's remaining value is
as a quotable source of line numbers, which the specimen has already
quoted.

## Asset 5: a resource found today that is NOT Atalanta's and should not leave with it

VERDICT: UNIQUE, NOT ATALANTA'S, HAND IT OVER.

Every May-era agent built on the same template wrote a second recording
channel into `agora.intelligence_outputs` on the canonical store, and
those rows are intact. This seat used them to recover its own lifecycle
after finding no filesystem residue on this host: 354 upstream_not_found
rows, 305 alarm rows, 3 startups, 1 clean shutdown, with per-row
finished_at timestamps that reconstruct a seven-day timeline to the
millisecond.

The table holds 15,495 rows covering the whole May fleet, not just this
agent. For any dead agent whose gitignored artifacts/ and state/ are gone
or stranded on a machine nobody can reach, this is a surviving primary
source. The Necropolis roster lists 48 agents; this seat checked four.

That is agent-archaeology, which is the Necropolis Keeper's lane and
Archaeon's interest, not a mission for a retiring seat to claim. It is
handed over in the report, with the regenerable query script
(roles/Atalanta/ledgers/telemetry_census.py) as the starting point. This
seat does not pursue it.

One caveat that must travel with the handover: `started_at` on these rows
is a module-global session start time, identical across every row of a
session, and is NOT the event time. Only `finished_at` is per-row. A
census built on `started_at` will silently collapse a seven-day run into a
single instant -- this seat's first query did exactly that before
switching fields.

## Recommendation

CLEAN RETIREMENT of the agent. Do not revive the daemon, do not reconnect
it to Apollo, do not lift its code, and do not give the seat a new
mission. The specimen is lifted, the invariant is proposed, the census is
filed, and the telemetry channel is handed to the seats that own
archaeology.

The honest form of the recommendation, since this seat is recommending its
own end and that is a direction in which it could be wrong: Atalanta never
completed one unit of its intended work, and the one durable thing it
produced it produced by failing in an unusually clean and well-instrumented
way. That is a real contribution and it is finished. Keeping the seat open
to look for more would be inventing a mission, which is the specific thing
the ruling forbids.
