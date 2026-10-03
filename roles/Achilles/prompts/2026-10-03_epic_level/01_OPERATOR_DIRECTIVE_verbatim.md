Make this adaptation lightly as possible, without overhauling everything:

Yes. I think Epic is the missing level.

The hierarchy then becomes:

\boxed{\text{Epic} \rightarrow \text{Thread} \rightarrow \text{Campaign} \rightarrow \text{Experiment} \rightarrow \text{Task} \rightarrow \text{Attempt}}

That maps much better onto Prometheus than making a Thread carry an entire research phase.

Epic should mean a long-lived strategic program with a scientific objective, boundaries, success/stop conditions, and multiple largely independent workstreams. It is not something an agent claims. It is the operator-level container.

For us:

Epic: Prometheus Phase 3 — Recursive Sagacity Observatory and Developmental Physics of Cognition

Then the RSO buildout is one Thread, not Phase 3 itself.

A reasonable initial shape is:

Level	Example
Epic	Phase 3 — developmental physics / sagacity
Thread	RSO Buildout
Campaign	C-004 — bounded S1–S5 methods slice
Experiment	reset/retention/evidence-binding qualification
Task	implement delayed-message reset fixture
Attempt	a particular model/run executing that task

And Phase 3 can naturally grow other Threads without polluting the RSO engineering graph. I can already see several:

* RSO Buildout — the observatory itself: evidence plane, runtime adapters, qualification, custody, throughput.
* Cognitive Architecture Portfolio — R0/R1/R3/R4/etc., new native architectures, alien mechanisms, architecture fossils.
* Developmental Worlds — W0 calibration, W1 worlds where development may pay, eventually W2/open developmental ecologies.
* Search & Reachability — cold reach vs repair, search operators, scaffold descent, architecture-foundry machinery.
* Sagacity Science — retention → transfer → combination → reuse → developmental improvement, with strong recursion staying unqualified until earned.
* Potentially later Architecture Foundry or Cognitive Ecology can split into their own Threads if they become substantial enough.

The useful semantic distinction is:

A Thread is a durable question/capability. A Campaign is a bounded attempt to advance it.

So RSO Buildout might contain dozens of campaigns over time:

methods slice → native witness → second-physics qualification → W1 support → async support → architecture throughput → production qualification ...

without needing to redefine the Thread every time.

I’d keep Experiment optional for engineering-heavy campaigns. We shouldn’t manufacture an “experiment” just to fit the tree. A scientific campaign may be:

Campaign → Experiment → Tasks → Attempts

while an engineering campaign may legitimately be:

Campaign → Tasks → Attempts.

The graph should permit both.

What belongs on an Epic

Keep it thin. Something like:

* epic_id
* title
* operator objective / North Star
* start date
* status
* governing constraints
* success/exit conditions
* active Thread IDs
* resource envelope/ledger references
* major operator decisions
* deferred/out-of-scope areas

No task leases, implementation details, or scientific receipts directly on the Epic.

I would also make one strong rule:

Evidence rolls upward; authority does not.

An Experiment receipt may support a Campaign conclusion. Several Campaigns may change a Thread’s status. Several Threads may advance Phase 3.

But an Epic being called “Recursive Sagacity” does not allow a child experiment to inherit that interpretation. Claims remain attached to the cell/experiment where they were earned.

That is particularly important for Prometheus.

Structurally I’d expect:

ops/
  epics/
    EP-PHASE3/
      EPIC.json
      README.md
  threads/
    TH-RSO-BUILD/
    TH-ARCHITECTURES/
    TH-WORLDS/
    TH-REACHABILITY/
    TH-SAGACITY/
  campaigns/
    C-004/
    ...

with every Thread carrying epic_id, and every Campaign carrying thread_id.

I would make this a small global workgraph enhancement, not an RSO-specific one. Achilles could add the Epic primitive later with almost no disruption because C-004 and the existing Threads already fit underneath it.

And importantly, don’t hold up Palamedes for it. Phase 3 can be declared as the Epic administratively while Palamedes continues C-004. This is exactly the kind of reversible control-plane improvement that should happen alongside the work rather than stopping it.

So, conceptually:

Phase 3 is the Epic.
The RSO is a Thread.
C-004 is the first Campaign of that Thread.

That feels like the right granularity.
