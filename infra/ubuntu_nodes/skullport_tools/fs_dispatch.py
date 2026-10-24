#!/usr/bin/env python3
"""Fleet fightsim sweep dispatcher (Achilles, ELSA). Rebuilt 2026-10-24 after the reset.

  prepare REV   build the musl fightsim at REV on the build host (ubu008), export the data subset the engine reads,
                push binary + data to every shard node as ~/fs_shards/<rev12>/{fightsim,data/}, verify --kinds.
  run REV --kinds a,b --levels 8-14 [--parties solo,four] [--seeds 200] [--shard 2] [--slots ubu001:2,...]
                fight the grid on the shard nodes (gated: pkg temp < 80 C, no cargo/rustc/blender/pytest, load5 <
                nproc-1, no ~/skullport/STOP_ALL; nice 15 on the QA CPUs), merge cells.jsonl, build the report with
                the repo's own tools/combat/sweep.py --report-only on the build host, publish to
                ubu005:~/fleet_reports/combat_<rev12>/ and print a compact summary.

Seeds come from hash(cell, seed-base, i) inside the binary, so the shard layout never changes a result.
Same method as combat-sweep-1 / the 02a931d62 fleet sweep.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

USER = "jcraig"
NODES = {  # name: (ip, qa cpu set for taskset)
    "ubu001": ("192.168.1.218", "2-3"),
    "ubu003": ("192.168.1.220", "2-3"),
    "ubu004": ("192.168.1.221", "2-3"),
    "ubu005": ("192.168.1.222", "4-7"),
    "ubu006": ("192.168.1.225", "2-3"),
    "ubu008": ("192.168.1.231", "2-7"),
    "ubu009": ("192.168.1.230", "2-7"),
}
BUILD_HOST = "ubu008"
BUILD_CLONE = "~/SmugglersHole"
REPORT_HOST = "ubu005"
REPORT_DIR = "~/fleet_reports"
DEFAULT_SLOTS = "ubu001:2,ubu003:1,ubu006:2,ubu009:2,ubu008:2"
PARTIES = {"solo": ["fighter"], "four": ["fighter", "cleric", "wizard", "rogue"]}
# the data subset the engine opens (paths.rs data_root/engine_dir users); same set as the nodes' old ~/SmugglersHole export
DATA_PATHS = ("content/skullport/economy content/skullport/items content/skullport/outfits content/skullport/quests "
              "content/skullport/art/weapons engine/data src/skullport web/data/appearances.json")
SSH = ["ssh", "-T", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", "-o", "ServerAliveInterval=30"]
HERE = Path(__file__).resolve().parent
LOG_LOCK = threading.Lock()
LOG_FH = None


def log(msg):
    line = f"{time.strftime('%H:%M:%SZ', time.gmtime())} {msg}"
    with LOG_LOCK:
        print(line, flush=True)
        if LOG_FH:
            LOG_FH.write(line + "\n")
            LOG_FH.flush()


def ip(node):
    return NODES[node][0]


def ssh(node, script, stdin=None, timeout=3600, check=True):
    """Run a bash script on the node; returns CompletedProcess (text)."""
    # bytes in and out: text mode on Windows would turn every newline into CRLF and break the remote bash
    if stdin is None:
        cmd, data = SSH + [f"{USER}@{ip(node)}", "bash", "-s"], script
    else:
        cmd, data = SSH + [f"{USER}@{ip(node)}", "bash", "-c", shlex.quote(script)], stdin
    r = subprocess.run(cmd, input=data.encode("utf-8"), capture_output=True, timeout=timeout)
    r.stdout = r.stdout.decode("utf-8", "replace")
    r.stderr = r.stderr.decode("utf-8", "replace")
    if check and r.returncode != 0:
        raise RuntimeError(f"{node}: exit {r.returncode}: {r.stderr[-2000:]}")
    return r


def scp(src, dst, timeout=600):
    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", src, dst], check=True, timeout=timeout)


def rev12(rev):
    return rev[:12]


# ----------------------------------------------------------------------------------------------------------- prepare

def prepare(a):
    rev = a.rev
    build = a.build_host
    log(f"prepare {rev}: fetch + resolve on {build}")
    fetch_bundle = ""
    if a.bundle:
        # a git bundle M1 left on ubu005 (the nodes hold no keys for each other: route it through ELSA)
        name = Path(a.bundle).name
        stage = HERE / "fs_stage"
        stage.mkdir(parents=True, exist_ok=True)
        scp(f"{USER}@{ip(REPORT_HOST)}:{a.bundle}", str(stage / name))
        ssh(build, "mkdir -p ~/fs_bundles")
        scp(str(stage / name), f"{USER}@{ip(build)}:fs_bundles/{name}")
        fetch_bundle = (f"git bundle verify ~/fs_bundles/{name} >/dev/null && "
                        f"git fetch -q ~/fs_bundles/{name} '+refs/heads/*:refs/bundles/*' '+refs/tags/*:refs/bundles/tags/*' 2>/dev/null || "
                        f"git fetch -q ~/fs_bundles/{name} '+HEAD:refs/bundles/HEAD'")
        log(f"bundle {name} staged on {build}")
    out = ssh(build, f"""set -e
