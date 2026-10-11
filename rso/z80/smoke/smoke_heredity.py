"""C-016-T021 known-answer smoke test: Z80 Atlas (archaeon/z80atlas) byte-level heredity. Read-only against that lane.

Command (repo root, one process, seconds; every RNG is a SplitMix64 with a seed fixed below):
    python -m rso.z80.smoke.smoke_heredity rso/z80/smoke/smoke_result.json
Exit 0 only if every known answer holds.

Generation boundary used (archaeon/z80atlas/engine.py:317-338, ENDOGENOUS_COPY branch of run()): a parent is executed with its
neighbour window; if >= copy_min_frac (0.9) of the G window bytes were WRITTEN BY THE PARENT'S OWN EXECUTION, the child
tape is that window (plus copy noise). Nothing is copied by the runner. The smoke test replays exactly that at VM level,
without the population loop, then asks whether the child still has the parent's FUNCTION (task ECHO_forced) and whether
the child can itself reproduce (next generation).
Known answers:
  H         planted heritable program (tasks.task_then_replicate): child written, function present, child reproduces
  NH        same function, no replicator (tasks.WITNESS): no child
  CON       constructor writing a 3-byte function into the window: window fraction < 0.9, no ENDOGENOUS_COPY birth
  ENV       function lives in the neighbour (JP 128), parent writes nothing: no child; competence collapses with a
            zeroed neighbour; donor_contributes() is True
  H_broken  heritable program with its copy-loop offset corrupted: the detector must say NOT heritable (sensitivity)
  engine    seeded vs random-only engine.run: provenance separates inserted ancestry from clean ancestry
"""
import hashlib
import json
import sys

from proteus.foundry.prng import SplitMix64
from archaeon.z80atlas import vm, tasks as T, grammar as GR
from archaeon.z80atlas import engine as E
from archaeon.z80atlas.grammar import FROZEN

G = 32
STEP_CAP = 256
TASK = "ECHO_forced"
I = vm.I


def pad(b):
    return T.pad(b, G)


def heritable(copy_prim=True):
    return pad(T.task_then_replicate(TASK, copy_prim))


def nonheritable():
    return pad(T.WITNESS[TASK])


def constructor():
    """Writes IN A / OUT A / HALT into window bytes 0..2 with LD A,imm ; LD (imm),A, then halts."""
    prog = []
    for k, byte in enumerate([I(21, 0), I(22, 0), I(23)]):
        prog += [I(1, 0), byte, I(19, 0, 1), 128 + k]
    return pad(prog + [I(23)])


def env_dependent():
    return pad([I(13), 128])               # JP 128: run whatever the neighbour window holds


def solves(tape, nbr, copy_prim, n=6):
    cs = T.cases(TASK, ("smoke", 1, 0), n, 0)
    sc = [T.score_case(TASK, vm.execute(tape, nbr, c, STEP_CAP, copy_prim, allow_nbr_write=False)["outputs"], c, {}) for c in cs]
    return sum(sc) / len(sc)


def generation(parent, nbr, copy_prim, noise_seed=None):
    """One parent->child boundary as the engine forms it under ENDOGENOUS_COPY."""
    case = T.cases(TASK, ("smoke", 1, 0), 1, 0)[0]
    res = vm.execute(parent, nbr, case, STEP_CAP, copy_prim)
    frac = sum(res["nbr_mask"]) / G
    born = frac >= FROZEN["copy_min_frac"] and res["writes_nbr"] > 0
    out = dict(writes_nbr=res["writes_nbr"], reads_nbr=res["reads_nbr"], exec_foreign=res["exec_foreign"], window_frac=round(frac, 4), born=bool(born),
               donor_contributes=E.donor_contributes(True, res, "ENDOGENOUS_COPY"))
    child = None
    if born:
        win = res["nbr_window"]
        child = E.copy_noise(win, res["nbr_mask"], SplitMix64(noise_seed), FROZEN["copy_noise"]) if noise_seed is not None else win
        out.update(child_sha=hashlib.sha256(child).hexdigest()[:16], parent_sha=hashlib.sha256(parent).hexdigest()[:16],
                   fidelity=round(E.fidelity(child, parent), 4), child_solves=round(solves(child, bytes(G), copy_prim), 3))
    return out, child


def lineage(parent, copy_prim, gens=3, noise_seed=None):
    """Heredity that sustains itself: does generation k+1 reproduce too?"""
    rows, cur = [], parent
    for g in range(gens):
        r, child = generation(cur, bytes(G), copy_prim, None if noise_seed is None else noise_seed + g)
        rows.append(r)
        if child is None:
            break
        cur = child
    return rows


