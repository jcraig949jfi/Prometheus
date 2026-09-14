"""World preservation: four axes, one small lattice (batch 11 P1).

Batch 10 measured whether the BODY is preserved. That is the lower half of the hierarchy. A fossil
can have an exact, verifying body and still have no reproducible world:

    SOURCE PRESENT < BODY PINNED < DEPENDENCY CLOSURE PINNED < EXECUTION WORLD PINNED
                                                             < BEHAVIOR REPRODUCIBLE

Four axes, each on the SAME 4-level lattice so they compose:

    0 UNKNOWN    the evidence cannot establish a state
    1 FLOATING   composition can change with no notice -- a network fetch in this phase, or a
                 native-host toolchain. Re-running later may not re-run the same thing.
    2 NAMED      a specific named world is used, but its identity is not recorded. A mutable tag
                 (":bookworm") is NAMED, never PINNED: the name can be re-pointed at new bytes.
    3 PINNED     the exact identity is recorded (image digest) AND no network fetch in this phase.

Axes:
    BODY_PRESERVATION            are the preserved bytes present, complete and verifying?
    EXTERNAL_SOURCE_PRESERVATION does the record name an EXACT upstream revision (sha256/40-hex)?
    BUILD_WORLD_PRESERVATION     is the world the BUILD steps execute in fixed?
    RUN_WORLD_PRESERVATION       is the world the RUN steps execute in fixed?

PINNED on the source axis means the REQUEST is exact. It does NOT claim upstream still serves it --
that is the disaster inventory's question, not this one.

    python -m techne.fossils.world --capture            record image identities (needs docker)
    python -m techne.fossils.world --census --out F     backfill all specimens
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import time

from . import record, vault

LEVELS = {-1: "N_A", 0: "UNKNOWN", 1: "FLOATING", 2: "NAMED", 3: "PINNED"}
IMAGES_FILE = pathlib.Path("techne/fossils/WORLD_IMAGES.json")

# a network fetch anywhere in a phase makes that phase's world floating, whatever image is used
_FETCH = re.compile(r"(apt-get\s+(?:-\S+\s+)*install|apt-get\s+update|pip3?\s+install|npm\s+install|"
                    r"go\s+get|cargo\s+(?:fetch|install)|gem\s+install|wget\s|curl\s|git\s+clone|"
                    r"conda\s+install)")


def _wsl(cmd: str, timeout=120):
    p = subprocess.run(["wsl.exe", "-e", "bash", "-lc", cmd], capture_output=True, text=True,
                       timeout=timeout)
    return p.stdout.strip()


def capture_images(out=IMAGES_FILE) -> dict:
    """Record the identity of every image any recipe references. A locally built image has no
    upstream to be re-pulled from: its identity is pinned but it is a UNIQUE LOCAL ARTIFACT."""
    imgs = set()
    sp = vault.specimen_dir("_").parent
    for d in sorted(sp.iterdir()):
        rp = d / "recipe.json"
        if rp.exists():
            try:
                r = json.loads(rp.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if r.get("image"):
                imgs.add(r["image"])
    rows = {}
    for img in sorted(imgs):
        raw = _wsl("docker image inspect %s --format '{{.Id}}|{{json .RepoDigests}}|{{.Created}}' "
                   "2>/dev/null || echo MISSING" % img)
        if not raw or raw.startswith("MISSING"):
            rows[img] = {"present": False, "id": "", "repo_digests": [], "created": "",
                         "origin": "UNKNOWN"}
            continue
        parts = raw.split("|")
        iid = parts[0] if parts else ""
        try:
            digests = json.loads(parts[1]) if len(parts) > 1 and parts[1] not in ("null", "") else []
        except ValueError:
            digests = []
        local_build = img.startswith("prometheus-fossil-")
        rows[img] = {"present": True, "id": iid, "repo_digests": digests or [],
                     "created": parts[2] if len(parts) > 2 else "",
                     "origin": "LOCAL_BUILD_NO_UPSTREAM" if local_build else "UPSTREAM_REGISTRY"}
    doc = {"schema": "techne.fossil.world_images/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "note": "An image ID pins WHICH bytes ran. It does not make them reconstructible: the "
                   "prometheus-fossil-* images are built locally and exist in no registry, so their "
                   "identity is pinned and their availability is single-host.",
           "images": rows}
    pathlib.Path(out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return doc


def _phase_text(recipe, phase):
    steps = recipe.get(phase) or []
    return " ".join(json.dumps(s) for s in steps)


def rp_exists(recipe):
    return bool(recipe)


def _world_level(recipe, phase, images):
    """The lattice level for one execution phase."""
    runner = recipe.get("runner")
    if not recipe.get(phase):
        if not rp_exists(recipe):
            return 0, "no recipe at all: nothing can be established about the %s world" % phase
        return -1, "this fossil has no %s steps; there is no %s world to pin" % (phase, phase)
    if _FETCH.search(_phase_text(recipe, phase)):
        # A fetch under a RECORDED FULL CLOSURE is materially different from an unconstrained one:
        # the composition is fixed by name+version, but obtaining it still depends on an external
        # service staying up. That is NAMED, not PINNED, and certainly not FLOATING.
        wc = recipe.get("world_closure") or {}
        if wc.get("constraints"):
            return 2, ("%s fetches under a recorded closure of %s pinned versions (%s); composition "
                       "is fixed, availability is not" % (phase, wc.get("n_pinned"), wc["constraints"]))
        return 1, "%s fetches from the network with no recorded closure" % phase
    if runner == "native":
        return 1, "native runner: the host toolchain is the world and is not recorded"
    img = recipe.get("image")
    if not img:
        return 0, "no image recorded for a %s runner" % runner
    info = (images or {}).get(img)
    if not info or not info.get("present"):
        return 2, "image %s named but its identity is not recorded on this host" % img
    if not info.get("id"):
        return 2, "image %s present but no identity captured" % img
    return 3, "image %s pinned to %s and no network fetch in %s" % (img, info["id"][:19], phase)


def assess(sid: str, images=None) -> dict:
    rec = record.load(sid)
    sd = vault.specimen_dir(sid)
    rp = sd / "recipe.json"
    recipe = json.loads(rp.read_text(encoding="utf-8")) if rp.exists() else {}

    # --- body
    from . import harvest
    pres = rec.get("preservation") or {}
    body_dir = vault.body_dir(sid) / "upstream"
    if not body_dir.exists():
        body = (0, "body not on this host")
    else:
        try:
            d = harvest.drift(sid)
            complete = not (pres.get("submodules_missing") or pres.get("submodules_drifted"))
            if not complete:
                body = (1, "body present but INCOMPLETE (missing/drifted submodule)")
            elif d["matches"]:
                body = (3, "tree hash matches the record")
            else:
                body = (1, "body present but DIFFERS from the record")
        except Exception as e:
            body = (0, "could not verify: %s" % str(e)[:60])

    # --- external source: does the record name an exact revision?
    arts = (rec.get("source_origin") or {}).get("artifacts") or []
    hashes = (rec.get("hashes") or {}).get("artifacts") or []
    if not arts:
        ext = (0, "no source artifacts recorded")
    else:
        unpinned = [a for a in arts if not record.established_pin(a, hashes)]
        ext = (1, "%d artifact(s) name no exact revision" % len(unpinned)) if unpinned else \
              (3, "every artifact names an exact sha256/commit")

    bw = _world_level(recipe, "build", images)
    rw = _world_level(recipe, "runs", images)
    axes = {"BODY_PRESERVATION": body, "EXTERNAL_SOURCE_PRESERVATION": ext,
            "BUILD_WORLD_PRESERVATION": bw, "RUN_WORLD_PRESERVATION": rw}
    applicable = [v[0] for v in axes.values() if v[0] >= 0]
    ok = lambda lvl: lvl == 3 or lvl == -1      # N_A phases cannot float
    out = {"specimen_id": sid,
           "axes": {k: {"level": v[0], "state": LEVELS[v[0]], "why": v[1]} for k, v in axes.items()},
           "min_level": min(applicable) if applicable else 0,
           "world_reproducible": bool(ok(bw[0]) and ok(rw[0]) and body[0] == 3),
           "world_image": recipe.get("image", ""),
           "world_is_single_host": bool(
               (images or {}).get(recipe.get("image", ""), {}).get("origin") == "LOCAL_BUILD_NO_UPSTREAM")}
    out["overall"] = LEVELS[out["min_level"]]
    return out


def census(out=None) -> dict:
    images = {}
    if IMAGES_FILE.exists():
        images = json.loads(IMAGES_FILE.read_text(encoding="utf-8")).get("images", {})
    sp = vault.specimen_dir("_").parent
    rows = []
    for d in sorted(sp.iterdir()):
        if (d / "record.json").exists():
            rows.append(assess(d.name, images))
    dist = {}
    for ax in ("BODY_PRESERVATION", "EXTERNAL_SOURCE_PRESERVATION",
               "BUILD_WORLD_PRESERVATION", "RUN_WORLD_PRESERVATION"):
        t = {}
        for r in rows:
            s = r["axes"][ax]["state"]
            t[s] = t.get(s, 0) + 1
        dist[ax] = t
    doc = {"schema": "techne.fossil.world_preservation/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "lattice": LEVELS, "n": len(rows), "distribution": dist,
           "world_reproducible_count": sum(1 for r in rows if r["world_reproducible"]),
           "world_reproducible_but_single_host": sum(1 for r in rows
                                                     if r["world_reproducible"] and r["world_is_single_host"]),
           "note": "Backfilled mechanically from existing evidence. A mutable tag is NAMED, never "
                   "PINNED. A network fetch in a phase makes that phase FLOATING whatever the image. "
                   "The distribution is not beautified.",
           "rows": rows}
    if out:
        pathlib.Path(out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.capture:
        d = capture_images()
        print("captured %d images -> %s" % (len(d["images"]), IMAGES_FILE))
        for k, v in sorted(d["images"].items()):
            print("  %-38s %-24s %s" % (k, v["origin"], (v["id"] or "")[:19]))
    if a.census or not a.capture:
        d = census(a.out)
        print("\nworld preservation census, n=%d" % d["n"])
        for ax, t in d["distribution"].items():
            print("  %-30s %s" % (ax, dict(sorted(t.items()))))
        print("  world_reproducible (body+build+run pinned or N/A): %d" % d["world_reproducible_count"])
        print("  ...of which the world image is LOCAL-BUILD-ONLY (exists in no registry): %d"
              % d["world_reproducible_but_single_host"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
