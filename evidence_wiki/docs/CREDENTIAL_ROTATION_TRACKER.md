# Credential rotation tracker (Mnemosyne)

Opened 2026-09-08. Standing register of credential exposures Mnemosyne is
aware of, their verified status, and who must act. Rotation itself is operator
action: nothing here can rotate a secret that other hosts and clients hold.

**Reporting rule for this file: redacted status only.** Never a key, never a
prefix, never a length that identifies one, never a vendor named against a
live value. Counts and classes only. A tracker that quotes the material is a
second copy of the leak.

| id | what | verified status | owner | state |
|----|------|-----------------|-------|-------|
| R-1 | PEW `machine_tokens`, `auth_token`, `db_password` committed in `evidence_wiki/config.json` | present in git history; every host holding the repo can authenticate as any machine | operator | OPEN |
| R-2 | `config.local.json` (documented credential override) was not gitignored until 2026-09-05 | closed preventively at the tracked repo root; any secret placed in that filename **before** 2026-09-05 was committable and should be treated as exposed | Mnemosyne (rule) / operator (any pre-date secret) | PREVENTED, residual unknown |
| R-3 | key-shaped strings in an untracked archive report (Archaeon assets audit §13) | see below | operator | OPEN, low urgency |

---

## R-1 — PEW credentials in git

Raised by the V3/closure credential ruling (`CLOSURE_PACKET_2026-09-04.txt`
§3). The committed cleartext remains a working default by design so M1 and M2
keep running; an operator moves real secrets to env vars or
`config.local.json` with no code change, precedence
`env > config.local.json > committed config.json`.

Because they have lived in git history, the tokens should be treated as
compromised and rotated. Removal must happen **simultaneously on M1 and M2**
(both read the same file) or the machine without the new secret source breaks.

Provenance impact: none any more. Host identity is server-attested from the
Postgres cluster `system_identifier`, so a shared token no longer implies a
shared host.

## R-2 — the override filename was not ignored

`ew/db.py` documents `config.local.json` as the untracked override; only
`config.local.yaml` was listed at the repo root, so a real secret placed under
the documented name could have been committed. Closed 2026-09-05 by adding the
rule to the **tracked root** `.gitignore` — a nested `evidence_wiki/.gitignore`
does not work, because `.git/info/exclude` hides nested ignore files and is
machine-local, so the rule would have protected M1 only.

Residual: whether any host wrote a real secret to that filename before
2026-09-05 is unknown to me and is checkable only on each host.

## R-3 — archive report key prefixes (routed 2026-09-08)

Source: Archaeon assets audit, `archaeon/docs/expansion/ASSETS.md` §13, which
records a live security finding from `SUBSTRATE_C_ARCHAEOLOGY.md`
("Treat as exposed; rotate").

Verified by Mnemosyne 2026-09-08 under the authorised workflow, counts only:

    path cited by the audit ....... not present as cited
    path actually on disk ......... one directory deeper than cited
                                    (a doubled `bitfrost-core/` segment)
    tracked by git ................ NO
    gitignored .................... YES
    present on origin/main ........ NO
    commits touching it ........... 0  (never committed)
    key-shaped occurrences ........ 5, across 4 distinct vendor classes
    length classification ......... 0 full-length-shaped; 5 prefix-shaped
    file self-describes exposure .. no (that language is in the audit's
                                    source document, not in this file)

**Assessment.** Exposure surface is local disk on this host only — not git
history, not the remote, not any packet. The material is prefixes, not
full-length keys, so it does not by itself authenticate anything. Rotation
remains warranted because a prefix plus a vendor identifies which key to
attack and confirms the key existed; urgency is LOW rather than immediate.

**Correction owed to Archaeon:** the path in ASSETS.md §13 does not resolve as
written; the file sits one directory deeper. Worth fixing so a future reader
does not conclude the finding was stale.

**Not a dependency** of any research item, per the routing order.
