# L - COMPUTE MODEL

No estimate here is a recollection. Where a number is not benchmarked it is
labelled EST and the reason is given. The directive forbids the phrase "one
CPU-day" surviving without benchmark evidence, and none appears.

## Measured today

    supplementary PDF retrieval + text extraction     < 5 s
    Avida 2.2 tarball retrieval                       1,664,380 bytes, ~4 s
    tarball extraction                                < 3 s
    lineage parse (112 records)                       < 1 s
    provenance gates over 6 artifacts                 < 1 s

## NOT measured, and dominant

**The cost of evaluating one Avida genome is unbenchmarked**, because Avida 2.2
has not been compiled. Every downstream estimate therefore depends on an
unmeasured constant, and the honest statement is that the compute model is
incomplete until that constant exists.

    e = seconds per genome evaluation (colony test to viability + phenotype)
        STATUS: UNMEASURED

## Static analysis scale, in units of e

    mutants per genotype        L * 25, i.e. 1250 (L=50) to 1525 (L=61)
    focal genotypes             3 checkpoints
    controls                    3-5 per checkpoint  -> 9-15 additional genotypes
    genotypes in H1A            12-18
    one-step evaluations        ~1250-1525 each, so 1.5e4 to 2.7e4 total
    k=2 sampled                 N2 per genotype, N2 TBD after convergence

**H1A therefore costs order 10^4 genome evaluations.** Even at a pessimistic
e = 10 ms that is minutes, and at e = 1 ms it is seconds. The static stage is
not compute-bound under any plausible e, which is why the directive is right
to insist on it before any replay forest.

## The build risk, which is the real cost

Avida 2.2 is 2005-era C++ with a CVS-era build system (bjam / autotools
fragments visible in the tree). Compiling it on a modern toolchain is the
single largest unquantified engineering cost in this pass, and it is a
**binary** risk: either the historical evaluator runs, or P-MED must be
implemented against a reimplementation, which immediately raises K8
(reconstruction fails to reproduce the historical phenomenon).

Recommended sequencing: attempt the 2.2 build FIRST, before writing any metric
code, because the outcome determines whether the analysis uses the historical
evaluator or a surrogate. That is a fork in the whole programme, not a detail.

## H1B, for scale only - NOT authorised

Forked descendant populations would multiply by K replicates x B budget x
checkpoints x controls. With population size, mutation rates and run length all
UNSPECIFIED, no credible estimate is possible. Any H1B number quoted today
would be invented. None is quoted.
