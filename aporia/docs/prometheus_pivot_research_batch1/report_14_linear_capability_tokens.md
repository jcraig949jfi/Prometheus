# Report 14 — Linear Capability Tokens / Object Capability Security

*Prometheus Pivot Research Batch 1 — 2026-05-02*
*Topic: Best practices and failure modes for linear capability tokens, drawing on KeyKOS / EROS / Capsicum / seL4 / Macaroons / Biscuit*

## 1. Situation

Prometheus's Σ-kernel (`F:\Prometheus\sigma_kernel\`) issues **linear capability tokens** — one-shot bearer authorizations consumed-by-use — to gate the privileged operations PROMOTE (lift a candidate claim into the canonical store), ERRATA (retract or amend a previously-promoted claim), and mint (create a new symbol/identifier in a reserved namespace). The threat model is multi-agent: Aporia, Charon, Ergon, Harmonia, Techne, future Apollo/Rhea, and external collaborators all hold credentials, run partly autonomously, and occasionally execute LLM-generated code that may be adversarial-by-confusion (prompt injection) rather than adversarial-by-malice. We need capability discipline that prevents a confused-but-authorized agent from corrupting the canonical store, while keeping the friction low enough that legitimate agent-to-agent delegation (e.g. Aporia asking Techne to mint a derivative symbol) does not require human mediation.

## 2. State of the Art

**KeyKOS / EROS / CapROS (capability-based microkernels).** Capabilities are *kernel-protected references* — opaque tokens that name an object and grant a fixed set of operations on it. Encoding: 128-bit slot index inside a kernel-managed C-list per process. Attenuation: a process can derive a *weaker* capability (fewer permitted ops, narrower object) and pass it to another process; the original is untouched. Revocation: via *revoker* objects — a layer of indirection where the holder of the revoker can atomically invalidate all derived capabilities. Persistence is checkpoint-based; capabilities survive reboot. Lessons: pure object-capability with no ambient authority is achievable; the C-list architecture is the gold standard for forgery resistance.

**Capsicum (FreeBSD capability mode).** Encoding: file descriptors decorated with a 64-bit rights bitmap (`cap_rights_t`). Once a process enters capability mode (`cap_enter()`), it loses access to global namespaces — no `open()`, no `bind()`, no `/proc`. Attenuation: `cap_rights_limit()` monotonically narrows an FD's rights. Revocation: close the FD; no out-of-band revoker. Lessons: ambient-authority elimination by *removing global namespaces entirely* is a powerful pattern; lack of revocation across forks is the operational pain point.

**seL4 (formally verified microkernel).** Encoding: capabilities live in CNodes (capability-storage nodes) with verified non-interference proofs. Attenuation: explicit `Mint` / `Derive` operations produce a child capability with a subset of rights, tracked in a CDT (capability derivation tree). Revocation: `Revoke` walks the CDT and atomically destroys all descendants. The seL4 contribution: machine-checked proof that capabilities cannot be forged or leaked outside their derivation tree.

**OAuth bearer tokens (the cautionary tale).** Encoding: opaque or JWT-encoded string; possession = authority. No attenuation (scopes are fixed at issuance). Revocation: server-side denylist or short TTL + refresh. Failure mode: a stolen bearer is indistinguishable from the legitimate holder — exactly the threat capability discipline is supposed to eliminate.

**Macaroons (Google, 2014).** Encoding: HMAC-chained list of **caveats** (predicates the verifier must check), keyed by a shared root secret. Attenuation: anyone can append a caveat (e.g. `time < 2026-05-01`, `agent = ergon`, `target_prefix = aporia/h15/*`) and re-MAC, *without* talking to the issuer. The new macaroon is strictly weaker. Revocation: short root-key rotation + caveat-encoded TTLs. **Third-party caveats** add discharge macaroons for federated authorization.

**Biscuit (Clever Cloud, 2020).** Macaroon's successor: caveats expressed in a Datalog dialect, signed with asymmetric keys (Ed25519) so that attenuation produces a *cryptographically auditable chain* — the verifier can prove which party added each restriction. Attenuation is offline; revocation is via TTL + revocation-id list.

**JWT vs proof-of-possession.** JWT is a signed bearer; PoP (RFC 7800) binds the token to a key the holder must prove ownership of (DPoP, MTLS-bound tokens). PoP defeats replay; JWT alone does not. For a bearer-style cap, an attacker who reads the token wire format gains the authority; for a PoP cap, they additionally need the binding key. Trade-off: PoP requires per-call signing; bearer is one-line cheap.

## 3. Patterns Prometheus Should Adopt

**(a) Biscuit-style attenuated capabilities.** Every Σ-kernel capability is an Ed25519-signed token whose payload is a small Datalog program. Holders can append further `check if ...` clauses and re-sign with their own key, producing a strictly-weaker derivative without contacting the kernel. The kernel verifies the full signature chain on use. Concrete example: Aporia receives a PROMOTE capability scoped to `domain=mathematics`. Before delegating to Techne for a sub-task she appends `check if symbol matches "mathematics/h15/*"` and `check if time < now+3600s`, then hands the attenuated capability to Techne. The kernel never had to mediate.

**(b) Macaroon-style contextual caveats — mandatory baseline.** Every kernel-issued capability ships with at least: `expires_at` (absolute timestamp, ≤ 1 hour by default), `agent_id` (the principal expected to present it), `target_pattern` (glob over the symbol namespace), `op` (PROMOTE | ERRATA | MINT), `nonce` (for one-shot linearity).

