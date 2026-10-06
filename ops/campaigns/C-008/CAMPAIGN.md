# C-008 -- Lane C: synthetic-epoch commodity fabric (R-EP D1-D5)

Thread TH-MOON-M4, Epic EP-MOONSHOT. Coordinator and owner: Themis. Opened 2026-10-06 under OP-LC1
(roles/Themis/prompts/2026-10-06_op_lc1/). CAMPAIGN.json says what; this says why.

## Why

Moonshot's science will run as shard epochs on cheap, flaky machines. Before any evolutionary
population rides on that plane, the plane itself must be shown to give exactly one published
successor per parent under every fault we can name, with identity that survives a change of
transport, and its cost must be measured against bounds frozen in advance. Lane C does that with
SYNTHETIC epochs (deterministic CPU busy-work), so no scientific question is at stake while the
infrastructure is built.

## Contract

moonshot/epoch/CONTRACT.md, frozen before the tests. Its two load-bearing rules come from OP-LC1: the
git commit SHA is transport identity (semantic identity = SHA-256 over canonical inputs, spec, runtime
and outputs), and a successful CAS is PUBLISHED, not accepted -- validation is a separate state, and a
disagreement fails closed (taint until deterministic replay resolves it).

## Tasks

- T001 D1+D2 under the D3 matrix (test-first; the RED commit precedes the implementation).
- T002 D4 preregistration (bounds frozen and pushed before any baseline).
- T003 D4 local baseline: single-ref vs per-chain, disposable LAN bare remote, epoch-duration sweep.
- T004 D4 GitHub arm: dedicated repo, repo-scoped credential, <=2 workers, <=250 write attempts.
- T005 D5 node auto-join without auto-authorization.

## Bounds on this campaign

Local unpaid compute inside MWO-0004 R2. No traffic to the Prometheus repository or its ref namespace.
GitHub only as T004 allows. M4 gates nothing else in Moonshot or the RSO (OP-LC1); native distributed
reproductive populations stay out of scope until D3/D4 establish the semantics.
