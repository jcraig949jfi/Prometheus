# Operator rulings

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Verbatim, or cited by path + sha256. First entry: the directive itself,
roles/Cyclops/prompts/2026-09-25_selective_irreversibility/01_OPERATOR_DIRECTIVE_verbatim.md
sha256 f0dd0599cbf624847460eccac057c46798a808c9021770b33af00382f85fce4a,
issued 2026-09-25 to Aporia and Cyclops.

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T20:05Z Aporia[m1-cb5a6069]
OPERATOR DIRECTIVE TO ANANKE: PTE-SI01, the Causal-State Boundary Challenge. Written in Aporia's
voice and pasted by the operator to both Ananke and Aporia.
  path    roles/Aporia/prompts/2026-09-25_ananke_pte_si01/01_OPERATOR_DIRECTIVE_TO_ANANKE_verbatim.md
  sha256  25a81442caa497542ccb74f166d21b5ae7e1ebf85730c33afeb62609fd5f9278
Effect on memo Q3: ANSWERED. The HOLD ALL ACTIVITY stays in force (its s2). C1b runs BEFORE
PTE-SI01, under its own frozen prereg, with NO SI-derived endpoints (s3). Aporia communicates the
HOLD release (s2), the PTE-SI01 launch go (s25) and the GPU no-conflict confirmation (s24). No
RunPod spend (s24).
AUTHORITY SEAT: Aporia. The release criterion, fixed HERE, before any review arrives:
  Aporia releases the HOLD only when (1) both reviews, Kairos #564 and Elenchus #565, have
  returned, (2) Ananke has answered each on comms, and (3) no review finding invalidates C1b's
  design. If (3) is in doubt, Aporia asks the operator instead of releasing. The release is
  posted to Ananke and Cyclops by name and recorded here.
The PTE-SI01 go requires every s25 deliverable, plus Cyclops's concurrence (both are named in s1).

### 2026-09-26T05:45Z Aporia[m1-cb5a6069]
RELEASE-TOKEN RULE for Aporia (after the C1b guard defect, #695). Aporia puts HOLD and RELEASE together
in a comms SUBJECT only in an actual HOLD release. That release's subject begins with the exact
literal "C1B HOLD RELEASE:", its kind is "ruling", it names Ananke, and its body carries the freeze
SHA it releases. Background: the C1b driver's first guard accepted any Aporia subject containing
both words, and two of Aporia's non-release posts (#605, #631) would have launched C1b under the
HOLD. Found by testing the guard against real sent messages before any row existed.
The HOLD release criterion itself (20:05Z entry) is unchanged.

### 2026-09-26T06:50Z Aporia[m1-cb5a6069]
C1b launch-guard fix VERIFIED independently (Ananke #705, code 4554a2fae, FREEZE_C1b v2 at 5bd6c3945).
check_release(), called on real comms data with frozen_at as the driver derives it (git %cI, tz-aware):
#605, #631, #684 and #696 refused; a synthetic valid release accepted; a release naming the old freeze
d9528d5f6 refused. A valid release must therefore begin "C1B HOLD RELEASE:", be kind=ruling, be sent to
Ananke, be created after 2026-09-26T02:28:01-04:00, and name 5bd6c3945 in its body.
Minor robustness note (not blocking): a tz-naive frozen_at would raise an uncaught TypeError. That is
unreachable via the driver, and it fails closed.
The HOLD itself is unchanged; its 20:05Z criterion is still unmet (Kairos #564, Elenchus #565 unseen).
