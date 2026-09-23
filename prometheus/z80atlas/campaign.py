"""CLI for the Z80 x Atlas campaign.

  python -m prometheus.z80atlas.campaign --hours 72 --workdir <dir> [--workers N] [--ticks 200] [--cells 144] [--seed 0]
  python -m prometheus.z80atlas.campaign --resume --workdir <dir>          # continue a checkpointed campaign in its original window
  python -m prometheus.z80atlas.campaign --status --workdir <dir>          # print progress from state.json
  python -m prometheus.z80atlas.campaign --finalize --workdir <dir>        # emit the packet from the last checkpoint (after an early stop)

No HITL, no LLM: once started the campaign runs from the frozen grammar until its wall-clock boundary, then stops
cleanly, freezes state and emits CAMPAIGN_PACKET.md."""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import pathlib

from prometheus.z80atlas.scheduler import Campaign


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--hours", type=float, default=72.0)
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument("--cells", type=int, default=144)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--finalize", action="store_true", help="emit the packet from the last checkpoint without running (after an early stop)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.status:
        st = json.loads((pathlib.Path(a.workdir) / "state.json").read_text(encoding="utf-8"))
        fams = st["families"]
        print(json.dumps({"start": st["start_utc"], "stopped": st["stopped"], "hours": st["hours"], "runs": st.get("n_runs", 0), "families": len(fams),
                          "promoted": sum(1 for f in fams.values() if f["promoted"]), "retired": sum(1 for f in fams.values() if f["retired"]),
                          "counters": st["counters"], "positive_controls": (st.get("positive_controls") or {}).get("all_passed"),
                          "flags": len(st.get("flags") or []), "last_decision": (st["decisions"] or [{}])[-1]}, indent=1))
        return 0
    if a.finalize:
        c = Campaign(a.workdir, a.hours, 1, resume=True)
        c._decide("finalize", None, "packet emitted from checkpoint at %d runs (early stop)" % len(c.runs))
        c.finalize()
        print(json.dumps({"finalized": c.s["stopped"], "runs": len(c.runs), "packet": str(c.wd / "CAMPAIGN_PACKET.md")}))
        return 0
    c = Campaign(a.workdir, a.hours, a.workers, ticks=a.ticks, cells=a.cells, seed=a.seed, resume=a.resume)
    c.run(quiet=a.quiet)
    print(json.dumps({"stopped": c.s["stopped"], "runs": len(c.runs), "families": len(c.s["families"]), "packet": str(c.wd / "CAMPAIGN_PACKET.md")}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
