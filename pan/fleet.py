"""Machines and seats (PAN-38; operator, 2026-10-10: "all of the computers in the e-waste network ... with specs,
operating system, ram, hard drive space, GPUs" and "all seats in the Pantheon, last active, last checkin, last
work/project, active/inactive status, last machine run on").

Sources stay authoritative; Pan joins them and says where each value came from.

  machines  infra/FLEET_HOSTS.md (Achilles' register, operator-filled; read from git at HEAD) lists the machines.
            A value a probe measured replaces the register's, and every disagreement is listed, never smoothed:
              pan.host_probe        Pan's read-only probes (ssh from M2 to the Linux nodes, CIM on the local host)
              agora.machine_probes  the older per-machine probe (still reporting from harry1 only)
            Last seen: comms.agent_instances (seat sessions), fabric.agent_instances (workers), either probe.
  seats     comms.agents + comms.agent_instances (sessions, check-ins = syncs, machines), pan.commit (newest commit
            on main per seat, from the "Seat[instance]:" subject prefix), comms.messages (newest message sent),
            roles/<Seat>/WORK_STATE.json at HEAD (declared state), docs/fleet/fleet_state.json (Achilles' census:
            role line and kind, as of its own generated_at).

A seat's or machine's status is derived from its newest activity, never from a status column.
"""
import datetime as dt
import json
import re
import shutil
import subprocess
import sys

from . import REPO, host

DOC = "infra/FLEET_HOSTS.md"
CENSUS = "docs/fleet/fleet_state.json"
LINUX_USER = "jcraig"                 # FLEET_HOSTS.md, "Linux nodes": user `jcraig` on every node
NOT_SEATS = {"base-role", "generic-worker-role", "rso-builder-role", "template"}
BUCKETS = ((24, "active"), (24 * 7, "week"), (24 * 30, "month"))

PROBE_SH = r'''
kv() { printf '%s=%s\n' "$1" "$2"; }
kv hostname "$(hostname)"
kv vendor "$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null)"
kv product_name "$(cat /sys/class/dmi/id/product_name 2>/dev/null)"
kv product_version "$(cat /sys/class/dmi/id/product_version 2>/dev/null)"
kv os "$(. /etc/os-release 2>/dev/null; echo "$PRETTY_NAME")"
kv kernel "$(uname -r)"
kv uptime_s "$(cut -d. -f1 /proc/uptime)"
kv cpu_model "$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
kv threads "$(nproc --all)"
kv cores "$(lscpu -p=core,socket 2>/dev/null | grep -v '^#' | sort -u | wc -l)"
kv mem_total_kb "$(awk '/^MemTotal/{print $2}' /proc/meminfo)"
kv mem_avail_kb "$(awk '/^MemAvailable/{print $2}' /proc/meminfo)"
kv disks "$(lsblk -J -d -b -o NAME,SIZE,ROTA,TYPE,MODEL 2>/dev/null | tr -d '\n')"
kv root "$(df -B1 --output=size,avail / | tail -1)"
kv gpu "$(lspci 2>/dev/null | grep -E 'VGA|3D|Display' | cut -d: -f3- | sed 's/^ *//' | paste -sd ';' -)"
kv load "$(cut -d' ' -f1-3 /proc/loadavg)"
'''

PROBE_PS = r'''
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = @(Get-CimInstance Win32_Processor)
$pd = @(Get-PhysicalDisk | ForEach-Object { [pscustomobject]@{model=$_.FriendlyName; size=[int64]$_.Size; media=[string]$_.MediaType} })
$ld = @(Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object { [pscustomobject]@{drive=$_.DeviceID; size=[int64]$_.Size; free=[int64]$_.FreeSpace} })
$vc = @(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name })
[pscustomobject]@{
  hostname=$env:COMPUTERNAME; vendor=$cs.Manufacturer; product_name=$cs.Model; os=$os.Caption; kernel=$os.Version;
  uptime_s=[int64]((Get-Date) - $os.LastBootUpTime).TotalSeconds; cpu_model=$cpu[0].Name.Trim();
  cores=($cpu | Measure-Object NumberOfCores -Sum).Sum; threads=($cpu | Measure-Object NumberOfLogicalProcessors -Sum).Sum;
  mem_total_kb=[int64]($cs.TotalPhysicalMemory/1024); mem_avail_kb=[int64]$os.FreePhysicalMemory;
  physical_disks=$pd; volumes=$ld; gpu=($vc -join ';')
} | ConvertTo-Json -Depth 4 -Compress
'''