cd {BUILD_CLONE}
git fetch -q origin
{fetch_bundle}
git rev-parse --verify --quiet '{rev}^{{commit}}' || git rev-parse --verify --quiet 'refs/bundles/{rev}^{{commit}}' || git rev-parse --verify 'origin/{rev}^{{commit}}'
""").stdout.strip().splitlines()[-1]
    full = out
    r12 = rev12(full)
    log(f"resolved {rev} -> {full}")
    gate = ssh(build, "pgrep -u $USER -x 'cargo|rustc|blender' >/dev/null && echo BUSY || echo IDLE").stdout.strip()
    if gate != "IDLE" and not a.force:
        sys.exit(f"{build} is building something else (cargo/rustc/blender); wait or --force")
    log(f"worktree + musl build on {build} (about 2 min)")
    script = f"""set -e
export PATH=$HOME/.cargo/bin:$PATH
cd {BUILD_CLONE}
WT=$HOME/sh_wt_fs/{r12}
if [ ! -d "$WT" ]; then git worktree add -q --detach "$WT" {full}; fi
cd "$WT/engine/skullport-engine"
CARGO_TARGET_DIR=$HOME/sh_target_fightsim nice -n 10 taskset -c {a.build_cpus} cargo build -q --release -j {a.build_jobs} --bin fightsim --target x86_64-unknown-linux-musl 2>&1 | tail -5
F=$HOME/sh_target_fightsim/x86_64-unknown-linux-musl/release/fightsim
D=$HOME/fs_shards/{r12}
mkdir -p "$D"
cp "$F" "$D/fightsim"
cd "$WT"
git archive --format=tar HEAD {DATA_PATHS} | gzip -1 > "$D/data.tgz"
rm -rf "$D/data" && mkdir "$D/data" && tar -xzf "$D/data.tgz" -C "$D/data"
echo {full} > "$D/data/COMMIT"
echo {full} > "$D/COMMIT"
echo "sha256=$(sha256sum $D/fightsim | cut -c1-16) data_bytes=$(stat -c %s $D/data.tgz) rustc=$(rustc -V | awk '{{print $2}}')"
SK_DATA_ROOT=$D/data $D/fightsim --kinds | wc -l
"""
    t0 = time.time()
    r = ssh(build, script, timeout=1800)
    log(f"build done in {time.time() - t0:.0f}s: " + " | ".join(r.stdout.strip().splitlines()[-2:]))
    # fan out via ELSA (the nodes hold no keys for each other)
    stage = HERE / "fs_stage" / r12
    stage.mkdir(parents=True, exist_ok=True)
    scp(f"{USER}@{ip(build)}:fs_shards/{r12}/fightsim", str(stage / "fightsim"))
    scp(f"{USER}@{ip(build)}:fs_shards/{r12}/data.tgz", str(stage / "data.tgz"))
    nodes = [n for n in a.nodes.split(",") if n and n != build]
    want = [k for k in a.expect_kinds.split(",") if k]
    for n in nodes:
        ssh(n, f"mkdir -p ~/fs_shards/{r12}")
        scp(str(stage / "fightsim"), f"{USER}@{ip(n)}:fs_shards/{r12}/fightsim")
        scp(str(stage / "data.tgz"), f"{USER}@{ip(n)}:fs_shards/{r12}/data.tgz")
        chk = ssh(n, f"""set -e
