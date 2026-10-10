"""PAN-38 fleet: register parsing, probe parsing, the measured-over-register merge, status buckets. No database."""
import datetime as dt

from pan import fleet

DOC = """# Fleet hosts

## Windows machines (2)

| Host (label) | Hardware | CPU | RAM | GPU | Disk | IP | Role / tags | Notes |
|---|---|---|---|---|---|---|---|---|
| SKULLPORT (M1) | desktop | Ryzen 7 7700X, 8C/16T | 32 GB | RTX 5060 Ti 16 GB | 2x 1 TB NVMe | .202 | `heavy.cpu` `gpu` | Postgres. Win 11 Home. |
| ELSA | Dell Optiplex 980 | i7-860, 4C/8T (no AVX) | 16 GB DDR3-1333 (4x 4 GB) | Radeon HD 5450 | 240 GB SATA SSD | .163 | `light` | Achilles' seat. |

## Linux nodes (1)

All Ubuntu Server 26.04.1, kernel 7.0.0-38, user `jcraig`.

| Sticker label | Host | Hardware | CPU | RAM | Disk | Net | Role / tags | State (2026-10-02) |
|---|---|---|---|---|---|---|---|---|
| ThinkPad P52s | ubu005 | ThinkPad P52s | i5-8350U, 4C/8T | 22 GB | 1 TB NVMe | Ethernet .222 (Wi-Fi .227) | `light` | Worker active |

## Candidates

| Machine | Expected | Verdict |
|---|---|---|
| basement | i7 | maybe |
"""

KV = """hostname=ubu005
vendor=LENOVO
product_name=20LB0010US
product_version=ThinkPad P52s
os=Ubuntu 26.04.1 LTS
kernel=7.0.0-38-generic
uptime_s=12345
cpu_model=Intel(R) Core(TM) i5-8350U CPU @ 1.70GHz
threads=8
cores=4
mem_total_kb=23000000
mem_avail_kb=20000000
disks={"blockdevices":[{"name":"sda","size":1000204886016,"rota":false,"type":"disk","model":"MP33"},{"name":"loop0","size":4096,"rota":false,"type":"loop","model":null}]}
root=983000000000 900000000000
gpu=Intel Corporation UHD Graphics 620 (rev 07)
load=0.10 0.20 0.30
"""


def test_register_parses_both_tables_and_skips_candidates():
    rows = {r["host"]: r for r in fleet.register(DOC)}
    assert set(rows) == {"SKULLPORT", "ELSA", "UBU005"}
    m1 = rows["SKULLPORT"]
    assert (m1["label"], m1["cores"], m1["threads"], m1["ram_gb"], m1["vram_gb"]) == ("M1", 8, 16, 32.0, 16.0)
    assert m1["os"] == "Windows 11 Home" and m1["ip"] == "192.168.1.202" and m1["tags"] == "heavy.cpu gpu"
    assert rows["ELSA"]["os"] == "" and rows["ELSA"]["ram_gb"] == 16.0
    u = rows["UBU005"]
    assert u["ip"] == "192.168.1.222" and u["os"].startswith("Ubuntu Server 26.04.1") and u["threads"] == 8


def test_probe_output_parses_and_drops_loop_devices():
    f = fleet.parse_kv(KV)
    assert f["threads"] == 8 and f["cores"] == 4 and f["mem_total_kb"] == 23000000
    assert [d["model"] for d in f["physical_disks"]] == ["MP33"]
    assert f["volumes"] == [dict(drive="/", size=983000000000, free=900000000000)]


def test_merge_measured_replaces_register_and_agreement_is_quiet():
    reg = {r["host"]: r for r in fleet.register(DOC)}["UBU005"]
    t = dt.datetime(2026, 10, 10, 12, tzinfo=dt.timezone.utc)
    m = fleet.merge(reg, fleet.parse_kv(KV), t, "ssh")
    assert m["mismatch"] == "" and m["specs"] == "measured 2026-10-10 (ssh)"
    assert m["ram_gb"] == 21.9 and m["gpu"] == "Intel UHD Graphics 620" and m["free_gb"] == 900
    assert "kernel 7.0.0-38-generic" in m["os"]


def test_merge_flags_every_disagreement():
    reg = {r["host"]: r for r in fleet.register(DOC)}["UBU005"]
    f = fleet.parse_kv(KV.replace("threads=8", "threads=4").replace("hostname=ubu005", "hostname=ubu006")
                       .replace("mem_total_kb=23000000", "mem_total_kb=7300000"))
    miss = fleet.merge(reg, f, dt.datetime.now(dt.timezone.utc), "ssh")["mismatch"]
    assert "UBU006" in miss and "8 threads, measured 4" in miss and "22 GB RAM" in miss


def test_unprobed_is_register_only():
    reg = fleet.register(DOC)[1]
    m = fleet.merge(reg, None, None, None)
    assert m["specs"] == "register only" and m["checked_at"] is None and m["ram_gb"] == 16.0


def test_status_buckets():
    now = dt.datetime(2026, 10, 10, 12, tzinfo=dt.timezone.utc)
    h = lambda x: now - dt.timedelta(hours=x)
    assert [fleet.bucket(h(x), now) for x in (1, 30, 200, 800)] == ["active", "week", "month", "inactive"]
    assert fleet.bucket(None, now) == "none"
