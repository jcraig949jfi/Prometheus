import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
class Stop(Exception): pass
SEED, E = int(sys.argv[1]), int(sys.argv[2]); TG = [int(x) for x in sys.argv[3].split(",")]
class R(world.Runner):
    def step(self):
        super().step()
        if self.epoch in (E - 6, E - 3, E):
            for o in self.orgs:
                if o.alive and o.oid in TG:
                    g = self._genome(o)
                    best = max((sum(g[(i + s) % 64] == imp[i] for i in range(64)), s) for s in range(64))
                    print(self.epoch, o.oid, g.hex(), "best rot match", best)
        if self.epoch >= E: raise Stop
r = R(dict(arm["cell"], atlas_axis="NONE"), SEED, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
print("imp", imp.hex())
try: r.run()
except Stop: pass
