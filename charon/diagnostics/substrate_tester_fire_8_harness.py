"""Substrate-Tester Fire #8 harness — Lane 11 batch-sweep.

Per PRESSURE_PROMPTS_v1.md Pressure-applier 23: 30 probes total (15
adversarial + 15 real-paper) drawn uniformly from landed Harmonia
corpora, submitted through the substrate, scored against expected
verdicts.

Deterministic seed: 20260507_12 (fire-timestamp-derived).

Substrate ingestion: uses SigmaKernel.CLAIM directly (DiscoveryPipeline
is Lehmer-only). Each probe is mapped to a CLAIM payload.

Outputs:
  charon/diagnostics/substrate_tester_fire_8_results.json
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from sigma_kernel.sigma_kernel import SigmaKernel, Tier


CORPORA = [
    Path("aporia/meta/pressure_appliers/corpora/harmonia_b_dynamics_v1.json"),
    Path("aporia/meta/pressure_appliers/corpora/harmonia_d_logic_v1.json"),
    Path("aporia/meta/pressure_appliers/corpora/harmonia_e_complexity_v1.json"),
]

SEED = 20260507_12
N_ADVERSARIAL = 15
N_REAL_PAPER = 15


def load_corpora():
    """Load all three landed corpora; return list of (corpus_id, payload_dict)."""
    out = []
    for path in CORPORA:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        out.append((path.name, d))
    return out


def sample_probes(rng: random.Random, corpora):
    """Sample 15 adversarial + 15 real-paper, drawn uniformly across landed corpora."""
    all_adv = []
    all_rp = []
    for cid, d in corpora:
        for p in d.get("adversarial", []):
            all_adv.append((cid, p))
        for p in d.get("real_paper", []):
            all_rp.append((cid, p))
    rng.shuffle(all_adv)
    rng.shuffle(all_rp)
    return all_adv[:N_ADVERSARIAL], all_rp[:N_REAL_PAPER]


def submit_probe(kernel: SigmaKernel, probe_kind: str, corpus_id: str, probe: dict) -> dict:
    """Map probe to a CLAIM payload and submit via SigmaKernel.CLAIM.
    Returns result dict with the submission outcome."""
    pid = probe.get("id", "unknown")
    target_name = f"{probe_kind}__{pid}"
    if probe_kind == "adversarial":
        hypothesis = probe.get("probe", "")[:500]
        evidence = {
            "use_case": "adversarial",
            "expected_answer": probe.get("expected_answer", "")[:200],
            "trap_pattern": probe.get("trap_pattern", "")[:200],
            "domain": probe.get("domain", ""),
            "subdomain": probe.get("subdomain", ""),
        }
        kill_path = "expected_REFUSAL"
        expected = "REFUSAL"
    else:  # real-paper
        cps = probe.get("claim_payload_for_substrate", {})
        hypothesis = (
            f"{cps.get('subject', '')} :: {cps.get('predicate', '')}"
        )[:500]
        evidence = {
            "use_case": "real-paper",
            "claim_type": cps.get("claim_type", ""),
            "verification_anchor": cps.get("verification_anchor", "")[:200],
            "arxiv_id": probe.get("arxiv_id", ""),
            "category": probe.get("category", ""),
            "domain": probe.get("domain", ""),
        }
        kill_path = f"expected_{probe.get('expected_substrate_verdict', 'UNKNOWN')}"
        expected = probe.get("expected_substrate_verdict", "UNKNOWN")
    try:
        claim = kernel.CLAIM(
            target_name=target_name,
            hypothesis=hypothesis,
            evidence=evidence,
            kill_path=kill_path,
            target_tier=Tier.Conjecture,
        )
        return {
            "probe_id": pid,
            "kind": probe_kind,
            "corpus": corpus_id,
            "expected": expected,
            "submitted_ok": True,
            "claim_id": claim.id,
            "claim_status": claim.status,  # likely "pending"
            "claim_kill_path": claim.kill_path,
            "verdict": str(claim.verdict) if claim.verdict else None,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "probe_id": pid,
            "kind": probe_kind,
            "corpus": corpus_id,
            "expected": expected,
            "submitted_ok": False,
            "error_type": type(e).__name__,
            "error_message": str(e)[:200],
        }


def run() -> dict:
    rng = random.Random(SEED)
    corpora = load_corpora()
    adv_probes, rp_probes = sample_probes(rng, corpora)

    kernel = SigmaKernel(":memory:")

    results = []
    for cid, p in adv_probes:
        results.append(submit_probe(kernel, "adversarial", cid, p))
    for cid, p in rp_probes:
        results.append(submit_probe(kernel, "real-paper", cid, p))

    summary = {
        "fire": 8,
        "lane": 11,
        "seed": SEED,
        "n_adversarial_sampled": len(adv_probes),
        "n_real_paper_sampled": len(rp_probes),
        "n_submissions": len(results),
        "n_submitted_ok": sum(1 for r in results if r["submitted_ok"]),
        "n_submission_failed": sum(1 for r in results if not r["submitted_ok"]),
        "n_with_verdict": sum(
            1 for r in results
            if r.get("submitted_ok") and r.get("verdict") is not None
        ),
        "results": results,
    }

    out_path = Path("charon/diagnostics/substrate_tester_fire_8_results.json")
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(
        f"submitted_ok: {summary['n_submitted_ok']}/{summary['n_submissions']}, "
        f"with_verdict: {summary['n_with_verdict']}"
    )
    return summary


if __name__ == "__main__":
    run()
