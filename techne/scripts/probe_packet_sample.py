"""Emit sample F-prom packets from REAL substrate residue (Techne, assembler contract).

Proof-on-real-data companion to the unit suite: the acceptance tests prove the guards fire on
fixtures; this proves the assembler runs end-to-end on the frozen D3 pool and the live forge /
signature-index ledgers, with the firewall armed and the stamps populated.

Deterministic: same pool + same seed -> byte-identical packets (sha256 printed).

Usage:
    python -m techne.scripts.probe_packet_sample --pool pivot/probe_d3_pool_2026-08-16.jsonl \
        --outdir pivot/probe_packet_samples_2026-08-16
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ergon.probe import assemble as A  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]


def pool_records(path: pathlib.Path) -> list[A.ResidueRecord]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        null_fields = tuple(
            f for f in ("kill_pattern", "kill_vector", "step_trace", "method")
            if not d.get(f)
        ) + ("kill_vector",)
        body = (
            f"  claim: {d.get('canonical_claim_text')}\n"
            f"  kind: {d.get('claim_kind')}\n"
            f"  kill_pattern: {d.get('kill_pattern') or '(null)'}"
        )
        if d.get("method"):
            body += f"\n  method: {d['method']}"
        if d.get("step_trace"):
            body += f"\n  trace: {d['step_trace']}"
        out.append(A.ResidueRecord(
            ledger_id=d["ledger_id"], seq=int(d["seq"]), source="theseus_corpus",
            record_id=d.get("record_id") or "?", body=body, domain="theseus",
            obstruction_class=d.get("obstruction_class"),
            null_fields=tuple(sorted(set(null_fields))), sampling=d.get("sampling", "unknown"),
        ))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="pivot/probe_d3_pool_2026-08-16.jsonl")
    ap.add_argument("--outdir", default="pivot/probe_packet_samples_2026-08-16")
    ap.add_argument("--per-packet", type=int, default=25)
    args = ap.parse_args()

    outdir = REPO / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    theseus = pool_records(REPO / args.pool)
    forge = A.load_forge_scraps(REPO / "agents" / "hephaestus" / "ledger.jsonl")
    sig = A.load_signature_classes(REPO / "theseus" / "orchestration" / "signature_index.sqlite")

    native = A.select_residue(theseus + forge + sig, stratum="D3")
    # τ(T) is a snapshot of LEDGER EXTENT at the cutoff, not of the selected subset — it must
    # cover every record any packet may cite, including the F-prom-whole signature_index
    # prefix. Deriving it from the filtered pool made the firewall fire on the first real run,
    # which is the guard working: a cutoff narrower than the citation set is a real defect.
    tau = A.tau_from_records(list(native) + list(sig))

    manifest = []

    # Three D3 retrieved packets over disjoint deterministic slices of the ordered pool.
    for i in range(3):
        chunk = native[i * args.per_packet:(i + 1) * args.per_packet]
        p = A.assemble_retrieved(
            task_uid=f"SAMPLE-D3-{i+1}", stratum="D3", records=chunk, tau=tau,
            excluded_transport_failures=2861,
            sampling_note="theseus: stratified across 265 batches (byte-offset + gz-head, "
                          "stamped per record); forge/signature_index: full scan",
        )
        (outdir / f"D3_sample_{i+1}.txt").write_text(p.text, encoding="utf-8")
        manifest.append({"file": f"D3_sample_{i+1}.txt", "arm": "F-prom-retrieved",
                         "tokens": p.header["token_count"], "sha256": p.sha256,
                         "records": len(p.header["source_record_ids"]),
                         "truncated": p.header["records_truncated_to_fit"]})

    # One F-prom-whole with the signature_index in cacheable-prefix position.
    whole = A.assemble_whole(
        task_uid="SAMPLE-WHOLE-1", stratum="D3", prefix_records=sig,
        records=[r for r in native if r.source != "signature_index"][:400], tau=tau,
        solver_context_tokens=1_000_000, excluded_transport_failures=2861,
    )
    (outdir / "WHOLE_sample_1.txt").write_text(whole.text, encoding="utf-8")
    manifest.append({"file": "WHOLE_sample_1.txt", "arm": "F-prom-whole",
                     "tokens": whole.header["token_count"],
                     "prefix_records": len(whole.header["prefix_record_ids"]),
                     "cap": whole.header["token_cap"], "sha256": whole.sha256})

    # Determinism check, on real data rather than fixtures.
    again = A.assemble_retrieved(task_uid="SAMPLE-D3-1", stratum="D3",
                                 records=native[:args.per_packet], tau=tau,
                                 excluded_transport_failures=2861,
                                 sampling_note="theseus: stratified across 265 batches "
                                               "(byte-offset + gz-head, stamped per record); "
                                               "forge/signature_index: full scan")
    deterministic = again.sha256 == manifest[0]["sha256"]

    # Apollo Tier-A oracle packet, quarantine armed.
    walls_raw = [json.loads(l) for l in
                 (REPO / "apollo" / "wall_corpus" / "corpus.jsonl").read_text(
                     encoding="utf-8").splitlines() if l.strip()]
    oracle = A.assemble_oracle(
        task_uid="SAMPLE-ORACLE-1",
        walls=[{k: str(w.get(k, "")) for k in A.WALL_SHIPPABLE} for w in walls_raw[:6]],
        raw_records=walls_raw[:6],
    )
    (outdir / "ORACLE_sample_1.txt").write_text(oracle.text, encoding="utf-8")
    manifest.append({"file": "ORACLE_sample_1.txt", "arm": "F-oracle",
                     "tokens": oracle.header["token_count"], "sha256": oracle.sha256,
                     "walls": 6, "quarantine": "armed — assert_wall_quarantine passed"})

    summary = {
        "assembly_version": A.ASSEMBLY_VERSION,
        "token_count_method": A.TOKEN_COUNT_METHOD,
        "pool_records": {"theseus": len(theseus), "forge": len(forge), "signature_index": len(sig)},
        "tau_ledgers": len(tau),
        "deterministic_rerun_matches": deterministic,
        "packets": manifest,
    }
    (outdir / "MANIFEST.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0 if deterministic else 1


if __name__ == "__main__":
    raise SystemExit(main())
