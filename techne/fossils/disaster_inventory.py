"""What is actually lost if this host dies (batch 11 P8).

Measurement only. No same-host directory is a mirror, and nothing here pretends SINGLE_HOST_RISK is
solved. The point is to say precisely WHAT is at risk, because the answer is not uniform:

  TRACKED HALF   records, recipes, harnesses, constraints, hash manifests, every behavioural
                 dataset. These live in git and are pushed to origin/main, so they are ALREADY
                 off-host. Losing this machine does not lose them.
  BODIES         the preserved upstream trees under the vault root. Gitignored, single-host.
                 Recoverable only insofar as upstream still serves the pinned revision.
  WORLDS         the container images. The prometheus-fossil-* ones are built locally and exist in
                 no registry: if this host dies they are gone, and a rebuild from a Dockerfile pulls
                 fresh packages and is therefore a DIFFERENT world.

    python -m techne.fossils.disaster_inventory [--probe] [--out F]

--probe additionally asks whether each distinct upstream still responds. Reachability today is NOT
proof of exact recoverability: it means the host answered, not that the bytes still hash the same.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.request

from . import record, vault


def _reachable(url: str, timeout=12) -> str:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "techne-fossil-vault"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return "OK_%d" % r.status
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):                      # HEAD refused; try a ranged GET
            try:
                req = urllib.request.Request(url, headers={"Range": "bytes=0-0",
                                                           "User-Agent": "techne-fossil-vault"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return "OK_%d" % r.status
            except Exception:
                return "HTTP_%d" % e.code
        return "HTTP_%d" % e.code
    except Exception as e:
        return "ERR_%s" % type(e).__name__


def _git_alive(url: str, timeout=25) -> str:
    try:
        p = subprocess.run(["git", "ls-remote", "--exit-code", "-h", url],
                           capture_output=True, text=True, timeout=timeout)
        return "OK" if p.returncode == 0 else "GONE_%d" % p.returncode
    except Exception as e:
        return "ERR_%s" % type(e).__name__


def inventory(probe=False) -> dict:
    sp = vault.specimen_dir("_").parent
    ids = [d.name for d in sorted(sp.iterdir()) if (d / "record.json").exists()]

    bodies, url_arts, git_arts, bytes_total = 0, {}, {}, 0
    for sid in ids:
        up = vault.body_dir(sid) / "upstream"
        if up.exists():
            bodies += 1
        rec = record.load(sid)
        bytes_total += int((rec.get("hashes") or {}).get("bytes") or 0)
        hashes = (rec.get("hashes") or {}).get("artifacts") or []
        for a in (rec.get("source_origin") or {}).get("artifacts") or []:
            pin = record.established_pin(a, hashes)
            if a.get("kind") == "url":
                url_arts.setdefault(a.get("url", ""), {"specimens": [], "pinned": bool(pin)})["specimens"].append(sid)
            elif a.get("kind") == "git":
                git_arts.setdefault(a.get("url", ""), {"specimens": [], "pinned": bool(pin)})["specimens"].append(sid)

    images = {}
    imf = pathlib.Path("techne/fossils/WORLD_IMAGES.json")
    if imf.exists():
        images = json.loads(imf.read_text(encoding="utf-8")).get("images", {})
    local_only = [k for k, v in images.items() if v.get("origin") == "LOCAL_BUILD_NO_UPSTREAM"]

    datasets = sorted(p.name for p in pathlib.Path("techne/fossils/pressure").glob("*.json"))

    reach = {}
    if probe:
        for u in sorted(url_arts):
            if u:
                reach[u] = _reachable(u)
        for u in sorted(git_arts):
            if u:
                reach[u] = _git_alive(u)

    gone = sorted(u for u, s in reach.items() if not s.startswith("OK"))
    doc = {"schema": "techne.fossil.disaster_inventory/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "single_host_risk": "UNCHANGED -- no independent physical destination exists",
           "off_host_already": {
               "what": "the entire tracked half: records, recipes, harnesses, world constraints, hash "
                       "manifests, instruments and every behavioural dataset",
               "where": "git, pushed to origin/main",
               "behavioural_datasets": len(datasets), "dataset_files": datasets},
           "at_risk_bodies": {"count": bodies, "bytes": bytes_total,
                              "distinct_url_upstreams": len(url_arts),
                              "distinct_git_upstreams": len(git_arts),
                              "note": "gitignored and single-host; recoverable only insofar as upstream "
                                      "still serves the pinned revision AND the bytes still match"},
           "at_risk_worlds": {"images_referenced": len(images),
                              "local_build_no_upstream": len(local_only),
                              "irreplaceable_images": sorted(local_only),
                              "note": "a rebuild from a Dockerfile pulls fresh packages and is a "
                                      "DIFFERENT world, so these are not reconstructible, only replaceable"},
           "upstream_probe": {"performed": bool(probe), "checked": len(reach),
                              "unreachable": gone, "n_unreachable": len(gone),
                              "caveat": "reachability is not exact recoverability: the host answered, "
                                        "which is not the same as the bytes still hashing identically",
                              "results": reach},
           }
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    d = inventory(a.probe)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("OFF-HOST ALREADY : tracked half in git (%d behavioural datasets)"
          % d["off_host_already"]["behavioural_datasets"])
    print("AT RISK  bodies  : %d (%.1f GB) across %d url + %d git upstreams"
          % (d["at_risk_bodies"]["count"], d["at_risk_bodies"]["bytes"] / 1e9,
             d["at_risk_bodies"]["distinct_url_upstreams"], d["at_risk_bodies"]["distinct_git_upstreams"]))
    print("AT RISK  worlds  : %d images, %d built locally and irreplaceable"
          % (d["at_risk_worlds"]["images_referenced"], d["at_risk_worlds"]["local_build_no_upstream"]))
    if a.probe:
        print("UPSTREAM PROBE   : %d checked, %d unreachable" % (d["upstream_probe"]["checked"],
                                                                 d["upstream_probe"]["n_unreachable"]))
        for u in d["upstream_probe"]["unreachable"][:12]:
            print("   GONE/ERR %-8s %s" % (d["upstream_probe"]["results"][u], u[:88]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
