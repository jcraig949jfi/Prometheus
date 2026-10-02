# Hardening Round Review Charter

Review Phase 3 Hardening v0.2 and its executable harness.

This is not primarily another ideation round. Attack whether the gates actually prevent the failure modes they claim to prevent.

Run:

```bash
cd harness
python -m unittest discover -v
```

Required attacks:

1. Add at least five deliberate mutants the harness should reject.
2. Try to make a physics-specific ruler masquerade as shared.
3. Try to make incomplete reset pass qualification.
4. Try to make repair reach masquerade as cold discovery.
5. Remove one required evidence facet and attempt claim promotion.
6. Attack the nested-compiler/R8 gate.
7. Attempt to construct a genuine positive for strong recursive improvement.
8. If no positive can be defined without smuggling the answer, say so.
9. Identify harness assumptions that privilege R1/R2 over R3/R4/R5.
10. Verify BLOCKED/UNQUALIFIED is distinct from FAIL.

Return:

- BUILD / REPAIR / REFRAME verdict;
- harness escapes;
- mutants added;
- tests suitable for production CI;
- misleading/overfit tests;
- design changes;
- architecture allocation changes;
- strong-recursion qualification status;
- smallest next experiment.
