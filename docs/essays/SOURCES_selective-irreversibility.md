# Sources for "Selective Irreversibility"

Verification pass, 2026-09-23, Aporia. Every entry below was resolved against the
publisher or arXiv record; nothing here is cited from memory. Where the essay's
wording and the source diverge, the divergence is stated rather than smoothed over.

---

## The load-bearing claim: "nostalgia"

The essay says:

> Still, Sivak, Bell and Crooks studied physical systems that retain information about
> their environments and separated remembered information into information useful for
> predicting the future and information merely about the past. They found a direct
> relationship between nonpredictive stored information and thermodynamic inefficiency.
> Their term for the useless retained past information is particularly memorable:
> nostalgia.

**VERIFIED, with three refinements.**

    Susanne Still, David A. Sivak, Anthony J. Bell, Gavin E. Crooks
    "The thermodynamics of prediction"
    Phys. Rev. Lett. 109, 120604 (2012); arXiv:1203.3271 (submitted 15 Mar 2012)
    https://arxiv.org/abs/1203.3271

1. The author list and order in the essay are exactly right.
2. The term is **"useless nostalgia"**, and it is in the body, not the abstract. The
   abstract calls the same quantity "nonpredictive information ... the ineffectiveness
   of the model". Verbatim from the paper:

       "The instantaneous nonpredictive information is defined as the difference
        between instantaneous memory and predictive power, I_mem(t) - I_pred(t).
        It represents useless nostalgia and provides a measure for the
        ineffectiveness of the model."

   So "nostalgia" is not a loose gloss: it names a specific quantity,
   I_mem - I_pred, where I_mem := I[s_t ; x_t] and I_pred := I[s_t ; x_{t+1}].
3. The paper's result is **stronger** than the essay claims. Not merely "a direct
   relationship" with inefficiency — the paper states that summed over the protocol,
   total nonpredictive information provides a **lower bound on total dissipation**.
   The essay understates its own best evidence.

**The direct follow-up, which the essay does not cite and arguably should:**

    Susanne Still
    "Thermodynamic cost and benefit of memory"
    Phys. Rev. Lett. 124, 050601 (2020); arXiv:1705.00612
    https://arxiv.org/abs/1705.00612

Still derives a generalized lower bound on dissipation for partially observable
information engines, shows that retention of irrelevant information limits efficiency,
and — most relevant here — shows that minimizing that bound *yields* a compression
strategy that maximally retains predictive information. Predictive inference emerges
as the strategy that least precludes energy efficiency.

That is close to the essay's "predictive selective retention" being derived rather
than posited. It is the single most important addition to the reference list.

---

## Landauer, and the cost of erasure

    Rolf Landauer
    "Irreversibility and heat generation in the computing process"
    IBM Journal of Research and Development 5(3), 183-191 (1961)
    doi:10.1147/rd.53.0183

    Charles H. Bennett
    "Logical reversibility of computation"
    IBM Journal of Research and Development 17(6), 525-532 (1973)
    doi:10.1147/rd.176.0525

Bennett is what licenses the essay's sentence "Reversible computation can in principle
avoid that cost until information is actually erased/reset" — he showed a general-purpose
machine can be made logically reversible at every step, making it plausible that a
computer could run while dissipating much less than kT per logical step.

**The experimental demonstration** the essay alludes to:

    Antoine Bérut, Artak Arakelyan, Artyom Petrosyan, Sergio Ciliberto,
    Raoul Dillenschneider, Eric Lutz
    "Experimental verification of Landauer's principle linking information
     and thermodynamics"
    Nature 483, 187-190 (8 March 2012); doi:10.1038/nature10872
    https://www.nature.com/articles/nature10872

A single colloidal particle in a modulated double-well potential; mean dissipated heat
saturates the Landauer bound in the long-erasure-cycle limit. This is the citation for
"Experiments have directly demonstrated the k_B T ln 2 limit for bit erasure."

**The "more general treatments"** the essay gestures at without naming:

    Juan M. R. Parrondo, Jordan M. Horowitz, Takahiro Sagawa
    "Thermodynamics of information"
    Nature Physics 11, 131-139 (2015); doi:10.1038/nphys3230

    David H. Wolpert
    "The stochastic thermodynamics of computation"
    J. Phys. A: Math. Theor. 52, 193001 (2019); doi:10.1088/1751-8121/ab0850

Wolpert is the right place to send a reader who wants the Landauer bound applied to
actual computation rather than to a single bit.

---

## The Information Bottleneck

    Naftali Tishby, Fernando C. Pereira, William Bialek
    "The information bottleneck method"
    arXiv:physics/0004057 (24 April 2000)
    https://arxiv.org/abs/physics/0004057

"We squeeze the information that X provides about Y through a 'bottleneck' formed by a
limited set of codewords." Exactly the essay's move: make Z small while preserving
I(Z;Y).

**Predictive information**, which is what Y stands in for when the task is the future:

    William Bialek, Ilya Nemenman, Naftali Tishby
    "Predictability, complexity, and learning"
    Neural Computation 13(11), 2409-2463 (2001); doi:10.1162/089976601753195969