def git_show(path, ref="HEAD"):
    r = subprocess.run(["git", "-C", str(REPO), "show", "{}:{}".format(ref, path)], capture_output=True)
    if r.returncode:
        raise RuntimeError("git show {}:{} failed: {}".format(ref, path, r.stderr.decode("utf-8", "replace")[:200]))
    return r.stdout.decode("utf-8")


def head_sha():
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def bucket(last, now):
    """Status from the newest activity: active (24 h), week, month, inactive (older), none (nothing recorded)."""
    if last is None:
        return "none"
    h = (now - last).total_seconds() / 3600
    return next((b for lim, b in BUCKETS if h <= lim), "inactive")


def _iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def _num(rx, s, cast=float):
    m = re.search(rx, s or "")
    return cast(m.group(1)) if m else None


def _plain(s):
    return re.sub(r"\*\*|`", "", s or "").strip()


# ---------------------------------------------------------------- the register

def parse_doc(text):
    """FLEET_HOSTS.md's two host tables -> one dict per row (keys: lower-cased headers, plus _family). A table is
    a '|' header line directly above a '|---|' separator, under a '## Windows' or '## Linux' heading."""
    rows, family, lines, i = [], None, text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            family = "Windows" if "Windows" in ln else "Linux" if "Linux" in ln else None
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if family and ln.startswith("|") and re.fullmatch(r"\|[-| :]+\|", nxt):
            head = [h.strip().lower() for h in ln.strip().strip("|").split("|")]
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) == len(head):
                    rows.append(dict(zip(head, cells), _family=family))
                i += 1
            continue
        i += 1
    m = re.search(r"All (Ubuntu Server [\d.]+), kernel ([\w.-]+)", text)
    linux_os = "{} (kernel {})".format(m.group(1), m.group(2)) if m else ""
    return rows, linux_os


def _get(r, prefix):
    return next((v for k, v in r.items() if k.startswith(prefix)), "")


def register(text):
    """Register rows -> machine dicts with the register's own values (nothing measured yet)."""
    rows, linux_os = parse_doc(text)
    out = []
    for r in rows:
        win = r["_family"] == "Windows"
        cell = _get(r, "host")
        name = cell.split()[0].upper()
        label = _num(r"\((M\d+)\)", cell, str) or ""
        cpu, ram, gpu = _plain(r.get("cpu")), _plain(r.get("ram")), _plain(r.get("gpu"))
        notes = _plain(r.get("notes") if win else _get(r, "state"))
        osname = ""
        if win:
            m = re.search(r"Win(?:dows)?\s*(1[01])\s*(Home|Pro)?", notes)
            osname = "Windows {} {}".format(m.group(1), m.group(2) or "").strip() if m else ""
        else:
            osname = linux_os
        ip = _num(r"\.(\d{1,3})\b", r.get("ip") if win else r.get("net"), str)
        out.append(dict(
            host=name, label=label, name="{} ({})".format(name, label) if label else name, family=r["_family"],
            hardware=_plain(r.get("hardware")), cpu=re.sub(r",.*", "", cpu), cores=_num(r"(\d+)C/", cpu, int),
            threads=_num(r"/(\d+)T", cpu, int), ram_gb=_num(r"^(\d+(?:\.\d+)?)\s*GB", ram), ram_note=ram,
            gpu=gpu, vram_gb=_num(r"(\d+)\s*GB", gpu), disk=_plain(r.get("disk")),
            ip="192.168.1." + ip if ip else "", tags=" ".join(re.findall(r"`([^`]+)`", _get(r, "role"))),
            os=osname, notes=notes[:240]))
    return out


# ---------------------------------------------------------------- probes

