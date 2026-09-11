# EOS-31 / Mission 3: can PENDING_ADMISSION require CONTACT rather than EXISTENCE?

Currency: 2026-09-11. Operator directive: investigate whether the
repository already contains stronger, machine-checkable relationship
evidence. Do NOT solve it with semantic similarity, embeddings, an LLM
relevance score, or another phrase list. A negative answer is acceptable.

Measurements: roles/Eos/intake/contact_witnesses_2026-09-11.json
Tool: agents/eos/src/contact_witness.py
THE GATE IS UNCHANGED. Nothing here is wired in. Under the directive Eos
may not optimise against the six live examples before the independent
attackers answer.

## The answer: NO for contact, YES for two things that are not contact

    CONTACT        no deterministic witness exists, and the reason is
                   structural rather than a gap in effort
    DUPLICATION    a deterministic witness exists, was built, and caught
                   a real duplicate on the first sample
    INTERRUPTION   several deterministic witnesses exist and they
    QUALITY        convict three of Eos's own six claims

## Why contact cannot be witnessed, stated as a structural argument

Candidate witnesses split into two kinds:

    REFERENT-SIDE   a function of the internal referent ALONE
                    (token specificity, inbound edges, ownership,
                    liveness, test ownership, backlog identifiers)
    PAIR-SIDE       a function of (external object, internal referent)

Only a pair-side witness can separate a true claim from a laundered one,
because a laundered claim names a perfectly good referent. Eos's own
sample proves this without any new experiment:

    live item 5      Proof-Carrying Cognition (arXiv 2609.09776v1)
    Test 4 bait      Compressed Coordinate Systems (constructed)

    BOTH NAME       roles/base-role/RESPONSIBILITIES.md#No LLM adjudicates

Every referent-side witness is IDENTICAL for these two by construction --
same token specificity (14), same inbound references (170), same owner,
same last commit. No quantity computed from the referent alone can
distinguish them, no matter how sophisticated. That closes off the entire
referent-side family in one line, which is why it is worth stating before
measuring anything.

The pair-side family is nearly empty, and for a concrete reason: the
repository contains no edges to external objects except citations of
things it has ALREADY metabolised. Import edges, opcodes, schema
ownership, test ownership and producer/consumer edges are all
repository-internal; they relate repository objects to each other. An
arXiv paper published last month has no edge into this tree and this tree
has no edge out to it. The witness does not exist because the relation
does not exist yet -- creating it is what admission IS.

CONCLUSION: the hole is preserved and the human admission boundary stays.
That is the operator's acceptable negative answer, and Eos is not going
to dress it up.

## What DOES exist, 1: a duplication witness, and it already earned itself

The one deterministic pair-side fact available is: does the repository
ALREADY cite this external object, by arXiv id, DOI, URL or title?

Measured over the six live PENDING items plus the Test 4 bait, excluding
everything Eos writes:

    popB-2608.15546v2  ATLAS: Scaffold-Free Algorithm Synthesis
                       CITED IN 1 FILE ALREADY
                       aporia/docs/frontier_campaign_69/hypotheses/
                       206_h3_adversarial_review.md:27
                       "...the ATLAS framework described in
                        arXiv:2608.15546 [cite: 4], heavily relies on
                        embedding-guided quality-div..."
    the other six      0

One of the six interruptions Eos sent was for an object the program had
already metabolised, in a lane (Aporia's frontier campaign) that Eos
never looked at. Apollo was asked to consider a paper another seat had
already written into a hypothesis document.

This is not a hypothetical improvement. It is a 1-in-6 false
interruption that a cheap, deterministic, non-semantic check would have
caught, and it is the strongest single result of this mission.

WHY THE EXISTING GATE MISSED IT: check_not_already_absorbed only asks
whether the REFERENT FILE cites the item. Aporia's document is not the
referent file. The fix is to widen the same check from "the file the
claim names" to "the whole program except Eos" -- which is the same
exclusion rule the dedup search already learned the hard way in Season I.

NOT WIRED IN YET, deliberately. Preregistered here: Eos will wire this
check only after the independent attackers answer, and states in advance
that with it wired, ATLAS would not have been sent. That admission is
made before anyone else can make it.

## What DOES exist, 2: interruption-quality witnesses that convict Eos

These do not decide relevance. They decide whether an interruption is
worth DELIVERING, which is the operator's Q5. Measured on the five
distinct referents behind the six live items:

    referent                                     token   inbound  last
                                                 spec.   refs     commit
    apollo/ARCHITECTURE.md
      #Structural mutations die on arrival            6        8  2026-04-23
    roles/base-role/RESPONSIBILITIES.md
      #No LLM adjudicates                            14      170  2026-09-11
    roles/Nyx/BACKLOG_H0H5.md#coevolution           118        5  2026-09-11
    roles/Nyx/RESPONSIBILITIES.md#MAP-Elites        481        7  2026-09-11
    agents/icarus/daemon.py#counterexample         1198       11  2026-06-15

    token spec.  = tracked files containing the token
    inbound refs = tracked files naming the referent FILE

READ THIS AGAINST EOS, NOT FOR IT. Three of the six claims named tokens
occurring in 118, 481 and 1198 files. A token in 1,198 files is a WORD,
not a referent. "MAP-Elites" and "counterexample" identify nothing; a
claim naming them has pointed at a file and then at a word that file
happens to contain. Those three claims are weakly anchored and Eos wrote
them.

The second row is also worth saying plainly: the referent with the
highest inbound count (170) is the base-role file, and it is the one the
bait successfully laundered through. POPULARITY OF A REFERENT IS NOT
EVIDENCE FOR A CLAIM ABOUT IT -- if anything the reverse, since a file
170 things point at contains a token for almost any purpose.

And the Apollo referent has not been committed since 2026-04-23, four and
a half months. Two of the six items were filed against a sentence in a
document that may have been superseded by the June recombination result
or the August type-bridge cycle. Eos flagged that to Apollo in the
admission prompt rather than discovering it here.

## What Eos proposes, and what it does not

PROPOSES, after the attackers answer, in this order:

    1  Widen the already-absorbed check from the referent file to the
       whole program minus Eos. Deterministic, cheap, demonstrated.
       Terminal state on a hit: REFUSED, reason DUPLICATE_ALREADY_
       METABOLIZED, with the citing path in the row.
    2  Attach token specificity and inbound-reference counts to every
       PENDING record as REPORTED CONTEXT, not as a gate. The owner sees
       "this token occurs in 1,198 files" and can discount accordingly.
       Eos does not propose a threshold; there is no basis for one yet.
    3  Attach the referent's last-commit date, so an owner can see they
       are being asked about a four-month-old sentence.

DOES NOT PROPOSE:

    -  Any threshold on specificity. One season, five referents. A gate
       closer to the observed values than their spread is not a gate.
    -  Any semantic, embedding or model-scored measure. Forbidden, and
       the structural argument above says it would not be a witness of
       contact either -- it would be a better guess.
    -  Closing the laundering hole. It is not closable with repository
       evidence. The human admission boundary IS the closure.
