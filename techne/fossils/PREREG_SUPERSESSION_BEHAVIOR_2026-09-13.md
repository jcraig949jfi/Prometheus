# PREREGISTRATION -- turning documented supersession into a behavioural coordinate (batch 10 P4)

Filed BEFORE building LAPACK or running any comparison.
Charter: roles/Techne/prompts/2026-09-13_batch10/OPERATOR_CHARTER.md sha256 2c28f471c33abc52...

## THE DOCUMENTED PRESSURE (what the human record actually claims)

LAPACK Users' Guide: LAPACK was written to supersede LINPACK and EISPACK. The stated reason is
NOT that LINPACK's mathematics was wrong -- it is that LINPACK and EISPACK are organised around
Level-1 BLAS (vector-vector) operations whose memory-reference pattern performs poorly on machines
with cache and multi-level memory hierarchies, while LAPACK restructures the same algorithms into
BLOCKED form expressed in Level-3 BLAS (matrix-matrix) so that data brought into cache is reused.

So the claim under test is about DATA REUSE / COMPUTATIONAL ORGANISATION, not about speed per se.

## WHY NOT WALL-CLOCK

The charter forbids a vanity benchmark, and it is right to: wall-clock on one container, with an
unoptimised reference BLAS, on a shared Windows/WSL host, measures the host at least as much as it
measures the fossils. It is also exactly the number a person would be tempted to tune.

## THE MEASUREMENT (structural, deterministic, timing-free)

Both factorisations are linked against a COUNTING SHIM: Fortran wrappers with the BLAS entry-point
names that increment per-routine counters and then call the real routine. Neither preserved body is
modified; the shim is harness code and lives outside both bodies.

For each solver and each matrix size we record, per BLAS routine:
  - number of calls
  - total matrix ELEMENT-REFERENCES implied by the arguments (for daxpy/dscal/ddot: n per call;
    for dgemm: m*n + m*k + k*n; for dtrsm: m*n + (m or n)^2/2; for idamax/dswap: n)
and derive:
  - LEVEL3_FRACTION = element-references issued through Level-3 routines / total element-references

LEVEL3_FRACTION is the behavioural coordinate. It is a property of the algorithm's organisation,
identical on any machine, and cannot be improved by tuning a timer.

Wall-clock IS also recorded, explicitly labelled SECONDARY and CONFOUNDED, and is not used for any
claim.

## PREREGISTERED REGIMES (fixed now, derived mechanically -- powers of two)

    n in {64, 128, 256, 512, 1024}

Rationale stated in advance: reference LAPACK's ILAENV returns a default block size of 64 for
dgetrf, so n=64 sits AT the block size (expect little or no blocking), and each larger n doubles
the number of blocks. No size will be added, removed or re-run after seeing results. The same
matrix (same generator, same seed, same values) is given to both solvers at each n.

## PREREGISTERED PREDICTIONS (falsifiable)

P-1. LINPACK dgefa issues ZERO Level-3 calls at every n. LEVEL3_FRACTION(dgefa) = 0.000 for all n.
P-2. LAPACK dgetrf issues Level-3 calls (dgemm and/or dtrsm) for n > 64, and its LEVEL3_FRACTION
     INCREASES monotonically with n over the preregistered sizes.
P-3. At n = 64 the two may be indistinguishable (dgetrf falls back to the unblocked dgetf2 at or
     below the block size). A null result AT n=64 is EXPECTED and is not a failure.
P-4. Both solvers produce the SAME factorisation to within floating-point tolerance on the same
     matrix: max |PA - LU| / (n * eps * ||A||) is O(1). If they do not agree, the comparison is
     invalid and no organisational claim may be made from it.

FALSIFICATION: if LEVEL3_FRACTION(dgetrf) is ~0 at every preregistered n -- e.g. because this
reference build's ILAENV returns nb=1 -- then the documented pressure is NOT reproduced by these
two preserved bodies in this environment, and that is the result to report. I will NOT enlarge n
or change the block size to manufacture a difference.

## CONFOUNDS RECORDED EXPLICITLY

C-1 ALGORITHMIC: dgefa factorises without pivoting bookkeeping identical to dgetrf's; both use
    partial pivoting (idamax) but LAPACK's right-looking blocked algorithm is a DIFFERENT algorithm,
    not merely a re-tiling. The comparison is organisation-vs-organisation, which is what the
    Users' Guide claims -- it is not an apples-to-apples re-implementation.
C-2 ENVIRONMENT: one container, one compiler (gfortran -O2), one host. Identical for both arms.
C-3 BLAS QUALITY: reference (unoptimised) BLAS for both. A vendor BLAS would change wall-clock
    enormously and LEVEL3_FRACTION not at all -- which is the point of choosing this coordinate.
C-4 SHIM OVERHEAD: the counting shim wraps every call and therefore penalises the arm that makes
    MORE calls, i.e. LINPACK. It affects wall-clock only, never the counts.
C-5 ERA: LINPACK 1979 Fortran 77 vs modern reference LAPACK. Not the same era of code quality.

## EISPACK / LAPACK

The same structural coordinate is applied to the symmetric eigenproblem: EISPACK `rs` (tred2+tql2)
versus LAPACK `dsyev`. The prediction is the same in form (P-1/P-2 with dsytrd's blocked reduction),
and the oracle is the closed-form spectrum of the second-difference matrix, so correctness is
checked against mathematics rather than against the other program. If reference LAPACK's dsyev does
not reach a blocked path at these sizes, that is reported as a null.