def _ssh_probe(address, timeout=40):
    ssh = shutil.which("ssh")
    if not ssh:
        return None, "no ssh client on this host"
    try:
        r = subprocess.run([ssh, "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", "-o", "StrictHostKeyChecking=yes",
                            "{}@{}".format(LINUX_USER, address), "bash -s"],
                           input=PROBE_SH.encode("ascii"), capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timed out after {} s".format(timeout)
    if r.returncode:
        return None, (r.stderr.decode("utf-8", "replace").strip().splitlines() or ["exit {}".format(r.returncode)])[-1][:200]
    return parse_kv(r.stdout.decode("utf-8", "replace")), None


def parse_kv(text):
    """key=value lines from PROBE_SH -> typed facts."""
    f = {}
    for ln in text.splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            f[k.strip()] = v.strip()
    for k in ("uptime_s", "threads", "cores", "mem_total_kb", "mem_avail_kb"):
        f[k] = int(f[k]) if f.get(k, "").isdigit() else None
    try:
        disks = json.loads(f.get("disks") or "{}").get("blockdevices", [])
    except ValueError:
        disks = []
    f["physical_disks"] = [dict(model=(d.get("model") or d.get("name") or "").strip(), size=int(d.get("size") or 0),
                                media="HDD" if str(d.get("rota")) in ("1", "True", "true") else "SSD")
                           for d in disks if d.get("type") == "disk"]
    f.pop("disks", None)
    root = (f.pop("root", "") or "").split()
    f["volumes"] = [dict(drive="/", size=int(root[0]), free=int(root[1]))] if len(root) == 2 and all(
        x.isdigit() for x in root) else []
    return f


def _local_probe():
    if sys.platform != "win32":
        return None, "local probe is written for Windows hosts"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", PROBE_PS],
                           capture_output=True, timeout=120)
        f = json.loads(r.stdout.decode("utf-8", "replace"))
    except (subprocess.TimeoutExpired, ValueError) as e:
        return None, "local probe failed: {}".format(e)
    for k in ("physical_disks", "volumes"):
        if isinstance(f.get(k), dict):
            f[k] = [f[k]]
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=30).stdout.strip().splitlines()
        f["nvidia"] = [dict(name=x.split(",")[0].strip(), vram_mb=int(x.split(",")[1])) for x in out if "," in x]
    except (OSError, subprocess.TimeoutExpired, ValueError):
        f["nvidia"] = []
    return f, None


def probe(out=print, addresses=None):
    """Probe every Linux node in the register (ssh, read-only) and the local host if it is in the register; one
    pan.host_probe row per attempt, failures included. `addresses` ({host: address}) overrides the targets."""
    from . import db
    machines = register(git_show(DOC))
    targets = addresses or {m["host"]: m["ip"] for m in machines if m["family"] == "Linux" and m["ip"]}
    run_id = "fleet-probe-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    results = {}
    for h, addr in sorted(targets.items()):
        facts, err = _ssh_probe(addr)
        results[h] = ("ssh", addr, facts, err)
    if addresses is None and host() in {m["host"] for m in machines}:
        facts, err = _local_probe()
        results[host()] = ("local", None, facts, err)
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, git_sha) values (%s, 'fleet-probe', %s, %s)",
                    (run_id, host(), head_sha()))
        for h, (method, addr, facts, err) in results.items():
            cur.execute("""insert into pan.host_probe (host, address, method, ok, facts, error, run_id)
                           values (%s, %s, %s, %s, %s, %s, %s)""",
                        (h, addr, method, facts is not None, json.dumps(facts or {}), err, run_id))
        ok = sum(1 for v in results.values() if v[2] is not None)
        counts = dict(probed=len(results), ok=ok, failed=sorted(h for h, v in results.items() if v[2] is None))
        cur.execute("update pan.run set finished_at = now(), status = %s, counts = %s where run_id = %s",
                    ("OK" if ok == len(results) else "PARTIAL", json.dumps(counts), run_id))
    for h, (method, addr, facts, err) in sorted(results.items()):
        out("{:<16} {:<6} {}".format(h, method, "ok: {} threads, {} GiB, {}".format(
            facts.get("threads"), round((facts.get("mem_total_kb") or 0) / 1048576, 1), facts.get("os"))
            if facts else "FAILED: " + err))
    return results


# ---------------------------------------------------------------- machines

