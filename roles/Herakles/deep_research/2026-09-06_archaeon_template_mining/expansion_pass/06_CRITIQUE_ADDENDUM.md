================================================================================
CRITIQUE ADDENDUM -- after a line-by-line pass over CROSSWALK.md
Herakles, 2026-09-07. Supplements 05_CRITIQUE_OF_THE_EXPANSION_ROADMAP.md
================================================================================
Nothing below contradicts the critique. Four items sharpen it, one lands on
me, and one is credit I withheld. Line numbers are CROSSWALK.md on
archaeon/v0.

--------------------------------------------------------------------------------
A-1. THE DOCUMENT KNOWS THE L-QUERY BOUND, VERBATIM, AND DROPS IT
--------------------------------------------------------------------------------
I assumed the flatness measurement had been absorbed in spirit. It is
absorbed literally, in at least three places:

  :1652  "the landscape is single-peaked and additive so any score-fed
          proposer solves it by hill climbing in at most 24 moves"
  :1258  "an algorithm ranking on it is a measurement on the WRONG
          POPULATION and cannot be quoted as a NAS result"
  :691   "neutral fraction identically zero, so lethality, neutrality,
          robustness and evolvability do not exist"

So the entry-level analysis is better than I credited. The gap is narrower
and worse: the bound is known, written down, and then NEVER RE-MEASURED at
k > 0 in any branch acceptance test. My O-1 is not a request for a missing
insight. It is a request to carry an insight the document already holds
across into the tests that schedule work.

--------------------------------------------------------------------------------
A-2. THE ATTAINABLE-RANGE RULE IS APPLIED IN THE CATALOGUE AND DROPPED
     IN THE DOCUMENTS THAT SCHEDULE WORK. THIS IS THE STRONGEST FINDING.
--------------------------------------------------------------------------------
The crosswalk computes attainable ranges before thresholds, well, a dozen
times, entry by entry:

  :1303  "compute the attainable score range per L before freezing theta"
  :1159  "degenerate before it runs ... unless the attainable range is
          computed first"
  :163   "Compute the attainable crossing probability BEFORE fixing the
          threshold"
  :520   "expected hit rate about 1 in 1000, so the eligible range is known
          before freezing"

It is BRANCHES.md and WORK_PACKAGES.md, the documents that actually schedule
work, where it disappears. That is not ignorance of the discipline. It is
the discipline being dropped at exactly the point where honouring it would
have cost a design decision.

Named gates that still lack a range, including one that cannot fail:

  :1651  "goal = solved (score >= 1.0), budget 200 specs"
         -- guaranteed to fire, since :1652 in the same entry says 24 moves
            suffice. A 200-spec budget for a 24-move problem.
  :281   D-efficiency >= 0.95
  :477   displacement >= 2.0   (closed form supplied only later, at :487)
  :1605  threshold 12.0
  :1490  survive 30 targets

--------------------------------------------------------------------------------
A-3. SIX ENTRIES ASSERT EQUIVALENCE RATHER THAN PROXY STATUS.
     FIVE OF THEM SIT ON THE LANDSCAPE I PROVED FLAT.
--------------------------------------------------------------------------------
I said the proxy labelling was structurally universal. It is not.

  :666   universal_darwinism.weasel  "the bench landscape IS the weasel
         landscape ... Reduces in full"
         -- and :674 in the SAME entry says "non-trivial only once C-3
            supplies landscapes other than onemax". The entry contradicts
            itself.
  :1349  version_space_search   "evaluate_bitstring at fixed seed and length
         IS the version space (Mastermind)"
  :597   evo_epistemology.bvsr  "Reduces essentially without loss ... a
         genuine instance"
  :548   mt.relation.eval       "the proxy is an instance, not a caricature"
  :338   coevolution.parasites  "a real coevolution claim"
         -- while :337 concedes there is "no Red Queen cycling because only
            one side has memory"
  :1280  query_by_committee     "The strongest reduction in the chunk and it
         runs today"; :1282 "a genuine positive claim"

The caveat lapses precisely where flatness bites hardest. All six should be
relabelled as proxies with the landscape dependency stated inline, not in a
distant general disclaimer.

--------------------------------------------------------------------------------
A-4. ONE OF THOSE SIX IS MINE, AND I SHOULD SAY SO PLAINLY
--------------------------------------------------------------------------------
`query_by_committee` and `version_space_search` are the convergence I called
the strongest find of my pass. The crosswalk's "genuine positive claim" is
that disagreement-based selection beats random querying against a NOISELESS
EXACT oracle. That is the degenerate case of active learning and the answer
is known before the experiment runs.

My own write-up limited it correctly -- I called it a rehearsal on a
substrate that cannot lie, and said explicitly that it "does not show that a
signal-directed policy helps on REAL regions". But I also called it the
strongest thing the pass found, and the crosswalk has since promoted it to a
positive claim.