---

## Where the compression boundary actually comes from

The essay is right that this is rate-distortion, not Landauer. The origin:

    Claude E. Shannon
    "Coding theorems for a discrete source with a fidelity criterion"
    IRE International Convention Record, vol. 7, 142-163 (1959)

R(d): for coding purposes where distortion d can be tolerated, the source behaves like
one of information rate R(d). The "abstraction cliff" is a statement about the shape of
R(d) for a particular task, which is why it is architecture-dependent.

---

## Steering as work

    David A. Sivak, Gavin E. Crooks
    "Thermodynamic metrics and optimal paths"
    Phys. Rev. Lett. 108, 190602 (8 May 2012); doi:10.1103/PhysRevLett.108.190602

A friction tensor induces a Riemannian manifold on the space of thermodynamic states.
Note the essay's hedge "within certain regimes" is precisely correct and should be kept:
the paper says the metric controls dissipation of finite-time transformations **within
the linear-response regime**. Dropping that qualifier would misstate the result.

---

## Predictive selective retention has a formal counterpart

    Cosma Rohilla Shalizi, James P. Crutchfield
    "Computational mechanics: pattern and prediction, structure and simplicity"
    J. Stat. Phys. 104, 817-879 (2001); arXiv:cond-mat/9907176
    doi:10.1023/A:1010388907793

Causal states, and the epsilon-machine as the **minimal representation consistent with
accurate prediction**. If "retain exactly what predicts, discard the rest" has an exact
formulation, this is it — and it predates the framing by two decades. Worth knowing
before claiming novelty for the idea.

---

## The prediction that constraint *creates* abstraction

This is the essay's most provocative claim — that more memory can make a system less
intelligent, and that capability may peak at intermediate constraint. It is not
speculation; there is a directly relevant experimental literature:

    Simon Kirby, Hannah Cornish, Kenny Smith
    "Cumulative cultural evolution in the laboratory: an experimental approach to the
     origins of structure in human language"
    PNAS 105(31), 10681-10686 (5 August 2008); doi:10.1073/pnas.0707835105

Artificial languages transmitted through chains of human learners, where each learner
sees only **part** of the language — a transmission bottleneck. Compositional structure
emerges as a consequence of that bottleneck, without any participant intending it.
Remove the bottleneck and the pressure toward structure goes with it.

That is the essay's causal chain — boundedness -> forced forgetting -> abstraction —
already demonstrated in one substrate. It makes the cross-substrate experiment the
essay proposes a **replication attempt with a known positive control**, not a shot in
the dark. Strongest single addition to the argument.

---

## The counter-arguments (added at the operator's instruction, 2026-09-23)

A hypothesis stated to be killed should carry its own best attackers. Three, each
verified, each now cited on the page in a closing section:

    Preetum Nakkiran, Gal Kaplun, Yamini Bansal, Tristan Yang, Boaz Barak,
    Ilya Sutskever
    "Deep double descent: where bigger models and more data hurt"
    ICLR 2020; arXiv:1912.02292
    https://arxiv.org/abs/1912.02292

The strongest single objection. Test error falls, rises, then falls AGAIN as capacity
grows past the interpolation threshold, and the paper identifies regimes where even
quadrupling training data hurts. Most of modern machine learning operates on the far
side of that second descent, where more capacity reliably helps. The essay predicts
capability peaking at intermediate constraint; this is a measured curve that does not
have that shape. Not fatal -- the essay's claim is about pressure to ABSTRACT, not raw
test error, and the two need not coincide -- but that distinction has to be argued, not
assumed.

    Horace B. Barlow
    "Possible principles underlying the transformation of sensory messages"
    in Sensory Communication, MIT Press, 216-234 (1961)

The efficient-coding hypothesis began with exactly this essay's intuition: sensory
systems reduce redundancy. It had to be substantially weakened. Real neural codes keep
considerable redundancy, deliberately, for noise tolerance and error correction. In the
one substrate we can inspect at leisure, evolution did NOT choose "destroy distinctions
that no longer matter". Cited both as the origin of the idea and as evidence against
its strong form.

    Falk Lieder, Thomas L. Griffiths
    "Resource-rational analysis: understanding human cognition as the optimal use of
     limited computational resources"
    Behavioral and Brain Sciences 43, e1 (2020)
    doi:10.1017/S0140525X1900061X

The deflationary objection, and the one hardest to answer. Resource-rational analysis
already explains a great deal of bounded cognition as optimizing against time, memory
and computational cost, with no physics in it at all. If it accounts for the phenomena,
Landauer is a layer nothing yet requires. The burden on the whole essay is to produce
one prediction resource-rationality does not already make.

---

## What remains uncited because it is genuinely ours

The Selective Irreversibility Hypothesis as stated, and the three ratios (eta_I, eta_A,
eta_F), are not drawn from any of the above. They are the essay's own construction and
should not be given borrowed authority. They remain, in the essay's own words, rulers
to attack.
