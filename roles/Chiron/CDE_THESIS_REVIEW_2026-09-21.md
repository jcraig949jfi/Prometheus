# Chiron review of the CDE design thesis (2026-09-21)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Subject: the operator's Engine Five thesis, captured verbatim at
roles/Chiron/prompts/2026-09-21_cde_thesis/CDE_THESIS.md (MANIFEST
beside it).

Status of this file: REVIEW ONLY. The operator's instruction was
"Capture this. Review it. Add your thoughts" and "Do not start on it."
Nothing here authorizes implementation, and no CDE code, world,
controller or run exists.

Pure ASCII by seat convention; the verbatim capture is not ASCII and is
not required to be.

## 1. Verdict

The thesis is strong where most engine proposals are weak: it states
what would make the engine unnecessary (s19), it treats its own
inductive bias as a treatment rather than an embarrassment (s14), and
it commits in advance to the ablation that could kill its headline
result (s4 of the ladder: "if competence does not collapse, it was not
causally responsible"). Those three things are worth more than the
synthesis of Voyager/SIMA/Genie, which is the part that will get
quoted.

It is weak in one specific and fixable way: its central question is not
yet measurable. "Does retained reusable competence causally expand the
set of experiences an organism can subsequently reach?" contains an
undefined term -- reachable -- and Prometheus has already paid for that
class of omission inside this repository, twice, in the seat whose
charter was almost the same sentence.

The two findings below are the reason this review exists rather than a
nod of agreement.

## 2. The in-house prior art the thesis does not cite: Crius C0-C2

The thesis raids DeepMind and does not raid Prometheus. The closest
prior work to CDE is not Voyager. It is Crius, three doors down, whose
operator charter was:

    "put players into a world and see if we can create a fitness
    function where they are rewarded for learning to learn."

Crius built an isolated sandbox in which Players had a Workspace with
persistent, addressable, executable state -- blocks, records, an
instruction set that could create, write, read and invoke them. That is
CDE's affordance thesis in miniature. Crius ran four preregistered
campaigns and the result was NO, four times, for four different
mechanical reasons (roles/Crius/STATUS.md, and the receipts it cites):

- C0: the assay was valid -- the POSITIVE CONTROL showed reuse_gain
  +3988/+3674 and the controls dissociated -- and search still found no
  learning-to-learn. The frozen metric turned out to order quitting
  (3.00) above genuine reuse (2.97), because a ratio of gained
  competence to spent budget rewards abstention.
- C1: nine runs, three arms. The winners were stride-counter random
  walkers with zero acquired-state effect.
- C1b: with the walkers suppressed, no reproducible ACC > FRESH, no
  block ever invoked, no ancestral gradient. The frozen C1 family was
  CLOSED.
- C2: rungs A and B showed no gradient; the rung C gate FAILED against
  the bytecode control and C/D were never searched.

The single most transferable line is in Crius's calibration ledger,
prediction R3: it expected useful invocations in more than 5 percent of
rung-B candidates and measured 2 to 126 of 7208 -- under 2 percent. The
correction reads:

    "creation being one edit does not make invocation one edit; count
    them separately in the next preregistration"

That is the warning CDE must answer. CDE's entire premise is that MORE
affordance helps. Crius measured that affordance PRESENCE is not
affordance USE, that the edit-distance to useful invocation is the
quantity that matters, and that a well-built instrument will happily
report a clean null while organisms exploit the substrate instead
(compressed enumerators, a stream-sign-flipping record-id clock).

This does not sink CDE. It locates its actual contribution. CDE's real
difference from Crius is not "more affordance" -- it is that CDE hands
the organism a WORKING acquisition mechanism (a writer/critic loop that
already knows how to produce a correct artifact) instead of requiring
blind search to discover that the store is worth using. Crius removes
the gradient problem by assumption. That is a defensible and
interesting move, but it must be stated as the difference, because it
is also the source of the confound in s4 below.

Recommendation: CDE-0 should include a Crius-style blind-search arm as
a declared negative control, so CDE's first claim is measured against
Prometheus's own established null rather than against nothing. Crius is
the only seat in the repository that has already run this experiment,
and the receipts are on disk.

## 3. What Atlas's catalog already says

The thesis's s1 says a prior-art raid "exposed several mature research
lines that had not been integrated into the design discussion early
enough." The catalog is more interesting than that framing suggests.

roles/Atlas/catalog/ECOSYSTEMS.jsonl has 365 entries and already
contains voyager, sima ("SIMA / SIMA 2", active), genie, genie-2
("Genie 2 / Genie 3", active), genie-redux, plus the entire adjacent
family the thesis omits: omni, omni-epic, ada (AdA), poet and four
POET derivatives, llm-poet, eurekaverse, gensim.

So the failure was not discovery. Atlas found them. The failure was
CONSUMPTION -- nothing carried a catalog entry into engine design. That
is an organizational defect with a different remedy than "raid harder":
it wants a standing path from Atlas's catalog into engine design
review, which is cheap and which no seat currently owns.

The catalog also permits an immediate, code-free test of the thesis's
central positioning claim, because its schema already carries the exact
axis CDE is built on -- organism.development (true/false) -- and an
environment_generation field. Cross-tabulating them:

    365  catalogued systems
     72  organism.development == true
     12  development == true AND environment_generation != fixed
      1  of those 12 is a cumulative-competence system: voyager

The other eleven (apesdk, chromaria, evolving-protozoa,
hybrid-nca-evocraft, movable-feast-machine, pbt-nca,
pd-nca-evolving-many-worlds, primordia, propeller, species-alre,
yuca-glaberish) are ALife systems where "development" means
morphogenesis or replication, and where generation is procedural or
co-evolved rather than conditioned on what the organism can currently
do.

Two consequences, pulling in opposite directions, and both should be
recorded:

- FOR the engine: CDE's corner of the space is close to empty. n = 1,
  and that one is Voyager. That is an unusually strong empirical
  justification for a new lens, and it was computed from this
  repository's own catalog in one query.
- AGAINST the engine: when the corner contains exactly one occupant,
  "new engine" and "reimplement that occupant with better telemetry"
  are hard to tell apart. s19's kill gate is correctly placed and
  should be treated as live, not ceremonial.

Separately, a defect to report to Atlas: organism.development is
overloaded. It is true for both Voyager (lifetime accumulation of
executable competence) and growing-nca (morphogenesis from a seed).
Those are different phenomena and CDE's scientific object depends on
telling them apart. The field needs splitting before it can be used as
evidence for anything.

## 4. The load-bearing weakness: "reachable" is undefined

CDE's first scientific question (thesis s17) cannot currently be
answered, only narrated. "The set of experiences an organism can
subsequently reach" needs a frozen operational definition BEFORE any
code exists. Reachable at what budget? Under what policy? At what
success probability? Over which task family?

The honest version is something like: the fraction of a held-out task
family solved within budget B at success rate p, where the family, B
and p are fixed and hashed before the first run. Without that, every
CDE result will be a story about a curve.

Crius lost prediction P1 on precisely this and the correction is
already in its ledger: "budgets are quoted with the reachable fraction,
never 'unreachable'." Reachability there turned out to be a measured
quantity that behaved nothing like the intuition -- ENUMERATE solved
3/6 held-out depth-4 tasks that were supposed to be out of reach.

## 5. The LLM confound: who is developing?

The thesis describes a Voyager skill as identifier / description /
executable payload / retrieval representation, and calls the
abstraction substrate-independent. That is true of the DATA STRUCTURE
and false of the SYSTEM. What makes Voyager work is a frontier LLM
writing the payload and a critic reading environment errors. Remove
the LLM and what remains is approximately Crius, which returned a
clean null.

The thesis says "do not inherit blindly: LLM-created semantic
ontology," but does not confront the consequence: if the artifact
writer is an LLM, most of the competence on display lives in the
writer's weights and in the retrieved text placed into its context,
not in the organism or its lineage. Every CDE result then faces the
question "did the lineage develop, or did the writer receive a better
prompt?"

This is exactly the failure class base-role s2 names -- verify the
property, never the label. The needed controls are cheap to specify
now and expensive to retrofit later:

- INFORMATION-MATCHED ABLATION: same writer, library removed, but the
  full prior transcript available in context. If performance holds, the
  library was a cache, not machinery.
- FROZEN WRITER: the writer model pinned by version and hash for the
  life of a campaign, recorded in every receipt. A silent model upgrade
  mid-campaign would otherwise read as development.
- WRITER-ONLY BASELINE: the writer attempting the held-out family cold,
  with no lineage at all, at matched budget.
- CONTAMINATION CHECK: if worlds are drawn from anything the writer
  could have memorized (Minecraft above all), transfer results are
  uninterpretable. This argues for synthetic worlds on scientific
  grounds, not just cheapness -- an argument the thesis's s5 reaches by
  a different route.

## 6. An unresolved governance conflict between s6 and s9

s6 argues Prometheus should supply INGREDIENTS, not ANSWERS, and gives
a table in which "skill library" is the answer whose ingredient is
"addressability." s9 then says CDE is deliberately the high-prior
puddle and will supply skill persistence, retrieval, modularity and
adaptive curricula -- i.e. the answers.

Both positions are defensible. The document does not say which one
governs, and that ambiguity is expensive: every future design argument
inside CDE will be able to cite whichever section suits it, and the
engine will drift toward whichever the arguer prefers that week.

Proposed resolution, for the operator to accept or replace: s9 governs
the DEVELOPMENTAL layer (CDE-0 to CDE-4 may use given machinery --
store, retrieval, curriculum -- because the question there is what
accumulation does). s6 governs the SUBSTRATE layer (CDE-5 and CDE-6,
where artifacts form an ecology and communication appears, must supply
ingredients only -- no router, no expert, no designated memory). Stated
that way the ladder has a coherent philosophical shape: it hands over
answers early to get a working loop, then progressively withdraws them.

Also, a smaller note on the s6 table: it conflates two relations.
"persistent artifacts -> procedural memory" is ingredient-to-
implementation; "local signals -> attention" and "communication ->
expert routing" are ingredient-to-emergent-pattern. The table will be
quoted as a design rule, so it should be tightened before it hardens.

## 7. CDE-3 is the Goodhart trap, and Prometheus has already been bitten

A generator that proposes tasks and also supplies the reward signal
will find the region where its agent succeeds. The thesis lists this in
s13 as one failure among eight. It is not one among eight; it is the
default outcome, and the repository already holds the precedent: the
Icarus tier calibration exposed Goodharted self-evaluation, and the
swarm-wide response was SW-2, blind-oracle discipline
(pivot/prometheus_swarm_roadmap_2026-05-28.md).

The external literature agrees and the catalog already has it: OMNI
exists because learning-progress curricula produce learnable-but-boring
task floods, and its remedy -- an outside model of interestingness --
is itself a judgment the agent can chase.

Concrete requirement: CDE-3 needs a held-out world family frozen and
hashed BEFORE the generator runs, which the generator cannot see, read
or condition on, and on which the competence frontier is measured. The
generator's own tasks may be used for training and never for the
verdict.

## 8. Nothing in CDE dies

Every other engine in the list has selection. CDE as specified in s17
has one persistent organism identity and an accumulating library. That
is accumulation without selection -- ontogeny with no population --
which means CDE-0 through CDE-4 are, strictly, N = 1 anecdotes unless
replicated across independent lineages.

This is a design choice, not an error, but it must be named, because
two things follow. First, the number of independent lineages per
condition is a statistical power question that has to be answered
before CDE-0, not after. Second, the phylogeny/ontogeny split the
thesis draws against NPE (s10) is doing real work: it means CDE cannot
answer any question about heritability until CDE-5, and should not be
asked to.

Crius is again the cautionary case: its effects had to be read across
seeds because single-run orderings were noise, and its ledger records
the correction -- "late/early is reported beside its FRESH noise floor
and is not a criterion."

## 9. Compute accounting will decide CDE-0 before the science does

CDE-0 compares no-memory, episodic history, demonstrations and
executable artifacts "after matching information and compute." Matching
compute across those four arms is genuinely hard and unglamorous: the
episodic arm spends its budget in the context window, the artifact arm
spends it in retrieval and execution, and there is no natural common
unit.

Crius hit this exactly and the fix is in its backlog (CRIUS-20):
replace approximate charging with the same budget accounting the VM
uses. Whatever single currency CDE picks -- wall time, tokens,
environment steps, or a declared composite -- it must be frozen and
hashed with the config before the first run, or CDE-0's verdict will be
an artifact of the accounting.

## 10. Mechanism identity needs a test, and the thesis already contains it

s12 is the highest-value claim in the document: that the same causal
pattern may appear independently across five differently biased
substrates. It is also the most under-specified -- "approximately the
same causal pattern" by what test? Left as is, cross-engine convergence
will be human pattern-matching, which is the thing base-role doctrine
says not to trust.

The operational test is already in the document, in s11's transfer
list: TRANSPLANT. Two mechanisms are the same if organ A, lifted from
engine A, stripped of semantics and transplanted into engine B's
substrate, performs organ B's function -- measured by ablating B's
native organ and showing the transplant restores what the ablation
removed. That is falsifiable, it is what Nyx already does, and it
should be promoted out of the s11 list into s12 as the definition of
convergence.

## 11. The kill gate needs a date and a receipt

s19 is the best section in the thesis and currently has no trigger.
A gate without an evaluation point is a sentence. Prometheus's own
pattern (Crius's rung gates, Aether's KILL_GATES_01) is that a gate
names its criteria, its evaluation moment, and the receipt that records
the verdict.

Proposal: CDE runs as an experiment family inside existing
infrastructure until CDE-1 reports. The gate is evaluated then, on the
evidence of CDE-0 and CDE-1, and its verdict is committed as a receipt.
Independent-engine status is granted or refused at that moment, and
"refused" means the work continues as a family, not that it stops.

## 12. Smaller notes

- s3's claim that Voyager's "source is public" is true and worth
  exploiting concretely: MIT licensed, JavaScript, last activity 2024
  (Atlas entry `voyager`). The curriculum, critic and retrieval are
  three separable files. A read of that source is the cheapest possible
  first move and requires no CDE infrastructure at all.
- Atlas's own Voyager entry flags one of its numbers as unverified
  ("3.3x figure from memory of abstract"). The thesis's
  characterizations of SIMA 2 in particular are from DeepMind's
  published material about a closed system and should carry the same
  flag until Techne's raid lands.
- The name is apt in a way worth keeping. Chiron is the tutor of
  heroes -- the one who trains Achilles, Jason and Asclepius and is
  never the hero. He is also the immortal who ends by giving up his
  immortality. An engine whose stated ambition (s20) is that the
  organism eventually discards the machinery the tutor supplied has the
  right name.

## 13. Recommended changes, in priority order

1. Freeze an operational definition of "reachable" (task family, budget,
   success threshold), hashed, before any code. [s4 above]
2. Add the LLM controls to CDE-0's design: information-matched
   ablation, frozen writer hash in every receipt, writer-only baseline,
   contamination check. [s5]
3. Add a Crius-style blind-search arm as CDE-0's declared negative
   control, and read Crius's four campaign packets first. [s2]
4. Freeze a blind held-out world family for CDE-3 before the generator
   exists; generator tasks train, never judge. [s7]
5. Declare the compute currency and the lineage count per condition
   before CDE-0. [s8, s9]
6. Rule on which of s6/s9 governs which rung of the ladder. [s6]
7. Bind the s19 kill gate to CDE-1's report with a committed receipt.
   [s11]
8. Promote transplant-under-ablation into s12 as the definition of
   cross-engine mechanism identity. [s10]
9. Report the overloaded organism.development field to Atlas. [s3]

## 14. Open questions for the operator

- Is the artifact writer an LLM? The whole control structure of CDE-0
  depends on the answer, and the thesis does not say.
- Does CDE own new infrastructure, or does it run inside BEE until the
  s19 gate? The thesis leans toward the latter (s10) and the backlog
  cannot be sized until it is settled.
- How many independent lineages per condition is CDE willing to pay
  for? This bounds every claim CDE can make.
- Is Crius's sandbox available to CDE as a negative control, or is that
  seat's lane closed to reuse?

## 15. What I did not verify

- I did not read Voyager's, SIMA's or Genie's source or papers in this
  pass. My characterizations of them are from model knowledge plus
  Atlas's catalog entries, not from a source-verified raid. SIMA 2
  specifics are DeepMind's own published claims about a closed system.
- I did not re-run any Crius campaign. The C0/C1/C1b/C2 findings quoted
  above are read from roles/Crius/STATUS.md and
  roles/Crius/calibration/LEDGER.md, which cite receipts under
  crius/runs/ that I did not open.
- The catalog cross-tab in s3 is my own query over
  roles/Atlas/catalog/ECOSYSTEMS.jsonl at commit 3e2c59c31 and depends
  entirely on Atlas's field assignments being correct. Given the
  overloading defect I report in that same section, the counts should
  be treated as indicative, not precise.
- No CDE code, world, controller, artifact store or run exists. Nothing
  in this review has been tested.
