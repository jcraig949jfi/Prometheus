"""The 68 ghost worlds: what is actually behind 'reproducible' (batch 12 P8).

Batch 11 reported 74/117 reproducible worlds and flagged that 68 depend on an image existing in no
registry. This measures what that really means, per image, mechanically.

Classification, per the charter:
  REBUILDABLE_EXACT          a build recipe exists AND all of its inputs are pinned
  REBUILDABLE_NOT_BIT_EXACT  a build recipe exists but at least one input floats, so a rebuild
                             produces a functionally similar world with different bytes
  LOCAL_ONLY_UNRECOVERABLE   no build recipe is preserved; if the host dies the world is gone
  UNKNOWN                    cannot be established

A Dockerfile is NOT sufficient if its inputs float. `FROM debian:bookworm-slim` is a MUTABLE TAG:
the same Dockerfile built tomorrow starts from different bytes. `apt-get install` with no version
pin resolves against a live index. Both make a rebuild functionally-similar, never identical.

    python -m techne.fossils.ghost_worlds [--out F]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import time

from . import vault

ENVDIR = pathlib.Path("techne/fossils/environment")
IMAGES_FILE = pathlib.Path("techne/fossils/WORLD_IMAGES.json")
WORLD_FILE = pathlib.Path("techne/fossils/WORLD_PRESERVATION_2026-09-13.json")


def _find_dockerfile(image: str):
    """Match prometheus-fossil-<name>:tag to its preserved build recipe."""
    m = re.match(r"prometheus-fossil-([a-z0-9]+):", image)
    if not m:
        return None
    stem = m.group(1)
    for p in list(ENVDIR.glob("*.Dockerfile")) + list(
            pathlib.Path("techne/fossils/specimens").glob("*/environment/*.Dockerfile")):
        if stem in p.name.lower().replace("-", ""):
            return p
        if re.search(r"fossil-%s-" % stem, p.name):
            return p
    # goexplore-style names live beside their specimen
    for p in pathlib.Path("techne/fossils/specimens").glob("*/environment/*.Dockerfile"):
        if stem.startswith(p.name.split("-")[0].lower()):
            return p
    return None


def analyse(image: str, info: dict, dependents: list) -> dict:
    df = _find_dockerfile(image)
    row = {"image": image, "origin": info.get("origin"), "image_id": (info.get("id") or "")[:19],
           "dependent_fossils": len(dependents), "dependents": sorted(dependents)}
    if df is None:
        row.update({"classification": "LOCAL_ONLY_UNRECOVERABLE", "dockerfile": None,
                    "why": "no preserved build recipe found for this image"})
        return row
    txt = df.read_text(encoding="utf-8", errors="replace")
    base = re.search(r"^FROM\s+(\S+)", txt, re.M)
    base_ref = base.group(1) if base else ""
    base_pinned = "@sha256:" in base_ref
    apt = bool(re.search(r"apt-get\s+(?:-\S+\s+)*install", txt))
    apt_pinned = bool(re.search(r"apt-get[^\n]*=\d", txt))
    git_pins = re.findall(r"git checkout --quiet ([0-9a-f]{40})", txt) + \
               re.findall(r"checkout\s+([0-9a-f]{40})", txt)
    floats = []
    if not base_pinned:
        floats.append("base image '%s' is a MUTABLE TAG, not a digest" % base_ref)
    if apt and not apt_pinned:
        floats.append("apt-get install with no version pins resolves against a live index")
    row.update({"dockerfile": str(df).replace("\\", "/"), "base_image": base_ref,
                "base_pinned_by_digest": base_pinned, "apt_install": apt,
                "apt_version_pinned": apt_pinned, "source_commits_pinned": sorted(set(git_pins)),
                "floating_inputs": floats,
                "classification": "REBUILDABLE_EXACT" if not floats else "REBUILDABLE_NOT_BIT_EXACT",
                "why": "all inputs pinned" if not floats else "; ".join(floats)})
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    images = json.loads(IMAGES_FILE.read_text(encoding="utf-8"))["images"]
    world = json.loads(WORLD_FILE.read_text(encoding="utf-8"))["rows"]
    deps = {}
    for r in world:
        img = r.get("world_image") or ""
        if img:
            deps.setdefault(img, []).append(r["specimen_id"])

    rows = [analyse(img, info, deps.get(img, []))
            for img, info in sorted(images.items())
            if info.get("origin") == "LOCAL_BUILD_NO_UPSTREAM"]
    rows.sort(key=lambda r: -r["dependent_fossils"])

    tally = {}
    for r in rows:
        tally[r["classification"]] = tally.get(r["classification"], 0) + 1

    rescue = [{"rank": i + 1, "image": r["image"], "dependent_fossils": r["dependent_fossils"],
               "classification": r["classification"],
               "action": ("docker save to a content-addressed tarball held OFF-HOST -- the only step "
                          "that preserves these exact bytes; rebuilding cannot") if r["dependent_fossils"]
               else "low priority: no fossil currently depends on it"}
              for i, r in enumerate(rows)]

    doc = {"schema": "techne.fossil.ghost_worlds/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "question": "are the 68 local-image-dependent worlds recoverable, and how?",
           "n_local_images": len(rows), "by_classification": tally,
           "total_dependent_fossils": sum(r["dependent_fossils"] for r in rows),
           "finding": "A preserved Dockerfile makes these worlds REPLACEABLE IN FUNCTION, not "
                      "RECOVERABLE IN IDENTITY. Every recipe starts FROM a mutable tag and installs "
                      "packages from a live index, so a rebuild is a different world -- which is "
                      "exactly the distinction batch 11 showed can change an answer.",
           "rescue_action": "docker save each image to a content-addressed tarball stored off-host. "
                            "That preserves the bytes the receipts were produced in. Pinning FROM by "
                            "digest and snapshotting apt would make FUTURE rebuilds exact, but cannot "
                            "recover the images that already exist.",
           "ranked_rescue_list": rescue, "rows": rows}
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("local-build images: %d   dependent fossils: %d" % (len(rows), doc["total_dependent_fossils"]))
    print("classification:", tally)
    print("%-38s %5s  %-26s %s" % ("image", "deps", "classification", "floating inputs"))
    for r in rows:
        print("%-38s %5d  %-26s %s" % (r["image"], r["dependent_fossils"], r["classification"],
                                       "; ".join(r.get("floating_inputs", []))[:60]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
