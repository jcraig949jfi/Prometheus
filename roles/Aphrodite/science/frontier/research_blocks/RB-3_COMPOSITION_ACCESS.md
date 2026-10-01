# RB-3 -- COMPOSITION-OPERATOR ABLATION: IS G1-DEPENDENT NOVELTY AN ACCESS PROBLEM? (T10, T11, T12)

Medium, autonomous after RB-1. Estimated 1-2 days. Read RB-00 first.

WHY
  K3: the fixed improver can derive 467 NEW single-hole schemas from PRISTINE coverage,
  and inheriting G1 adds ZERO (467 = 467), because derivation abstracts only over library
  coverage and G1's coverage is G1's own instances. K6: schemas that COMPOSE G1, such as
  ((acc + {H}) % last) and ((acc + {H}) * v), are representable in G4 (52 non-trivial
  forms, 2,792 instantiations). So G1-dependent novelty is not unrepresentable. It is
  INACCESSIBLE. This is Crius's existence-vs-accessibility split (CROSS_ENGINE s1), and
  NPE E-8's encoding-length lever.

STATUS: Q1 DONE 2026-09-27 as spike K8 (spikes/k8_composition_universe.py,
  K8_COMPOSITION_UNIVERSE.json): YES. 77 G1-composing schemas become derivable. Start at Q2.

QUESTIONS, in order
  Q1 (existence, analytic)  With a composition move that adds wrap(S, op, atom) entries
     for every library schema S, does the derivable NEW universe under inheritance grow
     beyond 467? Recompute K3 over the composed coverage.
  Q2 (value landscape)  Hand-build 10 G1-composing schemas. On the K2 pool families (or
     RB-2's widened world), does each pay (paired charges vs L1)? Do its partials pay?
     That is Crius-style pricing.
  Q3 (access, experiment)  Donor pairs on K5-style rich supplies:
       {G1 + composition ON, G1 + composition OFF, PRISTINE + composition ON,
        SHAM + composition ON}
     where SHAM is a random single-hole schema of equal instantiation count. Does
     composition ON make G1 donors select NEW (by the RB-1 ruler) schemas more often than
     PRISTINE and SHAM donors?
  Optional Q4: repeat Q1 with 2-hole LGG (T12).

GUARDRAILS
  - The composition move must be TREATMENT-BLIND: it applies to whatever schemas the
    library holds (G1, SHAM or none) with identical rules and charges.
  - Report the escrow breadth cost: composed entries consume budget (T14).
  - Q3 yields a disposition only if preregistered in a dated AMENDMENT (Aphrodite
    freezes). Before that it is forensic.

DELIVERABLES
  science/frontier/rb3/ (scripts, RB3_Q1/Q2/Q3 JSON, COMPOSITION_ACCESS.md).
  A Q1 = NO (no growth) is itself decisive: it says recursion needs representation
  change, not a move.
