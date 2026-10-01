# 2026-10-01 charter

The operator's charter for Dionysus, given in chat on SKULLPORT (M1) on
2026-10-01 in two messages, both verbatim here as received (spacing
unedited):

- 02_OPERATOR_LOCATE_DIRECTIVE_verbatim.md (about 13:40Z): find the
  Phase 3 architect prompt. The second paragraph is text the operator
  pasted from another session; it is recorded as pasted.
- 01_OPERATOR_CHARTER_verbatim.md (about 14:15Z): the charter itself.
  Design an architecture for Prometheus v3, with freedom to stray from
  the prompt.

The prompt the charter refers to is NOT copied here. It is already on
main, verbatim, as docs/phase3/PHASE3_ARCHITECT_PROMPT.md:

    commit   d2e2e86a3b9890c5e05b999dcbd0657eb1969d2b
    blob     77ecbfa4770cb2d1781d187dccf42098f0f26e9a (29771 bytes, LF)
    sha256   c65f4ed72774128d6a04c094969e73097b2632f9b8977f5deab5a5ccb253ac07

Verified by this seat at 2026-10-01T13:40Z: the sha256 of the committed
blob at d2e2e86a3 and at origin/main equals the value the operator
pasted. A CRLF working copy hashes differently; the blob is the
authority (base role s4, MANIFESTS).

Facts the charter fixes:

- Identity for the prompt's IDENTITY slot: FABLE-5.1. The operator set
  the session to Fable 5.1 (model id claude-fable-5-1) at maximum effort
  before issuing the charter. The creation pass earlier the same day ran
  on Opus 5.5 in the same session (instance tag m1-3815a3b9 unchanged).
- Output directory, from the prompt s20: docs/phase3/design/FABLE-5.1/.
- Independence, from the prompt: this seat does not seek, read or use the
  Phase 3 design conclusions of any other architect.
- Latitude: the charter says the prompt is a brainstorm (operator and
  ChatGPT 5.6) and that this seat may depart from it. Departures are
  listed in the package, each with its reason.

Committed before any design output so the order is in git history.
