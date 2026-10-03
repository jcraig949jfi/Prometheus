"""Deliver the replication's uint8 frames to M2 on an ORPHAN branch, built with git plumbing (no checkout, no change
to any working branch), exactly as HARM-55's frames travelled (harm55-frames-transfer). Refuses unless SELFCHECK.json
passed and every file hashes to frames128_manifest.json.

    python -m nyx.atlas.experiments.asal_replication.push_frames_branch [--push]
Branch: asal-repl-001-frames-transfer ; tree: transfer/asal_repl_001_frames128/<key>.npy + MANIFEST_frames128.json
NEVER merge this branch into main (it carries ~1,037 binary frame sets).
"""
import hashlib, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "out")
BRANCH = "asal-repl-001-frames-transfer"
PREFIX = "transfer/asal_repl_001_frames128"


def git(*a, inp=None, env=None):
    return subprocess.run(["git", *a], cwd=REPO, input=inp, capture_output=True, check=True, env=env).stdout


def main(push):
    sc = json.load(open(os.path.join(OUT, "SELFCHECK.json")))
    assert sc["pass"], "SELFCHECK not passed: nothing is delivered"
    man_path = os.path.join(OUT, "frames128_manifest.json")
    man = json.load(open(man_path))
    dest = man["dest"]
    entries = []
    for key, m in sorted(man["rollouts"].items()):
        p = os.path.join(dest, key + ".npy")
        b = open(p, "rb").read()
        assert hashlib.sha256(b).hexdigest() == m["sha256"], key
        blob = git("hash-object", "-w", "--stdin", inp=b).decode().strip()
        entries.append(f"100644 blob {blob}\t{key}.npy")
    mblob = git("hash-object", "-w", "--stdin", inp=open(man_path, "rb").read().replace(b"\r\n", b"\n")).decode().strip()
    entries.append(f"100644 blob {mblob}\tMANIFEST_frames128.json")
    for extra, name in ((os.path.join(OUT, "search", "embeddings32_torch.npz"), "embeddings32_torch.npz"),   # for native-vs-torch d_clip
                        (os.path.join(OUT, "selfcheck_torch.json"), "selfcheck_torch.json")):             # the C-SELF rescore file
        eb = git("hash-object", "-w", "--stdin", inp=open(extra, "rb").read()).decode().strip()
        entries.append(f"100644 blob {eb}\t{name}")
        print(name, "sha256", hashlib.sha256(open(extra, "rb").read()).hexdigest())
    inner = git("mktree", inp=("\n".join(entries) + "\n").encode()).decode().strip()
    t1 = git("mktree", inp=f"040000 tree {inner}\tasal_repl_001_frames128\n".encode()).decode().strip()
    root = git("mktree", inp=f"040000 tree {t1}\ttransfer\n".encode()).decode().strip()
    msg = (f"Nyx: ASAL replication 001 frames for the native column (M2) -- {len(entries) - 1} uint8 (8,128,128) sets + manifest; "
           f"packet freeze {man['packet_freeze'][:8]}; SELFCHECK max |diff| {sc['C-SELF']['max_abs_diff']:.3g}. ORPHAN: never merge into main.\n")
    commit = git("commit-tree", root, "-m", msg).decode().strip()
    git("update-ref", f"refs/heads/{BRANCH}", commit)
    print("branch", BRANCH, "commit", commit, "files", len(entries))
    if push:
        print(subprocess.run(["git", "push", "origin", f"{BRANCH}:{BRANCH}"], cwd=REPO, capture_output=True, text=True).stderr[-400:])
    return commit


if __name__ == "__main__":
    main("--push" in sys.argv)