def _gpu_short(s):
    """lspci names -> short ones: 'Intel Corporation Kaby Lake-U GT2 [HD Graphics 620] (rev 02)' -> 'Intel HD
    Graphics 620'; 'Intel Corporation Haswell-ULT Integrated Graphics Controller' -> 'Intel Haswell-ULT integrated'."""
    out = []
    for g in (s or "").split(";"):
        g = re.sub(r"\s*\(rev [0-9a-f]+\)", "", g).replace(" Corporation", "").strip()
        b = re.search(r"\[([^\]]+)\]", g)
        if b:
            g = "{} {}".format(g.split()[0], b.group(1))
        g = re.sub(r"\s*Integrated Graphics Controller", " integrated", g)
        if g:
            out.append(g)
    return "; ".join(out)


def merge(m, facts, measured_at, method):
    """Overlay measured facts on a register row; returns the row with `specs`, `checked_at` and `mismatch`."""
    m = dict(m)
    miss = []
    if not facts:
        m.update(specs="register only", checked_at=None, mismatch="")
        return m
    hn = (facts.get("hostname") or "").upper()
    if hn and hn != m["host"]:
        miss.append("answers as {} at {}".format(hn, m["ip"]))
    if facts.get("threads") and m.get("threads") and facts["threads"] != m["threads"]:
        miss.append("register {} threads, measured {}".format(m["threads"], facts["threads"]))
    gib = round(facts["mem_total_kb"] / 1048576, 1) if facts.get("mem_total_kb") else None
    if gib and m.get("ram_gb") and (gib < 0.85 * m["ram_gb"] or gib > m["ram_gb"] + 1):
        miss.append("register {:g} GB RAM, measured {:g} GiB".format(m["ram_gb"], gib))
    if facts.get("os_ambiguous"):
        m["os"] = m["os"] or facts["os_ambiguous"]
    elif facts.get("os"):
        m["os"] = re.sub(r"^Microsoft\s+", "", facts["os"])
        if facts.get("kernel") and m["family"] == "Linux":
            m["os"] += " (kernel {})".format(facts["kernel"])
    if facts.get("cpu_model"):
        m["cpu"] = re.sub(r"\s+", " ", re.sub(r"\((R|TM)\)|CPU|\d+(th|st|nd|rd) Gen|Processor", "",
                                              facts["cpu_model"])).replace(" @ ", ", ").strip()
    for k in ("cores", "threads"):
        if facts.get(k):
            m[k] = facts[k]
    if gib:
        m["ram_gb"] = gib
    nv = facts.get("nvidia") or []
    if nv:
        m["gpu"] = "; ".join(g["name"].replace("NVIDIA GeForce ", "") for g in nv)
        m["vram_gb"] = round(sum(g["vram_mb"] for g in nv) / 1024, 1)
    elif facts.get("gpu") and m["family"] == "Linux":
        m["gpu"] = _gpu_short(facts["gpu"])
    elif facts.get("gpu_name"):
        m["gpu"] = facts["gpu_name"].replace("NVIDIA GeForce ", "")
        if facts.get("gpu_vram_total_mb"):
            m["vram_gb"] = round(facts["gpu_vram_total_mb"] / 1024, 1)
    pdisks = facts.get("physical_disks") or []
    if pdisks:
        m["disk_total_gb"] = round(sum(d["size"] for d in pdisks) / 1e9)
        m["disk"] = " + ".join("{} {}".format(_size(d["size"]), d.get("media") if d.get("media") in ("HDD", "SSD", "SCM")
                                         else "(type not reported)") for d in pdisks)
    vols = facts.get("volumes") or []
    if vols:
        m["free_gb"] = round(sum(v["free"] for v in vols) / 1e9)
        m["free_where"] = ", ".join("{} {} free".format(v["drive"], _size(v["free"])) for v in vols)
    elif facts.get("prom_disk_free_gb") is not None:
        m["free_gb"] = round(facts["prom_disk_free_gb"])
        m["free_where"] = "{} {:,.0f} GB free".format(facts.get("prom_disk_mount") or "", facts["prom_disk_free_gb"])
    if facts.get("vendor") or facts.get("product_name"):
        prod = " ".join(x for x in (facts.get("product_version"), facts.get("product_name"))
                        if x and x.lower() not in ("none", "default string", "to be filled by o.e.m."))
        m["model_measured"] = "{} {}".format(facts.get("vendor") or "", prod).strip()
    m.update(specs="measured {} ({})".format(_iso(measured_at)[:10], method), checked_at=_iso(measured_at),
             mismatch="; ".join(miss))
    return m


