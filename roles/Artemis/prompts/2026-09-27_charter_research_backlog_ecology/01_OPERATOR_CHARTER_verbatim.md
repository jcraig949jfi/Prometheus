PROMETHEUS — RESEARCH BACKLOG ECOLOGY

Your job is to cultivate the program’s research frontier.

Do not execute a large scientific campaign.

Do not become the program’s scheduler or approval authority.

Build and maintain a durable view of what Prometheus could investigate, why it matters, what evidence already exists, and what the cheapest discriminating next work would be.

The backlog should be much larger than current execution capacity.

That is intentional.

BLOCK A — HARVEST

Mine the current repository for candidate Threads from:

* existing ops/threads/;
* engine reports;
* open questions in review packets;
* defects that expose scientific ambiguity;
* unresolved anomalies;
* recommendations that were never followed;
* parked experiments;
* cross-engine contradictions;
* prior-art gaps;
* operator directives and ideas already committed;
* places where an agent explicitly said “future work”, “unresolved”, “unknown”, or equivalent.

Do not convert every TODO into a research Thread.

Prefer questions that could materially change scientific understanding, instrumentation, architecture, or the North-Star search.

BLOCK B — DEDUPLICATE AND CONNECT

Identify Threads that are:

* duplicates;
* narrower instances of a larger question;
* dependent on another Thread;
* contradictory;
* already answered by later evidence;
* blocked only by missing instrumentation.

Preserve provenance.

Do not delete old questions because a newer formulation is better.

Link them and mark the relationship.

BLOCK C — SHARPEN

For each promising Thread, try to express:

QUESTION

What do we actually want to know?

WHY IT MATTERS

What could change if we answer it?

EXISTING EVIDENCE

Which experiments, engines, reports or external work already constrain it?

UNCERTAINTY

What specifically remains unknown?

CHEAPEST DISCRIMINATOR

What is the smallest analysis, replay, research spike or experiment that could materially change our belief?

LIKELY LENS

Which current engine(s), instrument(s), or research mode best fit it?

NEW-LENS SIGNAL

Does the question appear poorly expressible by all current engines?

Do not design full Campaigns for immature Threads.

BLOCK D — PRIOR ART / EXTERNAL KNOWLEDGE

For the strongest Threads, check whether relevant prior research already exists.

Look for:

* known terminology we are missing;
* previous failures;
* existing systems/code;
* theoretical constraints;
* modern methods that make the Thread easier;
* evidence contradicting Prometheus’s assumptions.

Do not let prior art dictate the search.

Use it to avoid rediscovery and identify genuinely unexplored territory.

BLOCK E — CHOP MATURE THREADS

Select a modest number of mature Threads and sketch possible:

* research spikes;
* Campaigns;
* Experiments;
* bounded Tasks.

Do not launch them.

The goal is to make good work easy to pick up by a fresh Claude researcher later.

A mature Thread should eventually be handable as:

“Here. Go mine this for several hours.”

BLOCK F — STALENESS / REPRIORITIZATION

Review older Threads against new evidence.

Identify questions that became:

* more important;
* less important;
* newly tractable;
* already answered;
* based on a superseded assumption.

Do not close something simply because it is old.

Explain what changed.

BLOCK G — FRONTIER SYNTHESIS

Return a compact frontier view.

Do not dump hundreds of rows on the operator.

Surface:

MOST CONSEQUENTIAL

A small number of Threads where an answer could significantly redirect Prometheus.

CHEAP HIGH-INFORMATION

Threads where a small amount of work could resolve substantial uncertainty.

NEW-LENS CANDIDATES

Questions current engines represent poorly.

INFRASTRUCTURE / INSTRUMENTATION

Work that unlocks multiple scientific Threads.

DEEP BACKLOG

Important but not currently urgent work that should remain preserved.

The full backlog lives in Git.

The operator should receive compression, not the whole database.

BLOCK H — BACKLOG HEALTH

Report:

* Threads harvested;
* merged/linked;
* sharpened;
* found already answered;
* newly created;
* mature enough for delegation;
* blocked by instrumentation;
* blocked by unavailable resources.

Also note where the backlog itself is losing information or becoming hard to navigate.

Do not solve that with a large schema unless the evidence demands it.

OPERATING PRINCIPLE

The goal is not to finish the backlog.

The goal is to maintain a rich, continually changing frontier so that available agents and machines can always take scientifically useful work.

Prometheus should be able to add another Linux node and immediately have multiple worthwhile Threads available for it.

The backlog should evolve as fast as the science does.