**(c) Confused-deputy prevention via pass-by-reference.** The kernel's PROMOTE/ERRATA APIs must accept a **capability that already names the target object**, never a separately-supplied `(capability, target_name)` tuple. The Confused Deputy Problem (Hardy 1988) arises precisely when authority and designation are decoupled. In code: `kernel.promote(cap)` not `kernel.promote(cap, symbol_name)` — the symbol is *inside* the cap, signed by the issuer, and cannot be re-aimed by the presenter.

**(d) Revocation via short TTL + rotation, not denylist.** Long-lived denylists scale O(revocations × verifications). Instead: cap TTLs ≤ 1 hour; an agent that needs continuing authority refreshes against the kernel; compromise containment window is bounded by TTL. Emergency revocation = rotate the kernel's root signing key; all outstanding caps die simultaneously. Maintain a tiny short-lived revocation set keyed by `nonce` for the in-flight window only.

**(e) Audit log of capability use, including the attenuation chain.** Every kernel verification records: root issuer, full chain of attenuators (Ed25519 public keys), final caveats, presenting agent, target, op, outcome. This is appended to the same Redis-Streams substrate as the artifact log (Report 11), so capability use is itself a first-class queryable history. Forensics after compromise reduces to "which caps did the compromised agent's key sign, and what were they used for?"

## 4. Failure Modes to Anticipate

**Confused deputy.** Mitigation: pass-by-reference (3c) plus refusal to accept "designation hints" alongside caps. An agent should never be able to say "use cap X on object Y"; the cap names Y itself.

**Ambient authority leakage.** Risk: capabilities placed in env vars, `~/.config`, or process globals get inherited by subprocess agents and LLM tool calls that should not have them. Mitigation: caps are passed only via explicit kernel-ABI calls; never read from environment; child agent sandboxes inherit *no* caps unless explicitly delegated; lint rule `no-cap-in-env` in CI.

**Capability proliferation.** N agents × M attenuations × T time → unbounded cap inventory in flight. Mitigation: short TTLs (forced collection by expiry) and a per-agent cap budget (max 100 outstanding caps; oldest evicted).

**Revocation lag during compromise.** Even with 1-hour TTLs, an attacker has up-to-an-hour to PROMOTE garbage. Mitigation: (i) PROMOTE requires a second-factor "promotion witness" from a different agent for high-impact namespaces (canonical math claims); (ii) anomaly-detection on PROMOTE rate per agent; auto-rotate root key on threshold breach.

**TOCTOU races.** A cap is checked, then between check and use the underlying object changes (a symbol gets ERRATA-d). Mitigation: caps name a *content-addressed* parent CID (Report 11). The kernel verifies the parent CID still exists at use time; if the namespace head moved, the cap holder must rebase and re-issue.

**Discharge oracle abuse (third-party caveats).** Avoid third-party caveats in v1; the discharge-macaroon dance enlarges the trust boundary unnecessarily.

## 5. Concrete Schema Proposal for Kernel Extension

```
SigmaCapability {
  version: u8 = 1,
  cap_id: uuid,                    // unique, for audit/revocation
  root_issuer: ed25519_pubkey,     // kernel root key id
  op: enum { PROMOTE, ERRATA, MINT },
  target_pattern: string,          // glob over symbol namespace
  parent_cid: multihash,           // content-addressed pin for TOCTOU
  expires_at: u64,                 // unix seconds, <= now + 3600
  agent_id: string,                // expected presenter
  nonce: bytes16,                  // one-shot linearity token
  caveats: [DatalogClause],        // appendable, biscuit-style
  signature_chain: [Ed25519Sig],   // root + each attenuator
}
```

Kernel verification: signature chain valid, `expires_at > now`, `agent_id == authenticated_caller`, `target ⊆ target_pattern`, `parent_cid` resolves, all caveats satisfied, `nonce` not in recent-use set; on success, mark `nonce` consumed.

## 6. References

1. Hardy, N. *The Confused Deputy*. ACM OSR, 1988.
2. Shapiro, J. et al. *EROS: A Fast Capability System*. SOSP 1999.
3. Hardy, N. *KeyKOS Architecture*. ACM OSR, 1985.
4. Watson, R. et al. *Capsicum: practical capabilities for UNIX*. USENIX Security 2010.
5. Klein, G. et al. *seL4: Formal Verification of an OS Kernel*. SOSP 2009.
6. Birgisson, A. et al. *Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud*. NDSS 2014.
7. Clever Cloud. *Biscuit: a bearer token with offline attenuation and authorization policies*. 2020. https://www.biscuitsec.org
8. Miller, M. *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control*. PhD thesis, JHU, 2006.
9. Levy, H. *Capability-Based Computer Systems*. Digital Press, 1984.
10. Jones, M., Bradley, J., Sakimura, N. *RFC 7519: JSON Web Token (JWT)*. 2015.
11. Jones, M. et al. *RFC 7800: Proof-of-Possession Key Semantics for JWTs*. 2016.
12. Fett, D. et al. *RFC 9449: OAuth 2.0 Demonstrating Proof of Possession (DPoP)*. 2023.
13. Tanenbaum, A. *Amoeba capabilities*, in *Distributed Operating Systems*, 1995.
14. Yee, K-P. *User Interaction Design for Secure Systems*. ICICS 2002.
15. Shapiro, J., Hardy, N. *EROS: A Principle-Driven Operating System from the Ground Up*. IEEE Software, 2002.
16. seL4 Foundation. *The seL4 microkernel: An introduction*. Whitepaper, 2020.
17. Stiegler, M. *The E Language in a Walnut*. (Object-capability semantics, distributed.)

Word count ~1180
