"""The two immutable replenishment blocks, and the preregistered rule for merging them.

WHY A REGISTRY RATHER THAN A SECOND COPY OF THE DRIVER. Block B needs the same prepass, the
same band read, the same cross-family screen, and the same estimator as block A. Forking
`campaign.p1` to get a block-B leg would create a second implementation of the statistic that
decides the campaign -- which is ATK-014's defect class exactly (a confirmatory estimator that
agrees with itself because it is itself). So the block-B leg re-points the driver's ledger
paths and calls the SAME `p1`. One estimator, two populations.

THE HAZARD THAT CREATES, named because it is severe. Re-pointing module globals means a bug
here writes block B's rows into block A's pinned ledgers -- silent contamination of a
population whose whole purpose is to be immutable. `test_blocks_gate_fire.py` therefore does
not assert the scoping works: it snapshots block A's directory, runs a block-B collection
against a mocked lane, and proves not one byte of block A changed.

MERGE RULE: `ergon/probe/PREREG_block_B_merge_rule_2026-08-25.md`, committed before block B
existed. `merge_reading` below is that document in code; where they differ, the document wins
and the difference is a defect in this file.
"""
import contextlib
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

#: Block A is the ORIGINAL PIN. It is immutable. Nothing in this module may write to it.
#: Block B is its sibling: same rung, same generator, same host, disjoint uid namespace,
#: its own sha, its own ledgers.
BLOCKS = {
    "A": {
        "block": "A",
        "manifest": "ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl",
        "sha16": "e6b1e001bf79e3ef",
        "uid_prefix": "nearmiss_mix-M30-",
        "dir_suffix": "",              # block A IS the driver's own directory
        "second_family_ledger":
            "ergon/probe/ledgers/coldband_drip/nvidia_nemotron-super-49b-v1.jsonl",
        "n": 200,
    },
    "B": {
        "block": "B",
        "manifest": "ergon/probe/manifests/nearmiss_mixB-M30_manifest_n220.jsonl",
        "sha16": "7444a1789e98642d",
        "uid_prefix": "nearmiss_mixB-M30-",
        "dir_suffix": "_blockB",
        "second_family_ledger":
            "ergon/probe/ledgers/coldband_drip/blockB_nvidia_nemotron-super-49b-v1.jsonl",
        "n": 220,
    },
}


def spec(block):
    if block not in BLOCKS:
        raise ValueError(f"unknown block {block!r}; known: {sorted(BLOCKS)}")
    return BLOCKS[block]


def load(block):
    """Rows for a block, REFUSING on a sha mismatch.

    The refusal is the point and it is copied deliberately from `campaign.manifest`: a block
    is defined by specific rows, and a cross-family screen computed against different rows
    under the same name is not a weaker result, it is a different experiment wearing the
    block's name.
    """
    s = spec(block)
    path = ROOT / s["manifest"]
    if not path.exists():
        raise SystemExit(f"block {block}: manifest absent at {s['manifest']}")
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    got = sha16(rows)
    if got != s["sha16"]:
        raise SystemExit(f"REFUSED: block {block} manifest sha {got} != {s['sha16']}; "
                         "the cross-family screen is defined on specific rows")
    if len(rows) != s["n"]:
        raise SystemExit(f"REFUSED: block {block} has {len(rows)} rows, expected {s['n']}")
    bad = [r["uid"] for r in rows if not r["uid"].startswith(s["uid_prefix"])]
    if bad:
        raise SystemExit(f"REFUSED: block {block} carries {len(bad)} uids outside its "
                         f"namespace {s['uid_prefix']!r}, e.g. {bad[:3]}")
    return rows


def sha16(rows):
    """Byte-identical to `campaign.manifest_sha256`, truncated. Imported rather than
    re-derived where possible; defined here only so `load` works before campaign imports."""
    from ergon.probe.campaign import manifest_sha256
    return manifest_sha256(rows)[:16]


def block_dir(block):
    """`block`'s ledger directory, derived FROM the live `campaign.DIR` by suffix.

    Not a repo-absolute path, and the difference is not cosmetic -- it was a live defect. The
    first version returned `ROOT / "ergon/probe/ledgers/campaign_blockB"` unconditionally. The
    dry-run test drives the whole campaign against a mocked lane with `campaign.DIR` pointed
    into a sandbox, and the block-B leg then ignored the sandbox and wrote 142 synthetic
    `executor: dryrun / host: TESTHOST` rows into the REAL block B prepass ledger. Nothing was
    spent and nothing was lost (the directory was untracked), but a later scheduled firing
    would have computed block B's band read over invented rows.

    Deriving by SUFFIX rather than by name is the second correction. Using a fixed name under
    `DIR.parent` sandboxed the live tree correctly but sent every dry-run to one shared
    `<temp>/campaign_blockB`, so consecutive test runs would inherit each other's rows and a
    later dry-run could see a block B that a previous one had "collected". The suffix binds
    the block directory to the exact directory the driver is using, so an isolated run is
    isolated in all of its blocks and a shared run shares all of them.

    Live:     .../ledgers/campaign      -> .../ledgers/campaign_blockB
    Dry-run:  <tmp>/campaign_dry_ab12   -> <tmp>/campaign_dry_ab12_blockB
    """
    import ergon.probe.campaign as C
    d = pathlib.Path(C.DIR)
    return d.parent / (d.name + spec(block)["dir_suffix"])


