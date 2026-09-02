
import json, random, sys, time
sys.path.insert(0, r"F:\Prometheus\evidence_wiki")
from ew.client import EvidenceWiki
machine, start, count, die_at = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
ew = EvidenceWiki(machine=machine, agent=f"v3-ingest-{machine}")
lat = []
rng = random.Random(hash(machine) & 0xffff)
for i in range(start, start + count):
    if die_at >= 0 and i - start == die_at:
        sys.exit(9)  # simulated crash mid-batch
    eid = f"SYN-{i:06d}"
    t0 = time.time()
    r = ew._post("fossil/encounters", {
        "encounter_id": eid,
        "sfe_entry_hash": f"sha256:synthetic{i:056d}",
        "world_id": f"synw_{i % 40:03d}",
        "outcome": rng.choice(["committed", "low_score", "timeout", "crash"]),
        "failure_class": rng.choice([None, "low_score", "timeout"]),
        "namespace": "synthetic",
        "idempotency_key": f"syn-{eid}"})
    lat.append(time.time() - t0)
    if rng.random() < 0.10:  # duplicate/retry injection
        ew._post("fossil/encounters", {
            "encounter_id": eid, "sfe_entry_hash": f"sha256:synthetic{i:056d}",
            "namespace": "synthetic", "idempotency_key": f"syn-{eid}"})
print(json.dumps({"machine": machine, "n": count,
                  "p50_ms": sorted(lat)[len(lat)//2]*1000,
                  "p95_ms": sorted(lat)[int(len(lat)*0.95)]*1000}))
