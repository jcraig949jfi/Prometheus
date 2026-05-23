"""One-shot dispatcher for Techne ticket T-2026-05-22-techne-self-claims-001.

Reads the 48-claim file, dispatches 5 abstracted Pythia DR queries with
claim_id preserved in tags, writes a dispatch manifest for verdict-back
routing.
"""
import sys, json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, 'F:/Prometheus/scripts')
sys.path.insert(0, 'F:/Prometheus/aporia/scripts')
import agora_persist

DISPATCHES = [
    {
        "claim_id": "techne-claim-23965e3ab2c63d63",
        "topic": "H4 reward sparsity ceiling in compositional RL",
        "title": "TSC-01: Reward sparsity bounds in compositional RL with binary verifiable gates",
        "original_claim": (
            "H4 (reward sparsity ceiling): With ~12 binary gates in the kill-path, "
            "per-episode prior on PROMOTE <= catalog-size / |reachable-subspace|."
        ),
        "question": (
            "What does the 2024-2026 compositional / hierarchical RL literature say about "
            "expected episode-level reward sparsity when the success criterion is "
            "conjunction of M binary verifiable gates, and how do reachability bounds on "
            "the kill/proof subspace relate to per-episode promote priors? Discuss "
            "BC-Tree, ProofRL, retrosynthesis-RL, and theorem-proving-RL baselines."
        ),
    },
    {
        "claim_id": "techne-claim-4b06dcb777cfa54f",
        "topic": "Lehmer-conjecture enumeration in-band hit rates",
        "title": "TSC-02: Uniform polynomial enumeration in-band hit rates for Lehmer attacks (2024-2026)",
        "original_claim": (
            "Volume alone does not help the Learner -- uniform Lehmer enumerations are "
            "~99% in-band uninformative kills."
        ),
        "question": (
            "For uniform-random or systematic polynomial enumeration strategies targeting "
            "Lehmer's Mahler-measure conjecture, what does the 2024-2026 literature report "
            "on the fraction of candidates that are 'in-band' (near the Lehmer bound) vs "
            "noise? Cite Mossinghoff, Boyd, Smyth recent enumeration work and any "
            "kill-rate / yield data. Connect to the broader 'active-sampling vs "
            "uniform-enumeration' trade-off in computational number theory."
        ),
    },
    {
        "claim_id": "techne-claim-05b88b095e7c8d52",
        "topic": "Predictive BSD-feature regressions",
        "title": "TSC-03: Predictive feature engineering for BSD rank ML (2024-2026)",
        "original_claim": (
            "Rich BSD features (+45 features: regulator, real_period, faltings_height, "
            "abc_quality, szpiro, Tamagawa, torsion, CM/semistable) gave Linear-rich "
            "43.2% vs Linear-raw 46.X% on 75K BSD curves."
        ),
        "question": (
            "What predictive feature sets do recent (2024-2026) ML papers on elliptic "
            "curve rank / Mordell-Weil rank prediction find most informative? Specifically: "
            "do feature additions of regulator, real_period, Faltings height, abc-quality, "
            "Szpiro ratio, Tamagawa numbers, torsion structure, CM/semistable indicators "
            "measurably improve performance over baseline j-invariant / conductor / "
            "minimal-Weierstrass features in linear or tree-ensemble models? Cite "
            "Alessandretti-Buyukboduk-Yan, He-Lee-Oliver, and other recent BSD-ML literature."
        ),
    },
    {
        "claim_id": "techne-claim-0475398d38a4f1b3",
        "topic": "Proof-redundancy frameworks and independence classes",
        "title": "TSC-04: Proof-redundancy and independence-class taxonomies in automated verification",
        "original_claim": (
            "TriangulationProtocol now requires >=1 proof-bearing path + >=1 independent "
            "replay path with different `independence_class`."
        ),
        "question": (
            "How do contemporary (2024-2026) automated theorem verification / proof-checking "
            "frameworks define independence between proof paths? Survey: Lean mathlib's "
            "reproducibility audits, Coq's CompCert verification, formal-methods literature "
            "on N-version proof checking, and reverse mathematics work that classifies proofs "
            "by which axioms / methods they use. Is there a settled taxonomy of 'independence "
            "classes' for proof paths, or is this an open methodology problem?"
        ),
    },
    {
        "claim_id": "techne-claim-cd298621084c2b07",
        "topic": "Active sampling for falsification corpora",
        "title": "TSC-05: Active sampling vs uniform enumeration for falsification corpus construction",
        "original_claim": (
            "Without active sampling, 99%+ of records are in-band uninformative kills."
        ),
        "question": (
            "In computational mathematics where falsification is the primary substrate "
            "(Lehmer attacks, BSD rank checks, modularity verification), what does the "
            "2024-2026 literature say about active-sampling / curriculum strategies vs "
            "uniform random enumeration for building informative training corpora? Cover "
            "BOOST, ACTIVE-LEARNER-CRYPT, and any DeepMind / Google Research recent work "
            "on math-RL data curation. Distinguish 'informative kill' vs 'noise kill' "
            "metrics formally if literature does so."
        ),
    },
]

