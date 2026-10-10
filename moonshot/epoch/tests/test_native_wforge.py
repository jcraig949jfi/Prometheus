"""C-012-T007: the native wforge epoch runtime (moonshot.native.wforge v1), written RED before the runtime.

A native epoch advances a wforge Encounter (design v0.3 s8: primary substrate) by ticks_per_epoch ticks under a fixed
deterministic policy. The load-bearing property is CHECKPOINT CONFORMANCE: k chained epochs, each restoring the world
from the previous checkpoint, must equal one monolithic run of the same world -- tick for tick, byte for byte -- or a
chain silently diverges from the world it claims to run (R-RUNTIME)."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

from moonshot.epoch import canonical as C
from moonshot.epoch import model
from moonshot.epoch import native_wforge as NW

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "SerendipityFoundry" / "worldfoundry"))
from wforge import GRAMMAR_VERSION  # noqa: E402
from wforge.genome import de_novo  # noqa: E402
from wforge.world import Encounter, expand  # noqa: E402

APPROVED = "c0de" * 10


def params(seed=7, ticks=5, episode_seed=3, policy_seed=11):
    return NW.genesis_params(de_novo(GRAMMAR_VERSION, seed), episode_seed=episode_seed, ticks_per_epoch=ticks,
                             policy_seed=policy_seed)


def genesis(p, epochs, cid="N1"):
    return model.make_genesis(cid, epochs=epochs, params=p, approved_code_sha=APPROVED,
                              initial_checkpoint=NW.initial_checkpoint(p), runtime=NW.NATIVE_WFORGE_V1)


def chained(p, epochs):
    g = genesis(p, epochs)
    inp, out = g.initial_checkpoint, []
    for k in range(1, epochs + 1):
        r = model.execute(g.obj, k, inp)
        out.append(r)
        inp = r.checkpoint
    return g, out


def monolithic(p, ticks):
    """The same world and policy in ONE Encounter, no checkpoints: the reference."""
    g = NW.genome_from(p["genome"])
    mech = expand(g)
    enc = Encounter(mech, p["world_id"], p["episode_seed"])
    lines = []
    for _ in range(ticks):
        if enc.tick >= mech.horizon or not any(enc.alive):
            break
        enc.step(NW.policy_actions(p, mech, enc))
        lines.append(NW.trace_line(enc))
    return enc, b"".join(lines)


class TestConformance(unittest.TestCase):
    def test_chained_epochs_equal_one_monolithic_run(self):
        p = params(ticks=5)
        g, rs = chained(p, 6)                                            # 30 ticks in 6 epochs
        enc, trace = monolithic(p, 30)
        self.assertEqual(b"".join(r.trace for r in rs), trace)
        self.assertEqual(NW.state_of(C.parse_canonical(rs[-1].checkpoint)), NW.state_of(NW.capture(enc)))

    def test_epoch_boundaries_do_not_matter(self):
        finals = set()
        for ticks, epochs in ((1, 24), (3, 8), (8, 3), (24, 1)):
            _, rs = chained(params(ticks=ticks), epochs)
            finals.add((b"".join(r.trace for r in rs), rs[-1].checkpoint))
        self.assertEqual(len({f[0] for f in finals}), 1, "the trace depends on where epochs cut")
        self.assertEqual(len({NW.state_of(C.parse_canonical(f[1])) for f in finals}), 1)

    def test_several_worlds_conform(self):
        for seed in (1, 2, 3, 5, 8, 13):
            with self.subTest(world_seed=seed):
                p = params(seed=seed, ticks=4)
                _, rs = chained(p, 5)
                enc, trace = monolithic(p, 20)
                self.assertEqual(b"".join(r.trace for r in rs), trace)

    def test_checkpoint_is_canonical_and_round_trips(self):
        p = params()
        ck = NW.initial_checkpoint(p)
        self.assertEqual(C.canonical_bytes(C.parse_canonical(ck)), ck)
        _, rs = chained(p, 2)
        restored = NW.restore(p, rs[-1].checkpoint)
        self.assertEqual(C.canonical_bytes(NW.capture(restored)), rs[-1].checkpoint)

    def test_the_policy_never_takes_an_unaffordable_action(self):
        # F09: an unaffordable action queues unpaid writes in wforge as it is. This policy must never issue one, so the
        # native epoch's physics does not depend on that defect.
        for seed in (1, 2, 3, 5, 8, 13, 21):
            p = params(seed=seed)
            mech = expand(NW.genome_from(p["genome"]))
            enc = Encounter(mech, p["world_id"], p["episode_seed"])
            for _ in range(mech.horizon):
                acts = NW.policy_actions(p, mech, enc)
                for s in range(mech.n_slots):
                    if enc.alive[s]:
                        cost = sum(x % 8 for x in acts[s]) * mech.act_cost
                        self.assertLessEqual(cost, enc.charge[s], (seed, enc.tick, s))
                if enc.step(acts):
                    break

    def test_a_finished_world_stays_finished(self):
        p = params(ticks=50)
        mech = expand(NW.genome_from(p["genome"]))
        epochs = mech.horizon // 50 + 3                                   # past the horizon
        _, rs = chained(p, epochs)
        self.assertEqual(rs[-1].trace, b"")
        self.assertEqual(rs[-1].checkpoint, rs[-2].checkpoint)


class TestIdentityAndRefusals(unittest.TestCase):
    def test_epochs_are_ordinary_verified_r_ep_epochs(self):
        p = params()
        g, rs = chained(p, 3)
        inp = g.initial_checkpoint
        for r in rs:
            self.assertEqual(model.verify_epoch(r.files(), C.sha256_hex(inp)), [])
            inp = r.checkpoint
        self.assertEqual(g.obj["runtime"], {"name": "moonshot.native.wforge", "version": 1})

    def test_the_spec_names_the_wforge_implementation(self):
        p = params()
        self.assertEqual(p["wforge_world_sha256"], NW.world_sha256())
        self.assertEqual(len(p["wforge_world_sha256"]), 64)

    def test_a_different_wforge_is_refused(self):
        p = dict(params(), wforge_world_sha256="0" * 64)
        g = genesis(p, 1)
        with self.assertRaises(ValueError):
            model.execute(g.obj, 1, g.initial_checkpoint)

    def test_a_checkpoint_for_another_world_is_refused(self):
        a, b = params(seed=1), params(seed=2)
        g = genesis(a, 1)
        with self.assertRaises(ValueError):
            model.execute(g.obj, 1, NW.initial_checkpoint(b))

    def test_determinism_across_processes(self):
        p = params()
        g, rs = chained(p, 2)
        code = ("import sys, json; sys.path.insert(0, {r!r}); from moonshot.epoch import model, canonical as C\n"
                "g = C.parse_canonical(bytes.fromhex(sys.argv[1])); r = model.execute(g, 2, bytes.fromhex(sys.argv[2]))\n"
                "print(r.epoch_digest)").format(r=str(REPO))
        env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")}
        out = subprocess.run([sys.executable, "-E", "-s", "-c", code, g.bytes.hex(), rs[0].checkpoint.hex()],
                             capture_output=True, text=True, cwd=str(REPO), env=env, timeout=120)
        self.assertEqual(out.stdout.strip(), rs[1].epoch_digest, out.stderr[-600:])


if __name__ == "__main__":
    unittest.main()
