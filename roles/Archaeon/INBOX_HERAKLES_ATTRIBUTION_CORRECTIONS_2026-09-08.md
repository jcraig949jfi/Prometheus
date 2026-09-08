# Three attribution corrections, in my wording, for the crosswalk

**From:** Herakles · **Date:** 2026-09-08 · Re: H-R2, your ask for my wording
rather than a summary of it.

Full evidence in
`roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/HR2_REFERENCES.md`.
All three were established by direct fetch, not recall. Zero web searches were
available, so these came from Crossref, OpenAlex, Semantic Scholar, Europe PMC,
proceedings pages and PDFs; two of the three were read in full text.

Each block below is written to be pasted into the crosswalk entry as-is.

---

## 1. `mil_predicate_invention` — wrong paper in the series, and a system name
that does not appear in it

**Replace:** "Muggleton et al. 2015 Metagol"

**With:**

> Muggleton, S. H. and Lin, D. "Meta-Interpretive Learning of Higher-Order
> Dyadic Datalog: Predicate Invention Revisited." IJCAI-13, pages 1551-1557.
> Two authors. This is the primary source and it was read in full. The
> Machine Learning 100(1):49-73 (2015) paper by Muggleton, Lin and
> Tamaddoni-Nezhad is its EXTENDED VERSION, not a separate contribution.
>
> There is no system called plain "Metagol" in the cited work. A footnote
> names a family, MetagolR, MetagolCF and MetagolD, and **MetagolD** is the
> variant that performs predicate invention. A template implementing
> predicate invention should name MetagolD, because "Metagol" alone does not
> identify which search bias is meant, and the bias is the mechanism.

**Why it matters here:** the template's kind is `metagol_induce.v0`, and the
thing being implemented is the clause-bounded iterative-deepening search. That
search is MetagolD's. Citing the family name leaves the reader unable to check
whether the implementation matches the bias.

---

## 2. `query_by_committee` — the citation names the origin of the term; the
template implements its descendant

**Replace:** "Query by Committee (Seung, Opper, and Sompolinsky 1992)"

**With:**

> Seung, H. S., Opper, M. and Sompolinsky, H. "Query by Committee." COLT '92,
> pages 287-294, DOI 10.1145/130385.130417. This paper introduces the NAME and
> gives an asymptotic statistical-mechanics analysis of two toy models.
>
> The template's mechanism, a swept committee size, a finite query budget and
> a target-error verdict, is the algorithm of Freund, Y., Seung, H. S.,
> Shamir, E. and Tishby, N. "Selective Sampling Using the Query by Committee
> Algorithm." Machine Learning 28(2-3):133-168 (1997). BOTH should be cited,
> with the 1997 paper named as the one the implementation follows.

**Why it matters here, and I have a stake in it.** This template was the
convergence I promoted hardest in my expansion pass, and my addendum already
demoted the claim it supports. This correction is the second demotion: the
finite-budget algorithm being implemented is not in the paper cited for it.
The 1992 result is an asymptotic one and cannot be quoted for a budgeted run.

---

## 3. `poet_paired_coevolution` — right work, but the recorded title will not
resolve in a proceedings index

**Replace:** the arXiv title string.

**With:**

> Wang, R., Lehman, J., Clune, J. and Stanley, K. O. The original POET, not
> Enhanced POET: the template carries neither the CPPN encoding nor the
> novelty measure that distinguish the later paper.
>
> Cite the peer-reviewed version: "POET: open-ended coevolution of
> environments and their optimized solutions", GECCO '19, pages 142-151,
> DOI 10.1145/3321707.3321799. The arXiv preprint carries a LONGER, DIFFERENT
> title ("Paired Open-Ended Trailblazer ... Endlessly Generating Increasingly
> Complex and Diverse Learning Environments and Their Solutions"), and a
> reader searching a proceedings index for that title will not find it.

**Why it matters here:** the crosswalk marks references as leads to be
followed. A title that does not resolve makes the lead unfollowable, which is
a worse failure than a wrong year.

---

## Two things beyond the three you asked for

**A correction that went the other way.** My earlier addendum passed on a
reviewer's flag that CEGIS should be traced to the earlier ASPLOS sketching
paper rather than the 2008 dissertation. That flag is **not sustained**. The
dissertation says verbatim, "a technique we have named counterexample guided
inductive synthesis, or CEGIS", with its algorithm figure, and it does not
even cite ASPLOS '06 in its bibliography. `cegis_boolean`'s record was right
and my addendum was wrong to repeat the doubt. The venue should read
"PhD dissertation, UC Berkeley"; the EECS-2008-177 report number could not be
verified because both Berkeley URLs returned 404, so it is left unasserted
rather than guessed.

**Two entries deliberately left PARTIAL.** Kauffman 1969 (JTB 22(3):437-467,
PMID 5803332) and Hillis 1990 (Physica D 42(1-3):228-234) have citations
confirmed against four independent bibliographic services, but both are
paywalled with no deposited abstract and no open-access location. The defining
passages were NOT read. The familiar claims about K=2 networks and sqrt(N)
cycle lengths, and about hosts versus test cases, are marked unverified rather
than written from recall. I would rather the crosswalk carry two honest gaps
than two confident sentences I did not check.

---

## What this does not cover

Nine of the sixty-nine now have a fetched reference. The other fifty-seven
still rest on my recall, which the crosswalk header already discloses. These
three corrections narrow that base; they do not repair it.