def _size(b):
    return "{:,.0f} GB".format(b / 1e9) if b < 1e12 else "{:.1f} TB".format(b / 1e12)


def machines(now=None):
    """One row per register machine: register values, measured values over them, last seen, seats seen in 7 days."""
    from . import db
    now = now or dt.datetime.now(dt.timezone.utc)
    rows = register(git_show(DOC))
    with db.cursor() as cur:
        cur.execute("""select distinct on (host) host, probed_at, method, facts from pan.host_probe where ok
                       order by host, probed_at desc""")
        pan_p = {h: (t, meth, f) for h, t, meth, f in cur.fetchall()}
        cur.execute("""select distinct on (upper(hostname)) upper(hostname), taken_at, cpu_count_logical, mem_total_gb,
                              gpu_name, gpu_vram_total_mb, prom_disk_mount, prom_disk_free_gb, extras
                       from agora.machine_probes order by upper(hostname), taken_at desc""")
        agora = {}
        for h, t, thr, mem, gname, vram, mount, free, ex in cur.fetchall():
            ex = ex or {}
            # platform.release() says "10" on Windows 11 before Python 3.12, so the probe's "10" cannot tell them apart
            py = tuple(int(x) for x in re.findall(r"\d+", ex.get("python_version", "0.0"))[:2])
            rel = str(ex.get("platform_release", ""))
            osname = "{} {}".format(ex.get("platform", ""), rel).strip()
            amb = "Windows 10 or 11 (probe cannot tell)" if rel == "10" and py < (3, 12) else osname
            agora[h] = (t, dict(threads=thr, mem_total_kb=int(mem * 1048576) if mem else None, gpu_name=gname,
                                gpu_vram_total_mb=vram, prom_disk_mount=mount, prom_disk_free_gb=free,
                                os_ambiguous=amb))
        cur.execute("""select upper(machine), max(last_active_at),
                              array_agg(distinct agent order by agent) filter (where last_active_at > now() - interval '7 days')
                       from comms.agent_instances where machine is not null group by 1""")
        sessions = {h: (t, a or []) for h, t, a in cur.fetchall()}
        cur.execute("select upper(host), max(last_seen_at), count(*) from fabric.agent_instances group by 1")
        fabric = {h: (t, n) for h, t, n in cur.fetchall()}
    out = []
    for m in rows:
        h = m["host"]
        if h in pan_p:
            t, meth, f = pan_p[h]
            r = merge(m, f, t, "ssh" if meth == "ssh" else "local CIM")
        elif h in agora:
            t, f = agora[h]
            r = merge(m, f, t, "agora probe")
        else:
            r = merge(m, None, None, None)
        seen = [(sessions.get(h, (None,))[0], "seat session"), (fabric.get(h, (None,))[0], "Fabric worker"),
                (agora.get(h, (None,))[0], "agora probe"), (pan_p.get(h, (None,))[0], "Pan probe")]
        seen = [s for s in seen if s[0] is not None]
        last, by = max(seen) if seen else (None, "")
        seats7 = sessions.get(h, (None, []))[1]
        r.update(last_seen=_iso(last), seen_by=by, status=bucket(last, now), seats_7d=", ".join(seats7),
                 n_seats_7d=len(seats7), fabric_workers=fabric.get(h, (None, 0))[1],
                 cuda=bool(re.search(r"RTX|GTX|Quadro|NVIDIA", r.get("gpu") or "")))
        for k in ("disk_total_gb", "free_gb", "free_where", "model_measured"):
            r.setdefault(k, None)
        r["os"] = r["os"] or "{} (edition not recorded)".format(r["family"])
        r["gpu"] = r["gpu"] or "not recorded"
        out.append(r)
    return out


# ---------------------------------------------------------------- seats

def _work_state(seat):
    try:
        return json.loads(git_show("roles/{}/WORK_STATE.json".format(seat)))
    except (RuntimeError, ValueError):
        return None


