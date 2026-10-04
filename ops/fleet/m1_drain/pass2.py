"""M1 drain pass 2 (M1-DRAIN-2026-10-03): case-by-case dispositions for the worktrees pass 1 skipped.

Each case is fixed in code below, with the reason it is safe, and every action is appended to DISPOSITIONS.jsonl.
Preservation always happens before removal; a removal step runs only after its preservation step is verified on origin.
"""
import gzip, hashlib, json, os, shutil, subprocess, sys, datetime as dt

REPO = "F:/prometheus"
LOG = "F:/Prometheus-worktrees/aporia-cwo/ops/fleet/M1_DRAIN_2026-10-03/DISPOSITIONS.jsonl"
WT = "F:/Prometheus-worktrees/"
TAGP = "archive/m1-drain-2026-10-03/"


def git(cwd, *a, timeout=1800):
    r = subprocess.run(["git", "-C", cwd, *a], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).rstrip()  # rstrip only: porcelain lines begin with a status column that may be a space


def log(**rec):
    rec["utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec) + "\n")
    print(rec.get("action"), rec.get("path", rec.get("tag", "")), rec.get("result"), flush=True)


def head(p):
    return git(p, "rev-parse", "HEAD")[1]


def remove(path, force=False, **extra):
    h = head(path)
    rc, out = git(REPO, "worktree", "remove", *(["--force"] if force else []), path)
    log(action="worktree_remove" + ("_force" if force else ""), path=path, head=h,
        result="REMOVED" if rc == 0 else "REMOVE_FAILED", detail=out[:200] if rc else "", **extra)
    return rc == 0


def remote_tag_sha(tag):
    rc, out = git(REPO, "ls-remote", "origin", "refs/tags/" + tag)
    return out.split()[0] if rc == 0 and out else None


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


git(REPO, "fetch", "-q", "origin")

# 1. RESOLVED (HEAD in origin/main, clean); owners drained (Nestor #1310, Sisyphus #1308, Tantalus #1311) or Aporia's own
for name in ["nestor-d2v13", "sisyphus-base-role", "tantalus-base-role", "tantalus-phase3-intake", "aporia-2026-09-15",
             "aporia-2026-09-23", "aporia-2026-09-25", "aporia-2026-09-29", "aporia-baserole"]:
    p = WT + name
    rc1, _ = git(p, "merge-base", "--is-ancestor", "HEAD", "origin/main")
    rc2, st = git(p, "status", "--porcelain", "--untracked-files=normal")
    if rc1 == 0 and rc2 == 0 and not st:
        remove(p, disposition="MERGE (already in main)")
    else:
        log(action="worktree_remove", path=p, result="SKIP_NOT_CLEAN_OR_NOT_IN_MAIN", detail=st[:200])

# 2. Nestor's ARCHIVE worktrees: remove only if the pushed archive tag exists at HEAD (#1310)
for name, tag in [("nestor-g2rerun", "Nestor/g2rerun-detached"), ("nestor-g2sample", "Nestor/g2sample-detached")]:
    p = WT + name
    t = remote_tag_sha(TAGP + tag)
    if t and t == head(p):
        rc, st = git(p, "status", "--porcelain")
        remove(p, disposition="ARCHIVE", tag=TAGP + tag) if not st else log(action="worktree_remove", path=p,
                                                                          result="SKIP_DIRTY", detail=st[:200])
    else:
        log(action="worktree_remove", path=p, result="SKIP_TAG_MISSING_OR_MISMATCH", tag=TAGP + tag, tag_sha=t)

# 3. DISCARD (owner-declared or generated-only), recording identity of what is discarded
def discard(path, allowed_untracked_prefixes=None, allow_tracked_files=None, reason=""):
    rc, st = git(path, "status", "--porcelain", "--untracked-files=all")
    lines = [l for l in st.splitlines() if l]
    rc_d, diff = git(path, "diff")
    ok = True
    for l in lines:
        code, f = l[:2], l[3:]
        if code == "??":
            if allowed_untracked_prefixes is not None and not any(f.startswith(a) or ("__pycache__" in f and "__pycache__" in a)
                                                                  for a in allowed_untracked_prefixes):
                ok = False
        elif allow_tracked_files is not None and f not in allow_tracked_files:
            ok = False
    ident = {"status_lines": len(lines), "status_sha256": hashlib.sha256(st.encode()).hexdigest(),
             "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(), "sample": [l for l in lines[:5]]}
    if not ok:
        log(action="discard", path=path, result="SKIP_UNEXPECTED_CONTENT", **ident)
        return
    remove(path, force=True, disposition="DISCARD", reason=reason, **ident)


discard(WT + "nestor-s1-forensics", allowed_untracked_prefixes=["roles/Nestor/campaigns/npe-arc3-2026-09-28/x_a3_"],
        allow_tracked_files=["roles/Nestor/LEASES.jsonl"],
        reason="Nestor #1310: LEASES lines appended to main 797d338ff; scratch results copied to main c4f37fd9a")
discard(WT + "nestor-s4v2", allowed_untracked_prefixes=[], allow_tracked_files=["roles/Nestor/LEASES.jsonl"],
        reason="Nestor #1310: LEASES lines appended to main 797d338ff")
discard(WT + "alethelia-base-role", allowed_untracked_prefixes=["__pycache__"], allow_tracked_files=[],
        reason="generated __pycache__ only; HEAD in main")
discard(WT + "kairos-base-role", allowed_untracked_prefixes=["__pycache__"], allow_tracked_files=[],
        reason="generated __pycache__ only; HEAD in main")

# F:/Prometheus-archaeon: only 0-byte .err files untracked
pa = "F:/Prometheus-archaeon"
errs = [l[3:] for l in git(pa, "status", "--porcelain")[1].splitlines() if l]
if errs and all(e.endswith(".err") and os.path.getsize(os.path.join(pa, e)) == 0 for e in errs):
    remove(pa, force=True, disposition="DISCARD", reason="only 0-byte .err files untracked; HEAD in main", files=errs)
else:
    log(action="discard", path=pa, result="SKIP_UNEXPECTED_CONTENT", files=errs)

# prom_main_wt2: interrupted checkout; every change is a deletion; HEAD f3b26ae9a in main (contract s7: destroy)
pt = "C:/Users/jcrai/AppData/Local/Temp/prom_main_wt2"
st = git(pt, "status", "--porcelain")[1].splitlines()
codes = {l[:2] for l in st if l}
if codes == {" D"} and git(pt, "merge-base", "--is-ancestor", "HEAD", "origin/main")[0] == 0:
    remove(pt, force=True, disposition="DISCARD", reason="interrupted checkout: %d tracked files missing, no other change"
           % len(st))
else:
    log(action="discard", path=pt, result="SKIP_UNEXPECTED_CONTENT", codes=sorted(codes))

# 4. Archaeon raw S5 results: gzip onto the seat's own branch, push branch + archive tag, then remove
pp = WT + "archaeon-pass-1804"
files = ["archaeon/docs/h0h5/S5_RESULTS_RUN2_L8_2026-09-13.json", "archaeon/docs/h0h5/S5_RESULTS_RUN2_L9_2026-09-13.json"]
recs = []
for f in files:
    src = os.path.join(pp, f)
    raw = sha256(src)
    with open(src, "rb") as i, gzip.open(src + ".gz", "wb", compresslevel=9) as o:
        shutil.copyfileobj(i, o)
    recs.append({"file": f, "raw_sha256": raw, "raw_bytes": os.path.getsize(src), "gz_bytes": os.path.getsize(src + ".gz")})
note = os.path.join(pp, "archaeon/docs/h0h5/S5_RESULTS_RUN2_RAW_ARCHIVE_README.md")
with open(note, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("# S5 RUN2 raw results (archived by M1-DRAIN-2026-10-03)\n\nThe full S5 RUN2 L8/L9 result files were untracked "
             "on M1 only; the SLIM versions are tracked. They are preserved here gzipped. Raw (uncompressed) identity:\n\n"
             + "\n".join("- %s: sha256 %s, %d bytes" % (r["file"], r["raw_sha256"], r["raw_bytes"]) for r in recs)
             + "\n\nOwner for reconsideration: Archaeon (H0H5 S5). Not merged to main: raw data, ~60 MB.\n")
rc, out = git(pp, "add", *[f + ".gz" for f in files], "archaeon/docs/h0h5/S5_RESULTS_RUN2_RAW_ARCHIVE_README.md")
msgf = os.path.join(pp, ".m1drain_msg.txt")
open(msgf, "w").write("ARCHIVE: S5 RUN2 raw L8/L9 results gzipped (were untracked on M1 only); M1-DRAIN-2026-10-03\n\n"
                      "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>\n")
rc, out = git(pp, "commit", "-q", "-F", msgf)
os.remove(msgf)
tag = TAGP + "Archaeon/pass-2026-09-11-1804"
h = head(pp)
rc1, o1 = git(pp, "push", "-q", "origin", "HEAD:refs/heads/archaeon/pass-2026-09-11-1804", timeout=900)
rc2, o2 = git(pp, "tag", tag, h)
rc3, o3 = git(pp, "push", "-q", "origin", "refs/tags/" + tag, timeout=900)
ok = remote_tag_sha(tag) == h
log(action="archive", path=pp, tag=tag, head=h, files=recs, result="ARCHIVED" if ok else "ARCHIVE_FAILED",
    detail=(o1 + o3)[-200:] if not ok else "")
if ok:
    for f in files:   # originals are now in the tag (gzipped, raw sha recorded); remove the untracked originals
        os.remove(os.path.join(pp, f))
    rc, st = git(pp, "status", "--porcelain")
    if not st:
        remove(pp, disposition="ARCHIVE", tag=tag)
    else:
        log(action="worktree_remove", path=pp, result="SKIP_DIRTY_AFTER_ARCHIVE", detail=st[:200])

# 5. _r8-main-merge-check: two unpushed merge commits -> archive tag; pm_ledger_test/A.jsonl (4 KB test) recorded, discarded
pr = WT + "_r8-main-merge-check"
tag = TAGP + "Nestor/r8-main-merge-check"
h = head(pr)
git(pr, "tag", tag, h)
git(pr, "push", "-q", "origin", "refs/tags/" + tag, timeout=900)
if remote_tag_sha(tag) == h:
    a = os.path.join(pr, "pm_ledger_test", "A.jsonl")
    ident = {"file": "pm_ledger_test/A.jsonl", "sha256": sha256(a), "bytes": os.path.getsize(a)} if os.path.exists(a) else {}
    log(action="archive", path=pr, tag=tag, head=h, result="ARCHIVED",
        reason="R8 main-merge check (candidate 91d6a6d66, memory nestor_r8_main_merge); owner Nestor; NEEDS_REVIEW at P2B",
        discarded_untracked=ident)
    remove(pr, force=True, disposition="ARCHIVE / NEEDS_REVIEW", tag=tag)
else:
    log(action="archive", path=pr, tag=tag, result="ARCHIVE_FAILED")

git(REPO, "worktree", "prune")
# local branches of removed worktrees: delete only if tip is in origin/main or under a verified archive tag
rc, wl = git(REPO, "worktree", "list", "--porcelain")
checked = {l.split(" ", 1)[1].replace("refs/heads/", "") for l in wl.splitlines() if l.startswith("branch ")}
for b in ["nestor/d2v13-2026-09-29", "sisyphus/phase3-intake-2026-10-01", "sisyphus/base-role-adopt-2026-10-01",
          "tantalus/base-role-adopt-2026-10-01", "tantalus/phase3-intake-2026-10-01", "aporia/pass-2026-09-15-boot",
          "aporia/pass-2026-09-23-boot", "aporia/pass-2026-09-25-cyclops", "aporia/mwo-0002-candidate-2026-09-29",
          "aporia/base-role-work-conserving-2026-09-29", "nestor/s1-forensics-2026-09-23", "nestor/s4v21-2026-09-29",
          "alethelia/base-role-adopt-2026-09-11", "kairos/base-role-adopt-2026-09-11", "archaeon/v0",
          "archaeon/pass-2026-09-11-1804"]:
    if b in checked:
        continue
    rc, sha = git(REPO, "rev-parse", "-q", "--verify", "refs/heads/" + b)
    if rc != 0:
        continue
    in_main = git(REPO, "merge-base", "--is-ancestor", sha, "origin/main")[0] == 0
    archived = b == "archaeon/pass-2026-09-11-1804" and remote_tag_sha(TAGP + "Archaeon/pass-2026-09-11-1804") == sha
    if in_main or archived:
        rc, out = git(REPO, "branch", "-D", b)
        log(action="branch_delete_local", branch=b, head=sha, result="DELETED" if rc == 0 else "DELETE_FAILED",
            basis="in_main" if in_main else "archive_tag")
print("pass2 done")
