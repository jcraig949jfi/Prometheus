# Project Moonshot -- Economics Appendix v1 (2026-10-05)

VERSIONED, and deliberately OUTSIDE the scientific contract (MOONSHOT_DESIGN_v0.2.md): cloud
prices decay faster than the design. Re-verify before any launch; fix the dollar cap at launch
from fresh first-party prices. Hyperscaler figures below are mid-2026 third-party tracker
snapshots, NOT live first-party reads; spot prices are live-market and volatile. RunPod figures
are from RunPod's own pricing page. No numbers here authorize spend -- spend is gated by the
design (R13/N6) and by explicit operator authorization.

## Why economics barely gate this project
Paid compute is reached only after a passed local gate + the required reachability level (RC2
for a scout). The dominant, cheapest work is the CPU wide tier that runs first and decides
whether the expensive tier is ever authorized. The cost question is "has this candidate earned
the next tier," not "can we afford to keep searching."

## Indicative $/GPU-hour (cheapest-first; RunPod first-party, hyperscaler = trackers)
| GPU | RunPod community | Hyperscaler spot | Hyperscaler on-demand |
|---|---|---|---|
| L4 (24GB) | $0.44 | ~$0.44 (AWS g6) | $0.71-0.80 |
| RTX 4090 (24GB) | $0.34 | n/a | n/a |
| A40 (48GB) | $0.35 | n/a | n/a |
| A100 80GB | $1.19 | ~$0.82-2.5 (volatile) | $3.4-4.4 |
| H100 80GB | $1.99 | ~$2.1-3.8 | $6.9-12.3 |

CPU wide tier (where the real leverage is): spot ~$0.005/vCPU-hr vs ~$0.034 on-demand.
RunPod bills per-second with $0 egress (the headline advantage); GCP egress $0.12/GB is worst.

## Worked scenarios (assumptions stated; spot carries interruption risk, mitigated by R-EP replay)
- Scout (~100 GPU-h, L4/A40): ~$35-85; RunPod community ~$36-44.
- Campaign (~2,000 GPU-h, A100-class): RunPod on-demand ~$2,400-3,200 all-in, no interruptions;
  hyperscaler on-demand $6,800-8,800; hyperscaler spot $1,600-6,200 but near-certain
  interruptions over weeks.
- Large cloud-only (20k-50k GPU-h): RunPod/neocloud A100 ~$16k-60k; RunPod H100 ~$40k-100k;
  hyperscaler on-demand $170k-205k (a 3-5x SLA markup an evolutionary search does not need).
- CPU-fleet alternative (the wide tier): 1,000 vCPUs for a month on spot ~= $3.6k-8.8k for
  ~730,000 vCPU-hours. Budget the bulk of the search here; reserve GPU for confirmation.

## Cost traps
1. Per-job overhead dominates the wide tier -- batch thousands of episodes per long-lived
   worker (one epoch covers many episodes, R-EP), never one VM per episode.
2. Egress -- keep results in-cloud, export only summaries (RunPod $0; GCP worst).
3. Spot interruptions over multi-week A100/H100 runs are near-certain -- R-EP checkpoint replay
   turns an interruption into a cheap resume, so spot is usable because of, not despite, our
   determinism requirement.
4. Idle on-demand and standing storage accrue silently.

## Sourcing / soft flags (verify at launch)
RunPod pricing page (first-party, reliable). Hyperscaler GPU numbers = holori/spheron/
intuitionlabs/cloudzero/ecorpit trackers, May-Sep 2026. Could-not-verify: RunPod A4000 and
RunPod CPU-pod $/vCPU-hr; Azure L4; GCP L4 spot (~$0.62 looked anomalous). Spot everywhere is
indicative only.
