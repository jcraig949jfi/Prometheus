
import hashlib, json, random, sys, time
sys.path.insert(0, r"F:\Prometheus\evidence_wiki")
from ew.client import EvidenceWiki
machine, start, count, die_at = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
run_tag = sys.argv[5]
ew = EvidenceWiki(machine=machine, agent=f"v3-ingest-{machine}")
lat = []
# Deterministic across processes. The original seed was hash(machine), which
# Python randomizes per process (PYTHONHASHSEED): every rerun therefore sent
# DIFFERENT outcomes under the SAME encounter ids. The pre-006 service hid
# that behind ON CONFLICT DO NOTHING; it now returns 409, correctly.
rng = random.Random(int(hashlib.sha256(machine.encode()).hexdigest()[:8], 16))
for i in range(start, start + count):
    if die_at >= 0 and i - start == die_at:
        sys.exit(9)  # simulated crash mid-batch
    eid = f"SYN-{i:06d}"
    row = {
        "encounter_id": eid,
        "run_id": run_tag,          # fresh execution identity per battery run
        "sfe_entry_hash": "sha256:" + hashlib.sha256(f"syn|{i}".encode()).hexdigest(),
        "sfe_event_id": "evt_" + hashlib.sha256(f"syn|{i}".encode()).hexdigest()[:24],
        "world_id": f"synw_{i % 40:03d}",
        "outcome": rng.choice(["committed", "low_score", "timeout", "crash"]),
        "failure_class": rng.choice([None, "low_score", "timeout"]),
        "namespace": "synthetic",
        "idempotency_key": f"syn-{run_tag}-{eid}"}
    t0 = time.time()
    r = ew._post("fossil/encounters", row)
    lat.append(time.time() - t0)
    if rng.random() < 0.10:  # duplicate/retry injection: byte-identical replay
        ew._post("fossil/encounters", dict(row))
print(json.dumps({"machine": machine, "n": count,
                  "p50_ms": sorted(lat)[len(lat)//2]*1000,
                  "p95_ms": sorted(lat)[int(len(lat)*0.95)]*1000}))