def block_second_family_ledger(block):
    """The block's second-family drip ledger, sandboxed alongside its campaign directory.

    Same hazard, other path: a sandboxed run that read the live drip ledger would compute its
    cross-family screen against production second-family rows, and one that appended to it
    would contaminate them.
    """
    import ergon.probe.campaign as C
    name = pathlib.Path(spec(block)["second_family_ledger"]).name
    return pathlib.Path(C.DIR).parent / "coldband_drip" / name


@contextlib.contextmanager
def repointed(block):
    """Run driver code against `block`'s ledgers instead of the currently active block's.

    Restores in a `finally` -- a collection that raises must not leave the module pointed at
    block B, because the very next caller would be `campaign._campaign()` writing block A's
    rows into block B's directory. The restore is asserted in the gate-fire suite by raising
    inside the context on purpose.
    """
    import ergon.probe.campaign as C
    prev_dir, prev_sf = C.DIR, C.SECOND_FAMILY_LEDGER
    target, sf = block_dir(block), block_second_family_ledger(block)
    C.DIR = target
    C.SECOND_FAMILY_LEDGER = str(sf)
    C.DIR.mkdir(parents=True, exist_ok=True)
    try:
        yield C.DIR
    finally:
        C.DIR, C.SECOND_FAMILY_LEDGER = prev_dir, prev_sf


def collect(block, budget):
    """Run the SAME `p1` -- prepass, truncation gate, band read, cross-family screen -- on
    `block`. Returns (read_or_None, spent)."""
    import ergon.probe.campaign as C
    rows = load(block)
    gold = {r["uid"]: r["gold_int"] for r in rows}
    with repointed(block):
        return C.p1(rows, gold, budget)


# ------------------------------------------------------------------ the merge rule, in code

def _xf(read):
    """The cross-family (Tier B) leg of a band read, or None. The single-family number is
    NEVER substituted here: HB-R1 disqualifies it, and the merge rule is written against the
    cross-family estimate. A block with no admissible second family contributes nothing."""
    return (read or {}).get("tier_b_cross_family_screen")


def merge_reading(read_a, read_b):
    """`PREREG_block_B_merge_rule_2026-08-25.md` §3, executed.

    Returns a dict that ALWAYS reports block-wise, and reports pooled only when all three
    preregistered conditions hold. Clause 3 is the one with teeth: non-overlapping intervals
    FORBID pooling and the disagreement is the finding, because two same-rung, same-host,
    same-generator blocks that disagree mean the rung is not a stable property of the family.
    """
    a, b = _xf(read_a), _xf(read_b)
    out = {
        "rule": "ergon/probe/PREREG_block_B_merge_rule_2026-08-25.md",
        "block_A": a, "block_B": b,
        "basis": "cross-family (Tier B, HB-R1)",
    }
    if a is None or b is None:
        out.update(pooling="UNAVAILABLE", n_pooled=None,
                   reason=("a block without an admissible second-family leg has no "
                           "cross-family screen, so it contributes nothing to a Tier B "
                           "reading (merge rule §2, second bullet). Missing: "
                           + ", ".join(n for n, v in (("A", a), ("B", b)) if v is None)))
        return out

    lo_a, hi_a = a["manifest_interval_95"]
    lo_b, hi_b = b["manifest_interval_95"]
    overlap = not (hi_a < lo_b or hi_b < lo_a)
    out["intervals_overlap"] = overlap
    if not overlap:
        out.update(pooling="FORBIDDEN", n_pooled=None,
                   reason=("merge rule §3: the blocks' cross-family intervals do not overlap "
                           f"(A {a['manifest_interval_95']} vs B {b['manifest_interval_95']}). "
                           "Pooling is forbidden and the DISAGREEMENT IS THE FINDING: two "
                           "same-rung, same-host, same-generator blocks that disagree mean the "
                           "rung is not a stable property of the family and the leveling does "
                           "not transfer across draws. Report both, pool neither, escalate."))
        return out

    n_pooled = a["n"] + b["n"]
    # The pooled point is the n-weighted mean of the two block points, which is exactly the
    # accuracy over the union -- the blocks are disjoint by construction, so no row is double
    # counted. Written as a weighted mean rather than recomputed from rows so that it cannot
    # silently disagree with the block-wise numbers reported beside it.
    point = (a["point_estimate"] * a["n"] + b["point_estimate"] * b["n"]) / n_pooled
    out.update(pooling="PERMITTED", n_pooled=n_pooled, pooled_point_estimate=round(point, 4),
               reason="merge rule §2 satisfied: both blocks have an admissible cross-family "
                      "leg and their intervals overlap.",
               reporting_note="merge rule §1: this pooled figure is never reported alone; "
                              "block_A and block_B travel with it, and every statistic is "
                              "reproducible restricted to either block.")
    return out
