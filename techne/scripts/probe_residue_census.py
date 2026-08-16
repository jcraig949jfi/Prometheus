"""D2/D3 residue eligibility census + frozen pool extraction (Techne, packet-assembler contract).

Answers the question the prereg makes decisive at §4.3: does enough eligible native residue
exist for a stratum to run at all? Below 40 eligible records a stratum is reported
`NOT-RUN-FOR-LACK-OF-RESIDUE` — never as Δ = 0.

Sampling is itself analysis (`feedback_sampling_strategy_is_analysis`). The Theseus corpus is
370 GB across 266 batch files with a 12.7 GB maximum; a head-read of every file would be a
sampling-window artifact of exactly the kind that produced the false "bridge_extension absent"
claim in the 2026-06-23 M0.5 pass. So:

  * plain `.jsonl` batches are sampled by SEEDED UNIFORM BYTE OFFSET, which reaches the whole
    file at O(draws) cost. Known bias, stated: byte-offset sampling favours longer records.
  * `.gz` batches cannot be seeked, so they are read as a HEAD WINDOW with a stride. Known
    bias, stated: early-in-batch records only.

Both are stamped per batch into the pool and into every packet header that draws from it.

Usage:
    python -m techne.scripts.probe_residue_census --out pivot/probe_residue_census_<date>.json
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ergon.probe import assemble as A  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
CORPUS = REPO / "theseus" / "corpus"
FORGE = REPO / "agents" / "hephaestus" / "ledger.jsonl"
SIGINDEX = REPO / "theseus" / "orchestration" / "signature_index.sqlite"
SEED = A.PREREG_SEED


def sample_batch(path: pathlib.Path, draws: int, rng: random.Random) -> tuple[list[dict], str]:
    """Return (records, sampling_method) for one batch file."""
    if path.suffix == ".gz":
        out = []
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for i, line in enumerate(fh, start=1):
                    if i > draws * 4:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    d["__seq"] = i
                    out.append(d)
        except (OSError, EOFError, gzip.BadGzipFile):
            return [], "gz-unreadable"
        return out[:draws], f"gz-head-window(first {draws * 4} lines)"

    size = path.stat().st_size
    if size == 0:
        return [], "empty"
    out, seen = [], set()
    for _ in range(draws * 3):
        if len(out) >= draws:
            break
        off = rng.randrange(0, size)
        try:
            with path.open("rb") as fh:
                fh.seek(off)
                fh.readline()  # discard the partial line
                raw = fh.readline()
        except OSError:
            break
        if not raw or off in seen:
            continue
        seen.add(off)
        try:
            d = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        d["__seq"] = off  # byte offset IS a monotone position in an append-only file
        out.append(d)
    return out, f"seeded-byte-offset(seed={SEED}, draws={draws}) — length-biased"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws-per-batch", type=int, default=25)
    ap.add_argument("--max-batches", type=int, default=0, help="0 = all")
    ap.add_argument("--out", default="pivot/probe_residue_census.json")
    ap.add_argument("--pool-out", default="pivot/probe_d3_pool.jsonl")
    args = ap.parse_args()

    rng = random.Random(SEED)
    census: dict[str, object] = {
        "seed": SEED,
        "assembly_version": A.ASSEMBLY_VERSION,
        "sources": {},
        "sampling_doctrine": "feedback_sampling_strategy_is_analysis — stratified across ALL "
                             "batches; per-batch method stamped; biases stated, not hidden",
    }

    # ---- signature_index (full scan, 3,311 rows) -------------------------------------------
    sig_kill = A.load_signature_classes(SIGINDEX, verdict_classes=("KILL",))
    sig_all = A.load_signature_classes(
        SIGINDEX, verdict_classes=("KILL", "CONFIRM", "UNVERIFIED", "INCONCLUSIVE")
    )
    census["sources"]["signature_index"] = {
        "scan": "full",
        "rows_total": len(sig_all),
        "eligible_KILL": len(sig_kill),
        "with_obstruction_class": sum(1 for r in sig_kill if r.obstruction_class),
        "verdict_class_vocabulary": sorted({r.body.split("class: ")[1].split()[0] for r in sig_all}),
        "NOTE": "no REJECTED class exists in this table; prereg §4.3 names "
                "'Theseus invariant_equality REJECTED records' — those live in the corpus "
                "batches, not this index. Filed for the owner.",
    }

    # ---- forge ledger (full scan) -----------------------------------------------------------
    forge_math = A.load_forge_scraps(FORGE, include_transport_failures=False)
    forge_all = A.load_forge_scraps(FORGE, include_transport_failures=True)
    census["sources"]["hephaestus_forge"] = {
        "scan": "full",
        "scraps_total": len(forge_all),
        "eligible_excluding_transport": len(forge_math),
        "excluded_transport_failures": len(forge_all) - len(forge_math),
        "with_obstruction_class": sum(1 for r in forge_math if r.obstruction_class),
        "obstruction_breakdown": dict(
            collections.Counter(r.obstruction_class for r in forge_math)
        ),
    }

    # ---- theseus corpus (stratified sample across every batch) ------------------------------
    batches = sorted(CORPUS.glob("batch-*.jsonl*"))
    if args.max_batches:
        batches = batches[: args.max_batches]
    kind_counter: collections.Counter = collections.Counter()
    verdict_counter: collections.Counter = collections.Counter()
    null_counter: collections.Counter = collections.Counter()
    obstruction_counter: collections.Counter = collections.Counter()
    pool: list[dict] = []
    sampled = 0
    methods: collections.Counter = collections.Counter()

    for b in batches:
        recs, method = sample_batch(b, args.draws_per_batch, rng)
        methods[method.split("(")[0]] += 1
        sampled += len(recs)
        for d in recs:
            verdict_counter[str(d.get("verdict"))] += 1
            if str(d.get("verdict")) != "REJECTED":
                continue
            kind_counter[str(d.get("claim_kind"))] += 1
            for f in ("kill_pattern", "kill_vector", "step_trace", "precision_dps", "method"):
                if d.get(f) in (None, "", []):
                    null_counter[f] += 1
            obstruction = A._obstruction_for_theseus(d)
            obstruction_counter[str(obstruction)] += 1
            if obstruction:
                pool.append({
                    "ledger_id": str(d.get("batch_id") or b.name.split(".")[0]),
                    "seq": int(d["__seq"]),
                    "source": "theseus_corpus",
                    "record_id": str(d.get("record_id", ""))[:16],
                    "claim_kind": d.get("claim_kind"),
                    "canonical_claim_text": d.get("canonical_claim_text"),
                    "kill_pattern": d.get("kill_pattern"),
                    "method": d.get("method"),
                    "step_trace": d.get("step_trace"),
                    "obstruction_class": obstruction,
                    "sampling": method,
                })

    rejected = verdict_counter.get("REJECTED", 0)
    census["sources"]["theseus_corpus"] = {
        "scan": "stratified sample across ALL batches (not head-of-file)",
        "batches": len(batches),
        "records_sampled": sampled,
        "sampling_methods": dict(methods),
        "verdict_distribution": dict(verdict_counter),
        "rejected_sampled": rejected,
        "rejected_claim_kinds": dict(kind_counter.most_common(20)),
        "invariant_equality_rejected": kind_counter.get("invariant_equality", 0),
        "null_rates_over_rejected": {
            f: round(100.0 * n / max(rejected, 1), 1) for f, n in null_counter.items()
        },
        "obstruction_classifiable": dict(obstruction_counter),
    }

    d3_eligible = (
        len(pool)
        + census["sources"]["hephaestus_forge"]["with_obstruction_class"]
        + census["sources"]["signature_index"]["with_obstruction_class"]
    )
    census["d3_verdict"] = {
        "eligible_records": d3_eligible,
        "prereg_floor": 40,
        "status": "SUPPLIED" if d3_eligible >= 40 else "NOT-RUN-FOR-LACK-OF-RESIDUE",
    }
    census["d2_verdict"] = {
        "status": "BLOCKED-PENDING-OWNER-RULING",
        "why": "prereg §4.1 assigns D2 to NATIVE residue; §4.3 defines D2 by mechanism tags "
               "that describe the probe's arithmetic task domains. Native Theseus/forge "
               "records carry no such tags. Assembler supports either source pool; the "
               "ruling is Ergon's (R12). See the committed discrepancy note.",
        "native_records_carrying_mechanism_tags": 0,
    }
    census["d0_d1_verdict"] = {
        "status": "AWAITING-PRE-PASS",
        "why": "probe_prepass ledger does not exist yet; loader returns empty and the packet "
               "reports NOT-RUN-FOR-LACK-OF-RESIDUE rather than inventing residue.",
    }

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(census, indent=1, sort_keys=False), encoding="utf-8")
    pool_out = pathlib.Path(args.pool_out)
    with pool_out.open("w", encoding="utf-8") as fh:
        for r in pool:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps(census, indent=1)[:4000])
    print(f"\npool -> {pool_out} ({len(pool)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