def _subject(s):
    return re.sub(r"^[A-Za-z][\w-]*(\[[^\]]*\])?:\s*", "", s or "")[:160]


def seats(now=None):
    """One row per seat: comms registrations and role directories, minus role templates and the census's
    historical role documents."""
    from . import db
    now = now or dt.datetime.now(dt.timezone.utc)
    census = json.loads(git_show(CENSUS))
    cs = census.get("seats", {})
    tree = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only", "HEAD", "roles/"],
                          capture_output=True, text=True).stdout.split()
    dirs = {p.split("/")[1] for p in tree if p.count("/") >= 2}
    has_ws = {p.split("/")[1] for p in tree if p.endswith("/WORK_STATE.json") and p.count("/") == 2}
    with db.cursor() as cur:
        cur.execute("select agent, last_active_at, last_sync_at, machine, model, tier from comms.agents")
        ag = {r[0]: r[1:] for r in cur.fetchall()}
        cur.execute("""select distinct on (agent) agent, machine, last_active_at from comms.agent_instances
                       where last_active_at is not null and machine is not null order by agent, last_active_at desc""")
        last_inst = {a: (m, t) for a, m, t in cur.fetchall()}
        cur.execute("""select agent, max(last_sync_at), max(last_active_at),
                              array_agg(distinct machine) filter (where machine is not null)
                       from comms.agent_instances group by agent""")
        inst = {a: (s, t, ms or []) for a, s, t, ms in cur.fetchall()}
        cur.execute("""select distinct on (seat) seat, committed_at, subject, sha from pan.commit
                       where seat is not null order by seat, committed_at desc""")
        commit = {s: (t, subj, sha) for s, t, subj, sha in cur.fetchall()}
        cur.execute("""select seat, count(*) from pan.commit where seat is not null
                       and committed_at > now() - interval '7 days' group by seat""")
        c7 = dict(cur.fetchall())
        cur.execute("""select distinct on (sender) sender, created_at, subject from comms.messages
                       order by sender, created_at desc""")
        msg = {s: (t, subj) for s, t, subj in cur.fetchall()}
        cur.execute("select max(committed_at) from pan.commit")
        commits_to = cur.fetchone()[0]
    names = (set(ag) | dirs) - NOT_SEATS
    names = {n for n in names if n in ag or cs.get(n, {}).get("kind") != "HISTORICAL_ROLE_DOC"}
    out = []
    for s in sorted(names, key=str.lower):
        a_last, a_sync, a_machine, model, tier = ag.get(s, (None,) * 5)
        i_sync, i_last, machines_ = inst.get(s, (None, None, []))
        c_t, c_subj, c_sha = commit.get(s, (None, "", ""))
        m_t, m_subj = msg.get(s, (None, ""))
        checkin = max([t for t in (a_sync, i_sync) if t] or [None])
        acts = [(t, k) for t, k in ((a_last, "comms"), (i_last, "comms"), (c_t, "commit"), (m_t, "message")) if t]
        last, via = max(acts) if acts else (None, "")
        lm = last_inst.get(s, (a_machine, None))[0] or a_machine
        ws = _work_state(s) if s in has_ws else None
        c = cs.get(s, {})
        declared = (ws or {}).get("state") or ""
        declared_at = ((ws or {}).get("updated_at_utc") or "")[:10]
        focus = (ws or {}).get("current_objective") or ""
        focus = re.split(r"(?<=[.;])\s", focus, 1)[0][:160] if focus else ""
        out.append(dict(
            seat=s, status=bucket(last, now) if s in ag or acts else "never",
            last_active=_iso(last), last_active_via=via, last_checkin=_iso(checkin),
            last_commit_at=_iso(c_t), last_commit=_subject(c_subj), last_commit_sha=(c_sha or "")[:9],
            commits_7d=int(c7.get(s, 0)), last_message_at=_iso(m_t), last_message=(m_subj or "")[:160],
            last_machine=(lm or "").upper(), machines=", ".join(sorted({x.upper() for x in machines_})),
            model=model or "", tier=tier or "", declared=declared, declared_at=declared_at, focus=focus,
            role=(c.get("short_role") or "")[:160], census_kind=c.get("kind") or "",
            on_comms=s in ag))
    meta = dict(census_generated_at=census.get("generated_at_utc"), commits_indexed_to=_iso(commits_to),
                head=head_sha()[:9], built_at=_iso(now))
    return out, meta


