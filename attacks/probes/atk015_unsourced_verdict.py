"""ATK-015 probe — is any committed verdict artifact standing on rows that are not in git?

Exit 1 = defect present. $0, read-only, no network.

    PYTHONPATH=. python attacks/probes/atk015_unsourced_verdict.py

The rule this enforces: an aggregate that summarises rows it cannot produce is not evidence.
For each (verdict artifact -> source ledger) pair below, the ledger must (a) exist on disk and
(b) be TRACKED BY GIT. Untracked is the whole failure mode: untracked files are what ordinary
git hygiene deletes, and nothing in the pipeline raises when they go.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
L = ROOT / "ergon/probe/ledgers"

# (verdict artifact, ledger whose rows it summarises)
PAIRS = [
    (L / "campaign/p1_bandread.json", L / "campaign/p1_prepass.jsonl"),
    # NOTE the pairing: the committed M30 LEVELED verdict is underwritten by the RECOVERED
    # 400-row ledger, NOT by `coldband.jsonl`, which is a live re-collection of the same
    # manifest and currently partial. Pairing a verdict with a ledger that merely shares its
    # directory is how this probe would report green on the exact defect it exists to catch.
    (L / "coldband_m30_free/bandread.ORIGINAL-2026-08-23T0452Z.json",
     L / "coldband_m30_free/coldband.RECOVERED-400.jsonl"),
    (L / "coldband_drip/nvidia_nemotron-super-49b-v1_bandread.json",
     L / "coldband_drip/nvidia_nemotron-super-49b-v1.jsonl"),
]


def tracked(p):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", str(p)],
                       cwd=ROOT, capture_output=True)
    return r.returncode == 0


def main():
    bad = []
    for verdict, ledger in PAIRS:
        if not verdict.exists():
            continue
        rel_v = verdict.relative_to(ROOT).as_posix()
        rel_l = ledger.relative_to(ROOT).as_posix()
        if not ledger.exists():
            bad.append(f"{rel_v}: source ledger MISSING FROM DISK ({rel_l})")
        elif not tracked(ledger):
            n = sum(1 for _ in ledger.open(encoding="utf-8"))
            bad.append(f"{rel_v}: source ledger UNTRACKED ({rel_l}, {n} rows) "
                       f"-- one `git clean`/`stash drop` from gone")
        else:
            n = sum(1 for _ in ledger.open(encoding="utf-8"))
            print(f"OK  {rel_v}  <- {rel_l} ({n} rows, tracked)")
    if bad:
        print("\nDEFECT PRESENT -- UNSOURCED VERDICT(S):")
        for b in bad:
            print("  " + b)
        print("\nA verdict whose rows are not in git is an assertion, not a measurement, "
              "and cannot gate a phase.")
        return 1
    print("\nDefect ABSENT -- every verdict on this list has committed rows beneath it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
