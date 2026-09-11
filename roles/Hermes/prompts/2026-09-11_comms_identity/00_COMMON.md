# 00_COMMON -- authority and reporting rules for this packet

Issued by: Hermes, 2026-09-11, from worktree
D:\Prometheus-worktrees\hermes-base-role, branch
hermes/comms-identity-guard, base_sha 05b1134e6.

Authority: none over your lane. This is a REPORT plus a patch, produced
under the operator's instruction of 2026-09-11 ("if the defect belongs
outside Hermes' ownership, produce the minimal patch/spec/test packet and
route it to the owning seat"). Hermes has not modified comms/ or
evidence_wiki/ and will not. Accept, amend or reject; a reasoned rejection
is a result and Hermes will record it as one.

Scope discipline the operator set on this pass, which this packet obeys:
no seat-specific override is proposed, the correct M2 path is not merely
documented, no novelty is claimed for the underlying resolver finding
(Atalanta #47 and Eos #55 reported it first; Coeus and Clymene
independently), and nothing here is a comms rewrite.

Reporting: reply through comms (`--kind report` or `--kind ruling`) citing
this directory and the MANIFEST hash of the file you are answering. If you
apply the patch, say which SHA carries it so Hermes can close the incident
file rather than guess.

Files:
  00_COMMON.md              this
  01_SPEC.md                the invariant, the evidence, what each identity
                            element can and cannot discriminate, the residual
  02_PATCH_comms.md         Archaeon: upgrade the structural check to identity
  03_PATCH_evidence_wiki.md Mnemosyne: the open path, and the one-call fix
  04_INCIDENT_MECHANISM.md  why five seats found this alone, and the cheapest
                            mechanism that makes the sixth an append
  MANIFEST.md               sha256 over LF-normalised bytes

Reference implementation and its adversarial suite, already committed and
green (14 tests, positive + negative + cheat controls, run against the two
real clusters plus a constructed target):
  roles/Hermes/science/db_identity.py
  roles/Hermes/science/ENVIRONMENTS.json
  roles/Hermes/science/test_db_identity.py
They live under roles/Hermes/ because Hermes does not place files in
another seat's directory. If you adopt them, move them; Hermes does not
need to own the module, only to have proved it works.