# ---------------------------------------------------------------- controls

def controls(write=True):
    """POSITIVE: the local host's measured threads and RAM agree with the register (M2: 28 threads, 32 GB) and at
    least one ssh probe succeeds. NEGATIVE: a probe of an unroutable TEST-NET address fails and is recorded as a
    failure; a register machine nobody probes is labelled 'register only'. CHEAT: a register row claiming 999
    threads for a measured host is flagged, not silently replaced; seats whose comms status column says 'active'
    but whose comms activity is over 24 h old must exist and none may be reported active on comms evidence."""
    from . import db
    now = dt.datetime.now(dt.timezone.utc)
    res = {}
    rows = machines(now)
    byh = {r["host"]: r for r in rows}
    loc = byh.get(host())
    res["POSITIVE_local_agrees"] = bool(loc and loc["specs"].startswith("measured") and not loc["mismatch"])
    res["POSITIVE_ssh_probe_ok"] = any(r["specs"].endswith("(ssh)") for r in rows)
    facts, err = _ssh_probe("192.0.2.1", timeout=20)
    res["NEGATIVE_unroutable_fails"] = facts is None and bool(err)
    reg = {m["host"]: m for m in register(git_show(DOC))}
    with db.cursor() as cur:
        cur.execute("select distinct host from pan.host_probe where ok")
        probed = {r[0] for r in cur.fetchall()}
        cur.execute("select distinct upper(hostname) from agora.machine_probes")
        probed |= {r[0] for r in cur.fetchall()}
        unprobed = sorted(h for h in byh if h not in probed)
        res["NEGATIVE_unprobed_register_only"] = dict(
            hosts=unprobed, all_labelled=bool(unprobed) and all(byh[h]["specs"] == "register only" for h in unprobed))
        cur.execute("""select distinct on (host) host, probed_at, facts from pan.host_probe where ok and method = 'ssh'
                       order by host, probed_at desc limit 1""")
        one = cur.fetchone()
        cur.execute("""select agent from comms.agents where status = 'active'
                       and coalesce(last_active_at, 'epoch') < now() - interval '24 hours'""")
        stale_active = {r[0] for r in cur.fetchall()}
    if one:
        fake = dict(reg[one[0]], threads=999)
        res["CHEAT_register_lie_flagged"] = "999" in merge(fake, one[2], one[1], "ssh")["mismatch"]
    st, _ = seats(now)
    res["POSITIVE_pan_active_here"] = any(r["seat"] == "Pan" and r["status"] == "active" for r in st)
    res["CHEAT_status_column_ignored"] = dict(
        comms_rows_saying_active_but_idle_24h=len(stale_active),
        reported_active_among_them=sum(1 for r in st if r["seat"] in stale_active and r["status"] == "active"
                                       and r["last_active_via"] == "comms"))
    res["NEGATIVE_never_on_comms"] = sorted(r["seat"] for r in st if not r["on_comms"])
    passed = (res["POSITIVE_local_agrees"] and res["POSITIVE_ssh_probe_ok"] and res["NEGATIVE_unroutable_fails"]
              and res["NEGATIVE_unprobed_register_only"]["all_labelled"] and res.get("CHEAT_register_lie_flagged", False)
              and res["POSITIVE_pan_active_here"]
              and res["CHEAT_status_column_ignored"]["comms_rows_saying_active_but_idle_24h"] > 0
              and res["CHEAT_status_column_ignored"]["reported_active_among_them"] == 0)
    out = dict(kind="fleet-controls", at=_iso(now), head=head_sha()[:9], passed=passed, results=res,
               mismatches={r["host"]: r["mismatch"] for r in rows if r["mismatch"]})
    if write:
        path = REPO / "roles" / "Pan" / "reports" / "controls" / "FLEET_{}.json".format(now.strftime("%Y%m%dT%H%M%SZ"))
        path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
        out["path"] = str(path)
    print(json.dumps(out, indent=1, default=str))
    return out