D=~/fs_shards/{r12}; chmod +x $D/fightsim
rm -rf $D/data && mkdir $D/data && tar -xzf $D/data.tgz -C $D/data && echo {full} > $D/data/COMMIT && echo {full} > $D/COMMIT
SK_DATA_ROOT=$D/data $D/fightsim --kinds > $D/kinds.txt
echo "kinds=$(wc -l < $D/kinds.txt) sha256=$(sha256sum $D/fightsim | cut -c1-16)"
for k in {' '.join(want)}; do grep -qx "$k" $D/kinds.txt && echo "  $k ok" || echo "  $k MISSING"; done
""").stdout.strip()
        log(f"{n}: " + " ".join(chk.split()))
    if want:
        chk = ssh(build, f"D=~/fs_shards/{r12}; SK_DATA_ROOT=$D/data $D/fightsim --kinds > $D/kinds.txt; "
                         f"for k in {' '.join(want)}; do grep -qx \"$k\" $D/kinds.txt && echo \"$k ok\" || echo \"$k MISSING\"; done").stdout
        log(f"{build}: " + " ".join(chk.split()))
    log(f"prepared {r12} on {build},{','.join(nodes)}")
    print(full)


# --------------------------------------------------------------------------------------------------------------- run

def party_spec(name, level):
    return ",".join(f"{c}:{level}" for c in PARTIES[name])


def levels_of(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            lo, hi = part.split("-")
            out += list(range(int(lo), int(hi) + 1))
        elif part:
            out.append(int(part))
    return out


REMOTE_RUN = r"""
set -u
D=~/fs_shards/__R12__
T=$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1); T=${T:-0}; T=$((T/1000))
for z in /sys/class/thermal/thermal_zone*; do [ "$(cat $z/type)" = x86_pkg_temp ] && T=$(( $(cat $z/temp) / 1000 )); done
L5=$(awk '{print $2}' /proc/loadavg); N=$(nproc)
[ -e ~/skullport/STOP_ALL ] && { echo "GATE stop_all" >&2; exit 75; }
[ "$T" -ge __TMAX__ ] && { echo "GATE hot ${T}C" >&2; exit 75; }
pgrep -u $USER -x 'cargo|rustc|blender|pytest' >/dev/null && { echo "GATE busy" >&2; exit 75; }
awk -v l="$L5" -v n="$N" 'BEGIN{exit !(l >= n-1)}' && { echo "GATE load $L5" >&2; exit 75; }
echo "GATE ok ${T}C load $L5" >&2
cat > $D/cells.$$.txt
SK_DATA_ROOT=$D/data nice -n 15 taskset -c __CPUS__ $D/fightsim --cells-file $D/cells.$$.txt --seeds __SEEDS__ --seed-base __BASE__ --cap-s __CAP__
rc=$?
rm -f $D/cells.$$.txt
exit $rc
"""


def run(a):
    global LOG_FH
    full = a.rev
    r12 = rev12(full)
    out = Path(a.out) if a.out else HERE / f"combat_{r12}"
    (out / "shards").mkdir(parents=True, exist_ok=True)
    LOG_FH = open(out / "run.log", "a", encoding="utf-8")
    kinds = [k for k in a.kinds.split(",") if k]
    levels = levels_of(a.levels)
    parties = a.parties.split(",")
    cells = [f"{party_spec(p, l)}/{k}" for l in levels for p in parties for k in kinds]
    shards = [cells[i:i + a.shard] for i in range(0, len(cells), a.shard)]
    slots = []
    for s in a.slots.split(","):
        n, c = s.split(":")
        slots += [(n, i) for i in range(int(c))]
    log(f"run {r12}: {len(kinds)} kinds x {len(levels)} levels x {len(parties)} parties = {len(cells)} cells, "
        f"{a.seeds} seeds -> {len(cells) * a.seeds} fights in {len(shards)} shards over {len(slots)} slots "
        f"({a.slots}); out {out}")
    queue = list(enumerate(shards))
    qlock = threading.Lock()
    done = {}
    failed = []
    retries = defaultdict(int)

    def worker(node, slot):
        cpus = NODES[node][1]
        script = (REMOTE_RUN.replace("__R12__", r12).replace("__TMAX__", str(a.tmax)).replace("__CPUS__", cpus)
                  .replace("__SEEDS__", str(a.seeds)).replace("__BASE__", str(a.seed_base)).replace("__CAP__", str(a.cap_s)))
        backoff = 0
        while True:
            with qlock:
                if not queue:
                    return
                idx, sh = queue.pop(0)
            t0 = time.time()
            try:
                r = ssh(node, script, stdin="".join(c + "\n" for c in sh), timeout=a.shard_timeout, check=False)
            except Exception as e:  # ssh failure / timeout
                r = None
                err = str(e)
            if r is not None and r.returncode == 0:
                rows = [ln for ln in r.stdout.splitlines() if ln.strip()]
                (out / "shards" / f"s{idx:04d}.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
                done[idx] = len(rows)
                log(f"{node}#{slot} shard {idx + 1}/{len(shards)} ok: {len(rows)} fights in {time.time() - t0:.0f}s "
                    f"({r.stderr.strip().splitlines()[0] if r.stderr.strip() else ''}); {len(queue)} left")
                backoff = 0
                continue
            gate = r is not None and r.returncode == 75
            err = (r.stderr.strip()[-300:] if r is not None else err)
            with qlock:
                queue.insert(0, (idx, sh))  # give it back
                retries[idx] += 0 if gate else 1
                if retries[idx] > a.retries:
                    queue.pop(0)
                    failed.append((idx, sh, err))
                    log(f"{node}#{slot} shard {idx + 1} FAILED for good: {err}")
                    continue
            backoff = min(300, backoff + 60) if gate else 20
            log(f"{node}#{slot} shard {idx + 1} {'gated' if gate else 'error'}: {err}; retry in {backoff}s")
            time.sleep(backoff)
            if gate and backoff >= 300 and a.drop_hot:
                log(f"{node}#{slot} leaves the pool (gated too long)")
                return

    threads = [threading.Thread(target=worker, args=s, daemon=True) for s in slots]
    t0 = time.time()
    for t in threads:
        t.start()
        time.sleep(0.3)
    for t in threads:
        t.join()
    nfights = sum(done.values())
    log(f"fights done: {nfights} in {time.time() - t0:.0f}s; shards ok {len(done)}/{len(shards)}, failed {len(failed)}")
    if len(done) != len(shards):
        for idx, sh, err in failed:
            log(f"  failed shard {idx}: {sh[:2]}... {err}")
        if not a.partial:
            sys.exit("incomplete; rerun (finished shards are kept in shards/; use --resume) or pass --partial")
    rows = []
    for f in sorted((out / "shards").glob("s*.jsonl")):
        rows += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    rows.sort(key=lambda r: (r["party"], r["monsters"], r["seed"]))
    (out / "cells.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    log(f"cells.jsonl: {len(rows)} fights")
    report(a, full, r12, out, levels)


def report(a, full, r12, out, levels):
    build = a.build_host
    log(f"report via tools/combat/sweep.py --report-only on {build}")
    wt = f"~/sh_wt_fs/{r12}"
    ssh(build, f"mkdir -p {wt}/build/combat")
    scp(str(out / "cells.jsonl"), f"{USER}@{ip(build)}:sh_wt_fs/{r12}/build/combat/cells.jsonl")
    r = ssh(build, f"cd {wt} && python3 tools/combat/sweep.py --report-only --golems --seeds {a.seeds} --seed-base {a.seed_base} "
                   f"--levels {','.join(map(str, levels))} --out build/combat/report.md 2>&1 | tail -3")
    log("sweep.py: " + r.stdout.strip().replace("\n", " | "))
    scp(f"{USER}@{ip(build)}:sh_wt_fs/{r12}/build/combat/report.md", str(out / "report.md"))
    scp(f"{USER}@{ip(build)}:sh_wt_fs/{r12}/build/combat/report.json", str(out / "report.json"))
    summary = summarize(out, full, a)
    (out / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    if not a.no_publish:
        dest = f"{REPORT_DIR}/combat_{r12}"
        ssh(REPORT_HOST, f"mkdir -p {dest}")
        for f in ("cells.jsonl", "report.md", "report.json", "summary.md", "run.log"):
            scp(str(out / f), f"{USER}@{ip(REPORT_HOST)}:fleet_reports/combat_{r12}/{f}")
        log(f"published to {REPORT_HOST}:{dest}/")


def summarize(out, full, a):
    js = json.loads((out / "report.json").read_text(encoding="utf-8"))
    cells = js["cells"]
    kinds = sorted({c["kind"] for c in cells})
    levels = sorted({c["level"] for c in cells})
    L = [f"# Fleet combat sweep {full[:9]} (data {js['meta']['data']}, {js['meta']['seeds']} seeds/cell, "
         f"{len(cells)} cells, {sum(c['n'] for c in cells)} fights)", ""]
    for party in ("solo", "four"):
        L += [f"## {party}: win % / ttk p50 s by level", "", "| kind | " + " | ".join(f"L{l}" for l in levels) + " | mean win |",
              "|--|" + "--|" * (len(levels) + 1)]
        rank = []
        for k in kinds:
            row, ws = [], []
            for l in levels:
                c = next((c for c in cells if c["kind"] == k and c["level"] == l and c["party"] == party), None)
                if c:
                    row.append(f"{c['win']:.0%} / {c['ttk_p50']:.0f}")
                    ws.append(c["win"])
                else:
                    row.append("")
            mean = sum(ws) / len(ws) if ws else 0
            rank.append((mean, k))
            L.append(f"| {k} | " + " | ".join(row) + f" | {mean:.0%} |")
        rank.sort(reverse=True)
        L += ["", "Order, easiest to hardest (mean win over the levels): " + " > ".join(f"{k} ({m:.0%})" for m, k in rank), ""]
    flags = [f for f in js["flags"] if f["code"] in ("one_shot_risk", "stalemate", "slog")]
    if flags:
        L += ["## Safety flags (one-shot, stalemate, slog)", ""]
        for f in flags[:15]:
            L.append(f"- {f['kind']} {f['party']} L{f['level']}: {f['code']}: {f['text']}")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("rev")
    p.add_argument("--build-host", default=BUILD_HOST)
    p.add_argument("--build-cpus", default="2-7")
    p.add_argument("--build-jobs", type=int, default=6)
    p.add_argument("--nodes", default="ubu001,ubu003,ubu006,ubu009,ubu008")
    p.add_argument("--expect-kinds", default="", help="kinds that must exist in the built binary's --kinds list")
    p.add_argument("--force", action="store_true")
    p.add_argument("--bundle", default="", help="path on ubu005 of a git bundle holding REV (M1's hand-off when not on GitHub)")
    p.set_defaults(fn=prepare)
    r = sub.add_parser("run")
    r.add_argument("rev", help="full sha from prepare")
    r.add_argument("--kinds", required=True)
    r.add_argument("--levels", default="8-14")
    r.add_argument("--parties", default="solo,four")
    r.add_argument("--seeds", type=int, default=200)
    r.add_argument("--seed-base", type=int, default=0)
    r.add_argument("--cap-s", type=float, default=600.0)
    r.add_argument("--shard", type=int, default=2, help="cells per shard")
    r.add_argument("--slots", default=DEFAULT_SLOTS)
    r.add_argument("--tmax", type=int, default=80)
    r.add_argument("--shard-timeout", type=int, default=3600)
    r.add_argument("--retries", type=int, default=2)
    r.add_argument("--drop-hot", action="store_true")
    r.add_argument("--partial", action="store_true")
    r.add_argument("--no-publish", action="store_true")
    r.add_argument("--build-host", default=BUILD_HOST)
    r.add_argument("--out", default="")
    r.set_defaults(fn=run)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