def run_engine(init):
    spec = GR.make({"topology": "well_mixed", "migration": "none", "resources": "unlimited", "env_dynamics": "fixed", "reservoir": False, "niches": 1},
                   {"substrate": "vmcopy", "genome": G, "layout": "shared"}, "ENDOGENOUS_COPY", ["implicit_survival"], "none", "local_byte", init,
                   stage="early", reason="smoke")
    spec["population"]["N"] = 64
    spec["budget"].update(max_epochs=60, vm_steps=2_000_000)
    r = E.run(spec, 16_021_001)
    p = r["signals"]["provenance"]
    return dict(init=init, births_endo=r["signals"]["births_endo"], endo_clean=p["births_endo_clean"], endo_inserted=p["births_endo_inserted"],
                founders=p["founders"], spontaneous_replication=r["signals"]["spontaneous_replication"],
                inserted_lineage_replication=r["signals"]["inserted_lineage_replication"], max_gen_inserted=p["max_generation_inserted"])


def main(out):
    res, ok = {}, {}
    H, NH, CON, ENV = heritable(), nonheritable(), constructor(), env_dependent()
    res["H"] = lineage(H, True, 3, noise_seed=16_021_100)
    res["H_nonoise"] = lineage(H, True, 3)
    res["NH"] = lineage(NH, True, 3)
    res["CON"] = lineage(CON, True, 3)
    envnbr = pad(T.WITNESS[TASK])           # an ECHO program sitting in the neighbour window
    g_env, _ = generation(ENV, envnbr, True)
    g_env["solves_with_live_neighbour"] = round(solves(ENV, envnbr, True), 3)
    g_env["solves_with_zero_neighbour"] = round(solves(ENV, bytes(G), True), 3)
    res["ENV"] = g_env
    broken = bytearray(H)
    broken[bytes(H).index(bytes([0xFC]))] = 0x00        # the JNZ offset of the copy loop
    res["H_broken"] = lineage(bytes(broken), True, 2)
    res["engine_seeded"] = run_engine("seeded_replicator")
    res["engine_random"] = run_engine("random")
    h = res["H_nonoise"]
    ok["H_born_each_generation"] = len(h) == 3 and all(r["born"] for r in h)
    ok["H_function_transmitted"] = all(r["child_solves"] == 1.0 for r in h)
    ok["H_exact_copy_without_noise"] = all(r["fidelity"] == 1.0 for r in h)
    # with the frozen copy noise a byte can flip (seed 16_021_100 flips one byte in generation 3 and the function is lost: recorded, not
    # asserted away). The invariant: every child is born with fidelity >= 0.9, and an EXACT copy always carries the function.
    ok["H_noise_run_born_and_exact_copies_function_ok"] = (all(r["born"] and r["fidelity"] >= 0.9 for r in res["H"])
                                                           and all(r["child_solves"] == 1.0 for r in res["H"] if r["fidelity"] == 1.0))
    ok["H_no_donor_material"] = not any(r["donor_contributes"] for r in h)
    ok["NH_no_child"] = len(res["NH"]) == 1 and not res["NH"][0]["born"] and res["NH"][0]["writes_nbr"] == 0 and solves(NH, bytes(G), True) == 1.0
    ok["CON_refused_by_copy_min_frac"] = not res["CON"][0]["born"] and 0 < res["CON"][0]["window_frac"] < FROZEN["copy_min_frac"]
    ok["ENV_function_is_environmental"] = (not g_env["born"] and g_env["writes_nbr"] == 0 and g_env["solves_with_live_neighbour"] == 1.0
                                          and g_env["solves_with_zero_neighbour"] < 0.5 and g_env["donor_contributes"])
    ok["detector_sensitive_to_broken_copy"] = not res["H_broken"][0]["born"]
    s, r = res["engine_seeded"], res["engine_random"]
    ok["seeded_run_is_inserted_not_clean"] = (s["endo_inserted"] > 0 and s["endo_clean"] == 0 and s["founders"]["seeded_replicator"] > 0
                                              and not s["spontaneous_replication"])
    ok["random_run_has_no_replication"] = r["births_endo"] == 0 and r["founders"]["seeded_replicator"] == 0
    res["checks"] = ok
    res["all_pass"] = all(ok.values())
    res["grammar_digest"] = GR.digest()
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for k_, v in ok.items():
        print("PASS" if v else "FAIL", k_)
    print("ALL_PASS" if res["all_pass"] else "SOME_FAIL", "sha256", hashlib.sha256(open(out, "rb").read()).hexdigest()[:16])
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
