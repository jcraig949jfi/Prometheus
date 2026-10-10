"""BEL-RD-72 E1 instrument (light): long-horizon half-capability census on the PLAIN World (no per-birth hooks).

Every `census_every` ticks each distinct living tape is classified LO / HI / BOTH / NONE (halves.HalvesWorld.halves
semantics, same fixed panels) and FUNC; the census keeps the counts and the most common LO, HI and BOTH tapes (hex).
The first census at which a BOTH and FUNC tape is alive is recorded with that tape. Because the world is deterministic,
any run with a BOTH event can be REPLAYED under the full HalvesWorld (byte tags) to obtain the temporal depth of the
composite's critical bytes; the light run itself makes no lineage claim."""
from __future__ import annotations

from collections import Counter

from belinst import Func
from halves import HI_PANEL, LO_PANEL, _expected
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World


class LightHalvesWorld(World):
    def __init__(self, cfg, seed, census_every: int = 250):
        super().__init__(cfg, seed)
        self.census_every = census_every
        self.func = Func(cfg)
        self._hc = {}
        self.census = []
        self.first_both = None

    def halves(self, tape: bytes) -> str:
        r = self._hc.get(tape)
        if r is not None:
            return r
        L = self.L; cfg = self.cfg
        def ok(x):
            mem = bytearray(256); mem[:L] = tape; mem[vm.IN_BASE] = x
            tr = vm.execute(mem, L, 0, cfg.budget, [x], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
            return bool(tr.outputs) and tr.outputs[0] == _expected(cfg.task, x)
        lo = all(ok(x) for x in LO_PANEL); hi = all(ok(x) for x in HI_PANEL)
        r = "BOTH" if lo and hi else ("LO" if lo else ("HI" if hi else "NONE"))
        if len(self._hc) < 300000:
            self._hc[tape] = r
        return r

    def step(self):
        rec = super().step()
        if self.tick % self.census_every == 0:
            c = Counter(); cf = Counter(); tapes = {"LO": Counter(), "HI": Counter(), "BOTH": Counter()}
            for o in self.cells:
                if o is None:
                    continue
                t = bytes(o.tape); h = self.halves(t); c[h] += 1
                fn = self.func(t)
                if fn:
                    cf[h] += 1
                if h in tapes and fn:
                    tapes[h][t] += 1
            top = {h: (tapes[h].most_common(1)[0][0].hex() if tapes[h] else None) for h in tapes}
            self.census.append({"tick": self.tick, "alive": sum(c.values()), "halves": dict(c), "halves_func": dict(cf), "top_func": top})
            if self.first_both is None and cf.get("BOTH"):
                self.first_both = {"tick": self.tick, "tape": top["BOTH"]}
        return rec
