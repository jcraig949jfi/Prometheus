"""Decoy check on the Aug-2026 autopsy observable for Argos.
The autopsy (AGENT_AUTOPSIES.jsonl, Aporia P46) cites '13 catalog .md files (count grew 11->13 then froze)'
as Argos's frozen output and CND_FRAME@v1's catalog anchors as its live consumer.
Test: git first-commit date of every harmonia/memory/catalogs/*.md vs Argos's first commit.
If every catalog predates Argos, the observable belongs to a different producer (identity error) and
PRODUCER-HALT-WITH-LIVE-CONSUMER is built on misattributed output. Run from repo root."""
import subprocess, glob, os, json
OUT = {}
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
cats = sorted(glob.glob("harmonia/memory/catalogs/*.md"))
OUT["catalog_files"] = {}
for c in cats:
    first = git("log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", c).splitlines()
    OUT["catalog_files"][os.path.basename(c)] = first[-1] if first else "UNTRACKED"
argos_first = git("log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", "harmonia/agents/argos").splitlines()
OUT["argos_first_commit"] = argos_first[-1] if argos_first else None
argos_date = OUT["argos_first_commit"].split()[1] if OUT["argos_first_commit"] else "9999"
OUT["n_catalogs"] = len(cats)
OUT["n_catalogs_committed_before_argos_existed"] = sum(1 for v in OUT["catalog_files"].values() if v != "UNTRACKED" and v.split()[1] < argos_date)
OUT["n_catalogs_authored_by_argos_commits"] = sum(1 for c in cats if "argos" in git("log", "--format=%s %an", "--", c).lower())
# does any catalog *text* claim Argos authorship?
OUT["n_catalogs_mentioning_argos_in_body"] = sum(1 for c in cats if "argos" in open(c, encoding="utf-8", errors="replace").read().lower())
OUT["verdict_on_observable"] = ("IDENTITY_ERROR: all catalogs predate Argos" if OUT["n_catalogs_committed_before_argos_existed"] == len(cats)
                                else "observable partially attributable to Argos")
sp = os.environ.get("SP", os.path.dirname(os.path.abspath(__file__)))
json.dump(OUT, open(os.path.join(sp, "argos_catalog_authorship_result.json"), "w"), indent=1)
print(json.dumps(OUT, indent=1))
