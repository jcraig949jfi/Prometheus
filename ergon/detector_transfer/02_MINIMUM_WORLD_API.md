# 02 - MINIMUM WORLD API

Smallest interface a controlled world must expose. The detector FAILS CLOSED:
a missing REQUIRED field aborts, never defaults.

## REQUIRED

    genotype serialisation   bytes <-> genotype, stable and injective
    finite alphabet          alphabet_size() -> A
    length                   len(g) -> L
    deterministic evaluation evaluate(g, context) -> Observation,
                             bit-identical on repeat
    phenotype observable     Observation.phenotype -> vector
    scalar selection obs.    Observation.scalar -> comparable
    projection guarantee     world asserts scalar is DERIVED FROM phenotype
    validity state           Observation.valid -> bool + reason code
    substitution enumeration neighbours_sub(g) -> iterator

## OPTIONAL (measured if present; absence reported, never imputed)

insertion enumeration; deletion enumeration; execution seed; environment or
resource state; execution trace; step count; halt class; parent pointer.

## FORBIDDEN TO INFER

The detector must NEVER synthesise:

    a scalar channel when the world exposes none -- inventing pi destroys the
      question (seam S1)
    a phenotype vector assembled from ANALYST-CHOSEN probes, unless the world
      defines the probe set. An analyst-chosen probe set makes P richer than
      anything selection ever saw, guaranteeing a positive.
    viability, when the world has no validity notion
    determinism, when the world declares NONDETERMINISTIC
    a mutation operator the world does not implement

## Fail-closed codes

    WORLD_API_INSUFFICIENT      a REQUIRED capability is absent
    NONDETERMINISM_DETECTED     repeat evaluation differs
    PROJECTION_UNVERIFIED       world will not assert scalar = pi(phenotype)
    NEIGHBOURHOOD_INTRACTABLE   |N1| exceeds the declared compute ceiling
