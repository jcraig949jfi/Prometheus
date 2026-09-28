"""Odysseus's own reproduction of the D2 audit's blocking findings (synthetic only; no secrets touched)."""
import json, os, subprocess, sys, tempfile, py_compile, shutil
from pathlib import Path
T = Path(sys.argv[1])                                  # extracted tree at the audited commit
sys.path.insert(0, str(T))
os.environ["COSMOS_BROKER"] = "1"
from prometheus.cosmos.c3_holdout_D2 import runner, protocol
out = {}

# V1: AST audit misses attribute calls / aliased builtins
srcs = {"np_fromfile": "import numpy as np\nx = np.fromfile('/home/op/secrets/hidden_D2.plain.json')\n",
        "aliased_open": "f = [open][0]\nd = f('/home/op/secrets/hidden_D2.plain.json').read()\n",
        "bare_open_control": "d = open('/x').read()\n"}
out["V1_ast_flags"] = {k: runner.audit_source(s, k + ".py") for k, s in srcs.items()}

# V2: a sourceless .pyc next to the entry is importable (and load_package audits only .py)
d = Path(tempfile.mkdtemp())
(d / "helper.py").write_text("VALUE = 'ran compiled code'\n")
py_compile.compile(str(d / "helper.py"), cfile=str(d / "helper.pyc")); (d / "helper.py").unlink()
r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import helper; print(helper.VALUE)" % str(d)],
                   capture_output=True, text=True)
out["V2_sourceless_pyc_imports"] = r.stdout.strip()

def git(repo, *a, **kw):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=kw.get("check", True))

def repo():
    g = Path(tempfile.mkdtemp()); git(g, "init", "-q", "-b", "main")
    git(g, "config", "user.email", "t@t"); git(g, "config", "user.name", "t")
    (g / "base.txt").write_text("b"); git(g, "add", "-A"); git(g, "commit", "-qm", "base")
    return g

# V3: a record swapped through a merge; is it still "added once"?
g = repo(); rel = "rec/R.json"
git(g, "checkout", "-qb", "side")                      # fork BEFORE the record exists on main
(g / "rec").mkdir(); (g / rel).write_text('{"v":"forged"}'); git(g, "add", "-A"); git(g, "commit", "-qm", "side adds R (forged)")
git(g, "checkout", "-q", "main")
(g / "rec").mkdir(exist_ok=True); (g / rel).write_text('{"v":"original"}'); git(g, "add", "-A"); git(g, "commit", "-qm", "main adds R (original)")
git(g, "merge", "-q", "--no-ff", "-X", "theirs", "side", "-m", "merge side taking theirs", check=False)
content = git(g, "show", "main:" + rel).stdout.strip()
plain = protocol._commits_touching(g, "main", rel)
full = git(g, "log", "--full-history", "--format=%H", "main", "--", rel).stdout.split()
try:
    protocol._added_once(g, "main", rel, protocol.CommitmentMissing); verdict = "accepted as added-once"
except protocol.RecordRewritten as e:
    verdict = "RecordRewritten"
out["V3_merge_swap"] = {"record_now": content, "commits_seen_plain": len(plain), "commits_seen_full_history": len(full),
                        "gate": verdict}

# V4: a tag named origin/main shadows the remote-tracking branch
g = repo(); good = git(g, "rev-parse", "HEAD").stdout.strip()
git(g, "update-ref", "refs/remotes/origin/main", good)
git(g, "checkout", "-q", "--orphan", "evil"); (g / "base.txt").write_text("evil"); git(g, "add", "-A"); git(g, "commit", "-qm", "evil")
evil = git(g, "rev-parse", "HEAD").stdout.strip(); git(g, "tag", "origin/main", evil)
out["V4_tag_shadow"] = {"rev_parse_origin_main_is_tag": git(g, "rev-parse", "origin/main").stdout.strip() == evil,
                        "show_reads": git(g, "show", "origin/main:base.txt").stdout.strip()}

# V5: a committed protocol/__init__.py shadows protocol.py
p = Path(tempfile.mkdtemp()) / "pkg"; (p / "protocol").mkdir(parents=True)
(p / "__init__.py").write_text(""); (p / "protocol.py").write_text("WHO = 'real gate module'\n")
(p / "protocol" / "FIREWALL_AUDIT.json").write_text("{}")
r0 = subprocess.run([sys.executable, "-c", "import pkg.protocol as m; print(m.WHO)"], cwd=p.parent, capture_output=True, text=True)
(p / "protocol" / "__init__.py").write_text("WHO = 'shadow package'\n")
r1 = subprocess.run([sys.executable, "-c", "import pkg.protocol as m; print(m.WHO)"], cwd=p.parent, capture_output=True, text=True)
out["V5_shadow"] = {"before": r0.stdout.strip(), "after_init_committed": r1.stdout.strip()}
print(json.dumps(out, indent=1))
