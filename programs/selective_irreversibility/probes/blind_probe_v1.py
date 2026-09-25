"""Registry probe v1 (terms frozen BLIND_LANES.md 2026-09-25T18:30Z, Aporia). Read-only.
Usage: python blind_probe_v1.py <repo> <sha>"""
import subprocess, sys, os

STRONG = ["selective irreversib", "selective-irreversib", "selective_irreversib",
          "2026-09-23-selective-irreversibility", "accessible causal state", "relevance-selective"]
WEAK = ["irreversib", "landauer"]
SEATS = {
    "Aether": ["roles/Aether", "Aether"],
    "Cosmos": ["roles/Cosmos", "prometheus/cosmos"],
    "Archaeon": ["roles/Archaeon", "archaeon"],
    "Bellerophon": ["roles/Bellerophon", "prometheus/z80atlas", "prometheus/toolbox", "prometheus/atlas_bee"],
    "Ensorain": ["roles/Ensorain", "ensorain"],
    "Daedalus": ["roles/Daedalus", "SerendipityFoundry"],
    "Vivarium": ["roles/Vivarium", "vivarium"],
    "Aphrodite": ["roles/Aphrodite"],
}
FROZEN_WORKDIRS = {"Bellerophon": [r"C:/Users/James/z80atlas_coupling_2026-09-24/code"]}

repo, sha = sys.argv[1], sys.argv[2]

def git(*a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

def grep_tree(term, paths):
    out = git("grep", "-i", "-F", "-c", term, sha, "--", *paths)
    hits = {}
    for line in out.splitlines():
        f, _, n = line.rpartition(":")
        hits[f.split(":", 1)[1] if f.startswith(sha) else f] = int(n)
    return hits

def first_commit(term, paths):
    out = git("log", sha, "--reverse", "--format=%h %cI", "-S", term, "--regexp-ignore-case", "--", *paths)
    line = out.splitlines()[0] if out.strip() else ""
    return line

def grep_dir(term, d):
    n = 0; files = []
    for root, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(root, f)
            try:
                t = open(p, encoding="utf-8", errors="ignore").read().lower()
            except Exception:
                continue
            c = t.count(term)
            if c:
                n += c; files.append(p)
    return n, files

for seat, paths in SEATS.items():
    print("=" * 70); print(seat, "scope:", " ".join(paths))
    for cls, terms in (("STRONG", STRONG), ("WEAK", WEAK)):
        for term in terms:
            h = grep_tree(term, paths)
            if h:
                fc = first_commit(term, paths)
                print(f"  {cls} '{term}': {sum(h.values())} hits in {len(h)} files; first commit {fc}")
                for f, n in sorted(h.items())[:8]:
                    print(f"      {n:4d}  {f}")
    lg = git("log", sha, "--format=%h %cI %s", "-i", "-F", *sum((["--grep", t] for t in STRONG), []))
    mine = [l for l in lg.splitlines() if seat.lower() in l.lower()]
    print(f"  git log --grep STRONG, subjects naming {seat}: {len(mine)}")
    for l in mine[:5]:
        print("      " + l[:150])
    for d in FROZEN_WORKDIRS.get(seat, []):
        for cls, terms in (("STRONG", STRONG), ("WEAK", WEAK)):
            for term in terms:
                n, fs = grep_dir(term, d)
                if n:
                    print(f"  frozen workdir {d} {cls} '{term}': {n} in {fs[:3]}")
        print(f"  frozen workdir {d}: scanned")
