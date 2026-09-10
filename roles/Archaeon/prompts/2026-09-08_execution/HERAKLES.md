HERAKLES — EXECUTION ORDER 2026-09-08 (from the operator)

Baseline: archaeon/v0 at 5191c3383. Archaeon's response to your critique is
roles/Herakles/INBOX_ARCHAEON_CRITIQUE_RESPONSE_2026-09-07.md; your requests
are roles/Herakles/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md (later
sections supersede). Tests per package: archaeon/docs/expansion/
WORK_PACKAGES.md. Branch C is on the critical path and it is built on your
specimen. Nothing here waits on anyone.

DO NOW, IN THIS ORDER
1. WP-C1. Extract the EvCA verifier (herakles/specimens/spec-evca-density/)
   as a PURE LIBRARY: seeded IC generation and deterministic evolution, no
   top-level execution, no file writes, no global-RNG side effects. Pin and
   document: ring boundary; neighbourhood bit order (leftmost = MSB);
   rule encoding (32-hex, 128-bit); supported radius (r = 3 only unless you
   implement the general decoder explicitly); update count; majority/tie
   convention for odd N; accuracy definition; bounded witness
   (misclassified ICs); one declared selected trajectory/digest. Keep the
   six recovered genomes and their provenance. Tests C1-a..d in the
   package: hand-computed tiny states with a SECOND simple implementation
   as oracle; golden results for the six genomes on small fixed ICs;
   malformed tables / unsupported radius / invalid density or grid fail
   explicitly; joint reflection AND complement equivariance on normalised
   trajectories, never raw hashes of differently oriented arrays; seed and
   configuration replay. Hand the library and its fixtures to Vivarium to
   wrap as ca_density_v0. Report which conventions you pinned and why.
2. WP-C1-e, SEPARATELY: the historical-reproduction run under the source's
   conventions with a declared IC sample and a prespecified uncertainty and
   multiplicity rule. Diagnose any discrepancy across conventions, horizon,
   sampling, transcription, implementation; never move the tolerance after
   looking. This is a qualification report, not a CI gate.
3. H-R2. Fetch the twelve load-bearing references (list in your inbox):
   exact source and version, the passage or algorithm, the claim supported,
   any mismatch with the proposed implementation. Resolve evodevo.bias
   (CTRNN vs Boolean) or say it is retired to rbn.attractor's family.
4. Then, and only then, H-R1: for Branch C, one region-targeted probe
   design (given a world and a fossil region on the rule-table coordinate,
   what would the discipline run next) with inputs, observations,
   alternatives and an owner-ready next step. No breadth census.

NOT ASKED: admitting anything; Prometheus-vocabulary searches; a second
pass over the 69.

REPORT FORMAT: item ID; revisions; commands run; expected vs observed;
fixture hashes; unresolved limits; next permitted action.
