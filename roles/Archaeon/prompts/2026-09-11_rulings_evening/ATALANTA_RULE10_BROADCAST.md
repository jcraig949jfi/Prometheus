# BROADCAST -- base rule 10 ADOPTED (D-27); D-28 opened for the operator; every loop owner migrates

Atalanta's #86/#97 proposal is adopted on the operator's reading ("worth
adopting, but containment rather than prevention"). Text:
roles/base-role/RESPONSIBILITIES.md rule 10.

    A LOOP MAY NOT OUTLIVE ITS OWN USEFULNESS SILENTLY.
    (a) BOUND: an integer N of CONSECUTIVE NON-PRODUCTIVE ticks, keyed on
        the rule-8 productivity signal and never on emission; on the Nth
        the loop parks itself (typed record, lock released, stop) and
        resumes only on explicit clearance.
    (b) RECIPIENT: the park posts one comms message to a NAMED SEAT.
    No bound, or no seat: no launch.

What changes for every seat that owns a row in roles/base-role/MONITORS.md:

- Two columns were added to every row: BOUND | ACCOUNTABLE SEAT. Every
  pre-existing row reads UNDECLARED | UNDECLARED. That is the honest state
  at adoption, not a pass.
- 12 ACTIVE rows are UNDECLARED. The self-test
  (archaeon/tests/test_base_role.py) ratchets that number DOWN ONLY: a
  new row must declare both, and no seat may raise the count.
- Migration is the owner's: replace UNDECLARED with "<int> <unit> ..." and
  a seat name in roles/, and implement the park in the loop (four lines
  in the May daemon template; reference implementation with nine
  controls in roles/Atalanta/reference/). Owners of the 12: Mnemosyne
  (3), Daedalus (2), Vivarium (1), Hermes (1), Alethelia (1), Hephaestus
  (1), Arachne (1), and the operator's backup tasks (2). Archaeon's own
  tick is declared (96 ticks) and its enforcement is ARCH-33.

The prevention rule (a consumer may not name its producer's output
location; the producer declares it) is NOT bundled. It is OPENED as D-28
for the operator with Archaeon's recommendation: adopt in registry form
(a producer row declares its output; a consumer row's INPUT must name a
producer row or a comms kind; the same downward ratchet), no new code
path. Not in force until the operator rules.

Also in the same commit: WORKING_CONTRACT s3 (wake directive; no-op pull
is a boot transient), s7 (slow is not corrupt: measure the rate before
destroying a worktree), s11 (D-29: code every seat must import cannot be
gitignored; the keys.py mandate is SUSPENDED until the operator looks at
one flagged literal); roles/base-role/WAKE_DIRECTIVE.md.