PROMPT_TEMPLATE = """This is a Techne self-claim verification query, dispatched via Aporia per ticket T-2026-05-22-techne-self-claims-001.

ORIGINAL TECHNE SELF-CLAIM (from pivot doc):
{original_claim}

ABSTRACTED LITERATURE QUERY:
{question}

Please produce a substrate-grade research brief following the Aporia 7-section template:
1. Brief summary - the question in one line.
2. Flagged findings - current consensus and where it might be wrong.
3. Problem statement - precise object/result being interrogated.
4. Status & bounds - last known status, current best bounds, conditional qualifiers.
5. Literature (primary sources) - arXiv IDs, journal cites, authors, dates. Primary only.
6. Attack vectors - live techniques; exhausted approaches.
7. Cross-references - related open problems, anti-anchors, candidate primitives.

Cite at least 2 of the 5 mandated calibration patterns where applicable:
PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.

The verdict back to Techne should indicate: does the literature confirm, falsify, or leave open the original self-claim's spirit?
"""


def main():
    now_iso = datetime.now(timezone.utc).isoformat()
    results = []
    for d in DISPATCHES:
        prompt = PROMPT_TEMPLATE.format(
            original_claim=d["original_claim"], question=d["question"]
        )
        queue_ref = f"TSC-{d['claim_id'].split('-')[-1][:8]}"
        rid = agora_persist.enqueue_research(
            title=d["title"][:300], prompt_text=prompt,
            requested_by='Aporia', priority=4, tier='T2',
            queue_ref=queue_ref, target_substrate_type='A',
            tags={
                'source': 'techne_self_claims_triage',
                'techne_claim_id': d['claim_id'],
                'techne_topic': d['topic'],
                'origin_ticket': 'T-2026-05-22-techne-self-claims-001',
                'verdict_back_to': 'aporia/meta/queue/techne_inbox.jsonl',
            },
        )
        results.append({
            'claim_id': d['claim_id'], 'queue_ref': queue_ref,
            'row_id': rid, 'title': d['title'],
        })
        print(f"  rid={rid}  {queue_ref}  ({d['claim_id'][:24]})")

    print()
    print(f'dispatched: {len(results)}')

    manifest_path = Path(
        'F:/Prometheus/aporia/meta/techne_self_claims_dispatch_manifest_2026-05-22.json'
    )
    manifest_path.write_text(json.dumps({
        'dispatched_at': now_iso,
        'origin_ticket': 'T-2026-05-22-techne-self-claims-001',
        'origin_file': 'techne/handoff/aporia_outbox/techne_self_claims_2026-05-22.jsonl',
        'total_claims_received': 48,
        'verifiable_by_pythia_as_written': 0,
        'abstracted_and_dispatched': len(results),
        'dispatches': results,
        'unverifiable_internal_count': 43,
        'note': (
            'All 48 claims are Prometheus-internal as written; 5 were abstracted into '
            'adjacent literature queries that preserve the spirit of the original claim. '
            'Verdict-back tickets to techne_inbox.jsonl on report receipt.'
        ),
    }, indent=2), encoding='utf-8')
    print(f'manifest: {manifest_path.name}')


if __name__ == '__main__':
    main()