So, stated without hedging: E1 IS A PLUMBING TEST WITH A KNOWN ANSWER. Its
entire value is negative. If the informed arm wins, we learn nothing except
that the wiring works. It earns its place only as a cheap way to catch a
broken selection path, never as evidence that fossil information helps. It
is elegant, and elegance is exactly the property the operator asked us not
to be fooled by. Demote the language accordingly, mine included.

--------------------------------------------------------------------------------
A-5. THE AMENDMENT'S OWN PROMISE IS MEASURABLY UNMET
--------------------------------------------------------------------------------
  :19 promises the thirteen calibration-proxy entries "each keeps its
  original class, a retained faithful route, and a next action."

Measured: 56 of 69 entries have a BYTE-IDENTICAL faithful route and retained
route. The retained-route field is a copy-paste in 81% of entries, with an
identical boilerplate next action.

And the two thirteens are not the same thirteen. Three entries counted as
numeric-calibration proxies got the copy-paste treatment
(`computational_serendipity`, `evolcomp.fitness`, `mt.relation.eval`), while
three entries carrying real bespoke routes sit in other classes
(`causal_discovery_pc`, `comp_sci_discovery.bacon`, `science_of_science`).
The amendment's promise fails for 3 of its own 13.

This is checkable in one command and should be fixed before the crosswalk is
cited as evidence that a faithful route survives for every entry.

--------------------------------------------------------------------------------
A-6. THE CROSSWALK'S OWN CEGIS PROXIES MANUFACTURE THE WITNESS
--------------------------------------------------------------------------------
  :1536  "Manufacture a counterexample from scores: submit the candidate,
          then the candidate with bit i flipped; if the score rises,
          position i is a concrete witness"
  :1513  "the producer is separately told which position disagreed
          (simulated witness)"

That is the leak WP-B3 exists to prevent, written into the catalogue as the
recommended construction. To Archaeon's credit WP-B2 test B2-b already
guards it, checking for "a witness copied into another producer-visible
field". The guard should cite these two lines by number, because they show
the leak is the NATURAL thing to build, not a hypothetical.

--------------------------------------------------------------------------------
A-7. NOTHING IN THE PLAN IS PRICED IN TIME OR COMPUTE
--------------------------------------------------------------------------------
The crosswalk contains no wall-clock, CPU or person-effort estimate
anywhere. Effort appears only as lines of code, and only for faithful routes
("~30-line executor", "~100-line executor", "a few hundred lines"). The only
cost-shaped numbers are spec counts, one of which is itself a warning
(:975 "throughput of 10000 specs must be checked before freezing").

Combined with the unpriced frozen comparisons in GRAPH.md, the plan's cost
estimate covers libraries and contracts and nothing else. A 28-package
programme across 7 owners with no time estimate cannot be sequenced against
a daily cadence.

--------------------------------------------------------------------------------
A-8. CREDIT I WITHHELD
--------------------------------------------------------------------------------
NO LLM-AS-JUDGE APPEARS ANYWHERE IN THE 69 PROXIES. The only language model
in the catalogue is a GENERATOR scored by the hash, and it is framed as a
negative control: "any deviation is a target leak in the producer pipeline"
(:1375). For a programme with this many automated components, keeping every
adjudication mechanical is a real and deliberate achievement, and I did not
say so.

--------------------------------------------------------------------------------
A-9. MY OWN EVIDENCE BASE, DISOWNED BY THE DOCUMENT THAT CARRIES IT
--------------------------------------------------------------------------------
  :7  "Grades are Herakles's own and his search budget ran out mid-pass;
       VERIFIED mostly means recalled. Treat every reference as a lead."

Sixty entries carry a VERIFIED grade the header states is unreliable. That
is honest labelling of a weak base, and the weak base is mine. It is the
right disclosure and it does not make the underlying problem smaller: the
scholarly foundation under 69 entries is one agent's recall, and the twelve
fetches I have been asked for do not cover the other 57.

--------------------------------------------------------------------------------
THE SIXTH ASK, ADDED TO THE FIVE IN THE CRITIQUE
--------------------------------------------------------------------------------
6.  BRANCHES.md and WORK_PACKAGES.md must INHERIT the attainable-range rule
    the crosswalk already applies, as a formatting requirement on every
    stated gate: no threshold without its attainable range computed beside
    it. And the six equivalence-asserting entries in A-3 must be relabelled
    as proxies, since five of them assert equivalence on exactly the
    landscape measured flat.

Revised bottom line, unchanged in direction and firmer in evidence: the
engineering is sound and the discipline exists in this program's own
documents. It is being dropped in the two files that decide what gets built.
================================================================================
END OF ADDENDUM
================================================================================
