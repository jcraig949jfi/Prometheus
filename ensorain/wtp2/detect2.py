"""WTP-02 detectors D1-D9, each with its named null twin, and the status
logic (PREREG_WTP02 s4-s5). A 'unit' is one seed's quartet of lives:
{'real', 'shuffled', 'frozen', 'random'} run on the same seed."""
import numpy as np

NULL = {"D1": "shuffled", "D2": "shuffled", "D3": "shuffled", "D4": "frozen", "D5": "random", "D6": "frozen",
        "D7": "shuffled", "D8": "shuffled", "D9": "shuffled"}
RATIO_DETS = ("D1", "D3", "D7", "D8", "D9")
DETS = tuple(NULL)


def _ok(r):
    return r is not None and r.get("status") == "OK"


def _cgu_trace(r):
    return [t["ACu"] - t["ACu0"] for t in r.get("trace", []) if t.get("ACu") is not None and np.isfinite(t["ACu"])]


def jump(r):
    s = _cgu_trace(r)
    if len(s) < 4:
        return 0.0, False
    inc = np.diff(s)
    j = float(inc.max())
    return j, bool(j >= 0.30 and j >= 5 * (np.median(np.abs(inc)) + 1e-9))


def reorg(r):
    tr = r.get("trace", [])
    end = r.get("CGu")
    if not tr or end is None or not np.isfinite(end):
        return 0.0, False
    best = 0.0
    for a, b in zip(tr, tr[1:]):
        ev = (a.get("kind") != b.get("kind")) or \
             (a.get("rank") is not None and b.get("rank") is not None and abs(b["rank"] - a["rank"]) >= 2) or \
             (a.get("sparsity") is not None and b.get("sparsity") is not None and abs(b["sparsity"] - a["sparsity"]) >= 0.2)
        if ev and b.get("ACu") is not None and np.isfinite(b["ACu"]):
            rise = end - (b["ACu"] - b["ACu0"])
            best = max(best, rise)
    return float(best), bool(best >= 0.10)


def stat(det, r, u, refs):
    """(statistic, fires) of detector `det` for life r inside unit u (u supplies the frozen/random baselines)."""
    if not _ok(r):
        return float("nan"), False
    cgu = r.get("CGu")
    cgu = cgu if cgu is not None and np.isfinite(cgu) else float("nan")
    fz = u.get("frozen")
    if det == "D1":
        return cgu, bool(np.isfinite(cgu) and cgu >= 0.10)
    if det == "D2":
        return jump(r)
    if det == "D3":
        c = cgu / max(r["n_floats"], 1) if np.isfinite(cgu) else float("nan")
        return c, bool(np.isfinite(c) and c >= refs["D3_top1"] and cgu >= 0.05)
    if det == "D4":
        return r["CG"], bool(r["CG"] <= -1)
    if det == "D5":
        ug = r["U"] - fz["U"] if _ok(fz) else float("nan")
        f = (np.isfinite(ug) and ug >= refs["UG_top5"] and r["CG"] <= 0) or \
            (np.isfinite(cgu) and cgu >= 0.10 and np.isfinite(ug) and ug <= 0)
        return ug, bool(f)
    if det == "D6":
        base = u.get("random") if r is fz else fz
        if not _ok(base):
            return float("nan"), False
        ratio = r["steps"] / max(base["steps"], 1)
        return ratio, bool(ratio >= 1.5 and r["alive"] != base["alive"])
    if det == "D7":
        return reorg(r)
    if det == "D8":
        rg = r.get("RG", float("nan"))
        return rg, bool(np.isfinite(rg) and rg >= 0.10)
    if det == "D9":
        return r["CA"], bool(r["CA"] >= 3 and np.isfinite(cgu) and cgu >= 0.05)
    raise KeyError(det)


def fires(det, u, refs):
    return stat(det, u["real"], u, refs)


def null_fires(det, u, refs):
    return stat(det, u.get(NULL[det]), u, refs)


def refs_from(units):
    reals = [u["real"] for u in units if _ok(u["real"]) and _ok(u.get("frozen"))]
    comp = [u["real"]["CGu"] / max(u["real"]["n_floats"], 1) for u in units
            if _ok(u["real"]) and u["real"].get("CGu") is not None and np.isfinite(u["real"]["CGu"])]
    ug = [u["real"]["U"] - u["frozen"]["U"] for u in units if _ok(u["real"]) and _ok(u.get("frozen"))]
    return dict(D3_top1=float(np.quantile(comp, 0.99)) if comp else 1e9,
                UG_top5=float(np.quantile(ug, 0.95)) if ug else 1e9, n=len(reals))


def status(det, units, refs):
    """Wave-B status from 5 replicate units (PREREG s5)."""
    n = len(units)
    deg = sum(u["real"].get("status") == "DEGENERATE" for u in units)
    if deg >= 3:
        return "DEGENERATE WORLD", {}
    real = [fires(det, u, refs) for u in units]
    null = [null_fires(det, u, refs) for u in units]
    hits = sum(f for _, f in real)
    nhits = sum(f for _, f in null)
    sd = [a - b for (a, _), (b, _) in zip(real, null) if np.isfinite(a) and np.isfinite(b)]
    med_sd = float(np.median(sd)) if sd else float("nan")
    med_stat = float(np.nanmedian([a for a, _ in real])) if any(np.isfinite(a) for a, _ in real) else float("nan")
    info = dict(hits=hits, null_hits=nhits, n=n, median_SD=med_sd, median_stat=med_stat, degenerate=deg,
                real=[a for a, _ in real], null=[b for b, _ in null])
    firing = [u for u, (_, f) in zip(units, real) if f]
    if any(u["real"].get("status") == "DEGENERATE" or u["real"].get("AC", 0) in (6.0, -3.0) for u in firing):
        return "METRIC ARTEFACT", info
    if hits <= 1:
        return "FALSIFIED", info
    if hits == 2:
        return "UNRESOLVED", info
    if det in ("D4", "D6") and nhits >= 3:
        return "MECHANICAL", info
    if nhits >= 3:
        return "STRUCTURE-INDEPENDENT", info
    ratio_ok = det not in RATIO_DETS or (np.isfinite(med_stat) and med_sd >= 0.5 * med_stat)
    if nhits <= 1 and np.isfinite(med_sd) and med_sd >= 0.10 and ratio_ok:
        return "STRUCTURE-DEPENDENT", info
    return "UNRESOLVED", info
