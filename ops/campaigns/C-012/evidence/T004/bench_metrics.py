"""C-012-T004 analysis code (frozen with the preregistration, ../../prereg/T004_PREREG.md s5-s6).

Pure functions over the raw per-attempt rows a benchmark point records; no database, no clock. Every timestamp
comes from M1 Postgres (one clock): task created_at, attempt started_at/ended_at, artifact created_at, Moonshot
attempts.classified_at. Times are seconds as floats.

Row (one per Fabric attempt): task_id, attempt_id, instance, host, status (succeeded | failed | abandoned |
canceled), created (task), started, ended, first_artifact, last_artifact, artifact_bytes, params_bytes,
classified (Moonshot, or None), outcome (Moonshot, or None).
"""

BOUNDS = {"B1": 0.05, "B2": 0.05, "B3": 0.10, "B4": 0.01}


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def p95(xs):
    """Nearest-rank 95th percentile."""
    xs = sorted(xs)
    if not xs:
        return None
    import math
    return xs[max(0, math.ceil(0.95 * len(xs)) - 1)]


def stages(r):
    """Per-attempt stage durations (s) of an attempt that reached its artifacts."""
    if r["first_artifact"] is None or r["ended"] is None:
        return None
    return {"execute": r["first_artifact"] - r["started"],
            "transfer": r["last_artifact"] - r["first_artifact"],
            "finish": r["ended"] - r["last_artifact"],
            "queue": r["started"] - r["created"],
            "publish": (r["classified"] - r["ended"]) if r["classified"] is not None else None}


def gaps(rows):
    """Worker-side claim gaps: for each worker instance, the time from the end of one attempt to the start of its
    next (Fabric's worker re-claims at once after an attempt; with work queued, this is pure coordination: reap,
    touch, claim transactions; with nothing queued it includes idle polling)."""
    by = {}
    for r in rows:
        if r["started"] is not None:
            by.setdefault(r["instance"], []).append(r)
    out = []
    for rs in by.values():
        rs.sort(key=lambda r: r["started"])
        for a, b in zip(rs, rs[1:]):
            if a["ended"] is not None:
                out.append(b["started"] - a["ended"])
    return out


def point_metrics(rows, *, wall_s, published, db_bytes, rate_limit_or_db_errors=0):
    """The preregistered metrics M1-M7 and throughput for one point."""
    executed = [r for r in rows if r["started"] is not None]
    st = [s for s in (stages(r) for r in executed) if s is not None]
    g = gaps(rows)
    execute = [s["execute"] for s in st]
    coord = sum(g) + sum(s["transfer"] + s["finish"] for s in st)
    m1 = coord / (coord + sum(execute)) if (coord + sum(execute)) > 0 else None
    tasks = {r["task_id"] for r in rows}
    fabric_retries = len(executed) - len(tasks)
    moonshot_non_pub = sum(1 for r in rows if r["outcome"] not in (None, "PUBLISHED"))
    contention = sum(1 for r in rows if r["outcome"] in ("DUPLICATE", "STALE", "HALTED"))
    m2 = (max(0, fabric_retries) + contention) / published if published else None
    m3 = (p95(g) / median(execute)) if (g and execute and median(execute)) else None
    abandoned = sum(1 for r in executed if r["status"] in ("abandoned", "failed")) + \
        sum(1 for r in rows if r["outcome"] == "STALE")
    m4 = abandoned / len(executed) if executed else None
    moved = sum(r["artifact_bytes"] + r["params_bytes"] for r in executed)
    m5 = moved / published if published else None
    m6 = db_bytes / published if published else None
    m7 = (m6 * (published / wall_s) * 30 * 86400) if (m6 is not None and wall_s) else None
    pub = [s["publish"] for s in st if s["publish"] is not None]
    return {
        "published": published, "attempts_executed": len(executed), "tasks": len(tasks), "wall_s": wall_s,
        "throughput_per_s": published / wall_s if wall_s else None,
        "M1_coordination_wall_fraction": m1, "M2_retries_per_published": m2, "M3_p95_gap_over_median_execute": m3,
        "M4_abandonment_rate": m4, "M5_bytes_moved_per_published": m5, "M6_db_bytes_per_published": m6,
        "M7_tripwire_bytes_per_30d": m7, "db_errors": rate_limit_or_db_errors,
        "moonshot_non_published": moonshot_non_pub,
        "execute_s": {"median": median(execute), "p95": p95(execute)},
        "gap_s": {"median": median(g), "p95": p95(g), "n": len(g)},
        "transfer_s": {"median": median([s["transfer"] for s in st]), "p95": p95([s["transfer"] for s in st])},
        "finish_s": {"median": median([s["finish"] for s in st]), "p95": p95([s["finish"] for s in st])},
        "publish_latency_s": {"median": median(pub), "p95": p95(pub)},
        "queue_s": {"median": median([s["queue"] for s in st]), "p95": p95([s["queue"] for s in st])},
    }


def verdict(m):
    """ADEQUATE iff B1-B5 hold (prereg s6); else RECONSIDER naming the failed bounds."""
    failed = []
    for b, key in (("B1", "M1_coordination_wall_fraction"), ("B2", "M2_retries_per_published"),
                   ("B3", "M3_p95_gap_over_median_execute"), ("B4", "M4_abandonment_rate")):
        v = m.get(key)
        if v is None or v > BOUNDS[b]:
            failed.append(b)
    if m.get("db_errors", 0) != 0:
        failed.append("B5")
    return ("ADEQUATE", []) if not failed else ("RECONSIDER", failed)


def envelope(by_d):
    """T*: the smallest swept D that is ADEQUATE with every larger swept D ADEQUATE too; None if the largest fails."""
    t = None
    for d in sorted(by_d, reverse=True):
        if by_d[d] != "ADEQUATE":
            break
        t = d
    return t
