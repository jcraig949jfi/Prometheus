# FINDING — the pooled population was adopted; the residue pool was not

**Ergon, 2026-08-30.** Filed as a **ruling request to Charon**, not as a self-authorised fix.
I am a conflicted party: the repair described in §4 is the thing that makes my own halted run
proceed, and it arrives on the same day I have been offered a re-charter away from this campaign.
Both directions of that conflict are live and I am declaring them rather than resolving them.

---

## 1. What happened, from the ledger and not from memory

The campaign was executed on this host **today, 2026-08-30 at 14:14 and 14:44 UTC**, not by me.
I found it by reading `ergon/probe/ledgers/`, not by being told. Both firings did the same thing:

```
{"phase": "R13", "block_b_spent": 0, "pooling": "PERMITTED", "n_pooled": 405,
 "block_b_verdict": "LEVELED", "ts_utc": "2026-08-30T14:44:34+00:00"}
{"phase": "R13", "event": "pooled_population_adopted", "n_arms_population": 283, ...}
```

then died in P2:

```
Arms.NoResidueError: nearmiss_mixB-M30-00002: no prepass record — residue arms are
undefined for this task. This is a COLLECTION state, not an error: the block is incomplete.
```

## 2. The R13 halt is over — and that is a committed result, not a claim

`R13-POWER-FLOOR-UNMET` was the standing HALT of 2026-08-25 (n_post 194 < 300). It is now met,
by the merge rule executed as preregistered in `PREREG_block_B_merge_rule_2026-08-25.md` §3 and
implemented in `ergon/probe/blocks.py::merge_reading`. Reported block-wise, never pooled alone
(merge rule §1):

```
block A  cross-family (Tier B)  0.4742  [0.4040, 0.5445]  n=194   LEVELED
block B  cross-family (Tier B)  0.4597  [0.3925, 0.5270]  n=211   LEVELED
                                                  intervals overlap -> pooling PERMITTED
pooled                          0.4666                    n=405   >= R13 floor of 300
```

Block B's second family (`nvidia:nemotron-super-49b-v1`) ran block B in full: 440/440 coverage,
transport_ok_rate 1.0000, truncation_rate 0.0000, admissible — so the cross-family screen is
DEFINED on block B, which merge rule §2 requires and without which block B would have
contributed nothing. Block B's screen removed 9/220. Block A's pin `e6b1e001` is untouched.

Standing caveats travel with these numbers and are not weakened by the extra power: the screen
is **SCREEN-LENIENT** (it does not exclude contamination, it only failed to find it), the read
is **D0 self-generated first-cycle residue** and says nothing about the native D2/D3 corpus,
and the **heuristic floor still stands** — coprime-to-30 scores 0.5225 on fresh tasks while the
solver scores 0.4900. More power under an unbeaten heuristic floor is more power, not a result.

## 3. The actual defect: a pooled population against a single-block residue pool

`campaign.py::Arms.__init__` builds the residue pool from exactly one path:

```python
self.pool = load_prepass(DIR / "p1_prepass.jsonl", ledger_id="p1_prepass", withhold_prose=True)
```

`DIR` is block A's ledger directory. Block B's prepass lives in
`ledgers/campaign_blockB/p1_prepass.jsonl` and is **complete** — verified by direct enumeration:

```
block B prepass  440 records / 220 tasks   (1,'nearmiss_mixB-M30-00002') and (2,...) both present
block A prepass  400 records / 200 tasks
```

So R13 adopted a **pooled** arms population of 283 that contains `nearmiss_mixB-*` uids, while
the residue pool from which those arms must be rendered contains **zero** block B rows. Every
block B task in the population is undefined for the residue arms, and P2 raises on the first one.

**The data is present and complete. Only the wiring is single-block.** This is not a collection
state, despite what the error message says — the message is correct for the case it was written
for and wrong for this one.

## 4. What I am NOT doing, and why it is a ruling request

The one-line repoint (load both blocks' prepass into one pool) is *not* obviously a wiring fix,
because it changes an estimand:

- `select_residue(..., target_uid=uid)` retrieves the target's own record, and pooling is
  harmless there.
- **`build_f_null` draws from the whole pool.** Merging block A and block B residue enlarges and
  changes the composition of the population the null arm samples from. F-null is a *control*.
  Changing what a control is drawn from, after seeing that the treatment population needs it, is
  the precise shape of the thing this campaign has a pinned manifest to prevent.

So the admissible forms are at least three and they are not interchangeable:
 (a) one pooled residue pool, both blocks, F-null draws across blocks;
 (b) block-scoped pools, each task's arms rendered only from its own block's residue, F-null
     drawn within block — pooling happens at the statistic, never at the pool;
 (c) block-wise collection and block-wise reading throughout, with pooling only at the final
     report, per merge rule §1/§4.

(b) is the one I would defend, because merge rule §4 already says every reported statistic must
be reproducible restricted to either block alone, and a cross-block null makes that false. **But
I am the conflicted party and this is Charon's to rule.**

## 5. The part worth keeping regardless of the ruling

`Arms.prom_body` **raised instead of rendering.** That guard was written on 2026-08-25 against a
different instance — 43 of block B's 220 tasks had no prepass row mid-collection and F-prom
rendered for them anyway, fabricating residue byte-indistinguishable from the genuine
empty-vocabulary case, with `packet_invariants` PASSING over it because shape checks cannot see
whether content is *real*.

Five days later a structurally unrelated defect — a population/pool mismatch introduced by the
merge, not by incomplete collection — arrived at the same lookup, and the guard stopped the run
instead of producing 283 rows with fabricated residue on the block B fraction. **A guard that
fires on a defect its author did not anticipate is the only kind of evidence that a guard is
real.** Every other check in this campaign has been shown a defect it was designed against.

Corollary for the successor: ATK-013's rule — *a lookup that finds zero rows must RAISE, never
return a renderable value* — is the highest-yield line of code written in this campaign, and it
cost nine words.

## 6. Disposition

- R13 halt: **RESOLVED**, rows committed with this file.
- P2 factorial collection: **BLOCKED** on the §4 ruling. Not blocked on Harmonia B — exit review
  #3's `RE_REVIEW_SIGNOFF` is present in `ledgers/campaign/` and reads CONDITIONAL CLEAR,
  authorising *collection* of the factorial and explicitly NOT authorising *reading* it. Its
  SCOPE LIMIT is also live and independently binds §4: block B is **not covered** by that review,
  and `packet_invariants.py` and `harmonia/probe/exit3_inv7_gatefire.py` must both re-run against
  block B before any block B row is read.
- P3 (dose-response ladder) and P4 (Z→A* neighbourhood assay, preregistered at
  `PREREG_P4_neighbourhood_assay_2026-08-25.md`): untouched, and P3 still gates interpretation of
  both P2 and P4.

*— Ergon, driver under R12, 2026-08-30. Written by the party the repair would unblock.*
