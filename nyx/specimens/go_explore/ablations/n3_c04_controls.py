"""NYX-44 controls for go_explore c04 (representation selection). FROZEN 2026-09-12 ~04:40Z, BEFORE any
managed pin exists and before any executable result. Ruling 2026-09-12 (N3 accepted; N4 closed):
pre-authorized to run when Techne satisfies #201; controls may not be altered after a result except to
repair a demonstrably malformed control, ledgered BEFORE rerunning. Priority order is the ruling's.

HOW IT RUNS (when a pin exists): the specimen's OWN code is imported from the managed pin path given as
argv[1] (the directory containing robustified/). The environment is stubbed at the module-global ENV the
specimen already uses (it never touches ALE here); frames are synthetic uint8 arrays. Nothing in the
specimen is modified; the objective under test is Explore.try_split_frames as shipped, reached through the
same call the ancestor makes (maybe_split_dynamic_state -> try_split_frames), with Explore constructed
with minimal args. If the import fails on gym/cv2/loky, the receipt records CANNOT_INSTANTIATE with the
missing module and NOTHING else is attempted (no shim; a shim would be a bridge).

PREDICTED OUTCOMES (written now so the receipt can embarrass them):
  1 dynamic_state on/off        off: the cell key is the raw frame bytes and the archive size equals the
                                number of distinct frames; on: fewer cells at a chosen granularity.
  2 entropy vs count-only       with the entropy term removed (count-only), the search picks a parameter
                                whose part count is nearest the target regardless of balance; the
                                shipped score prefers the balanced one when counts tie.
  3 uniform vs table weights    (c02, exercised for the record) uniform selection changes WHICH cells are
                                chosen, not whether admission (c01) works; no prediction about c04.
  4 prob_override 0 vs >0       >0 admits worse elites at random (F5); with 0 the archive is monotone in
                                the fitness order.
  5 c04 POSITIVE                sample from k=4 well-separated synthetic 'rooms' (frames with distinct
                                block patterns); a downscale family that can separate them; the search
                                returns ~4 parts of near-equal occupancy.
  6 c04 NEGATIVE                a constant sample: every parameter yields one part; score 0; the search
                                returns a degenerate representation and the archive has one cell.
  7 c04 CHEAT (decisive)        a family in which one parameter setting maps EVERY frame to a unique key
                                (e.g. no downscaling at full pixel depth on distinct-noise frames): the
                                penalty sqrt(|n - target|/target + 1) must make it LOSE to a coarser
                                setting when n approaches the sample size. If the unique-key setting
                                WINS, c04 is maximizing apparent diversity by inventing identifiers and
                                the control kills it.
"""
from __future__ import annotations
import datetime as _dt, importlib, json, sys, types
from pathlib import Path
HERE = Path(__file__).resolve().parent
REC = {"date": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "frozen": "2026-09-12T04:40Z", "blocks": []}

def block(name, predicted, fn):
    try:
        obs, err = fn(), None
    except Exception as e:  # noqa: BLE001
        obs, err = None, f"{type(e).__name__}: {e}"[:400]
    REC["blocks"].append({"name": name, "predicted": predicted, "observed": obs, "error": err})

def main(pin_root: str) -> None:
    sys.path.insert(0, str(Path(pin_root) / "robustified"))
    try:
        ge = importlib.import_module("goexplore_py.goexplore")
        import numpy as np
    except Exception as e:  # noqa: BLE001
        REC["blocks"].append({"name": "IMPORT", "predicted": "specimen importable from the managed pin", "observed": None,
                              "error": f"CANNOT_INSTANTIATE: {type(e).__name__}: {e}"[:400],
                              "note": "no shim attempted (a shim would be a bridge; ruling anti-reassembly)"})
        return
    rng = np.random.default_rng(20260912)

    def frames_rooms(k=4, n=200, shape=(210, 160)):
        out = []
        for i in range(n):
            f = np.zeros(shape, dtype=np.uint8)
            r = i % k
            f[(r * shape[0]) // k:((r + 1) * shape[0]) // k, :] = 200
            f += rng.integers(0, 3, size=shape, dtype=np.uint8)  # tiny noise
            out.append(f)
        return out

    def frames_constant(n=200, shape=(210, 160)):
        return [np.full(shape, 7, dtype=np.uint8) for _ in range(n)]

    def frames_noise(n=200, shape=(210, 160)):
        return [rng.integers(0, 255, size=shape, dtype=np.uint8) for _ in range(n)]

    def make_explore(args_over):
        # Minimal args namespace mirroring what try_split_frames / maybe_split_dynamic_state read.
        a = types.SimpleNamespace(cell_split_factor=0.02, split_iterations=60, max_recent_frames=1000,
                                  recompute_dynamic_state_every=1, first_compute_dynamic_state=0,
                                  first_compute_archive_size=10, max_archive_size=10 ** 9, dynamic_state=True,
                                  use_real_pos=False, base_path=str(HERE / "_scratch"), reset_pool=False, n_cpus=1,
                                  explore_steps=1, ignore_death=0, batch_size=1, prob_override=0.0, optimize_score=True,
                                  reset_cell_on_update=False, save_cells=False, recent_frame_add_prob=1.0, game="stub")
        for k, v in args_over.items():
            setattr(a, k, v)
        ex = ge.Explore.__new__(ge.Explore)  # bypass __init__ (it builds ENV and pools); set only what try_split_frames reads
        ex.args = a
        ex.normal_frame_shape = (210, 160)
        return ex

    def run_split(frames, args_over=None):
        ex = make_explore(args_over or {})
        rle = [ge.RLEArray.fromarray(f) if hasattr(ge, "RLEArray") else f for f in frames]
        enc = [r.tobytes() if hasattr(r, "tobytes") else r for r in rle]
        shape, pix, n = ex.try_split_frames(enc)
        return {"shape": list(shape), "pix_val": int(pix), "n_parts": int(n)}

    block("5_c04_positive_k4_rooms", "~4 parts of near-equal occupancy", lambda: run_split(frames_rooms()))
    block("6_c04_negative_constant", "one part; degenerate representation", lambda: run_split(frames_constant()))
    block("7_c04_CHEAT_unique_key_family", "the unique-key (full-resolution) setting must LOSE to a coarser one: n_parts far below the sample size (200); if n_parts ~ 200, c04 is killed",
          lambda: run_split(frames_noise(), {"cell_split_factor": 0.02}))
    block("2_entropy_vs_count_only", "shipped score prefers the balanced partition when counts tie; count-only cannot; measured as n_parts and occupancy spread on the rooms sample under two targets",
          lambda: {"target_0.02": run_split(frames_rooms(), {"cell_split_factor": 0.02}), "target_0.5": run_split(frames_rooms(), {"cell_split_factor": 0.5})})
    block("1_dynamic_state_on_off", "off: keys are raw frame bytes (distinct frames -> distinct cells); on: fewer cells. Measured as distinct keys over the rooms sample",
          lambda: {"off_distinct_raw_keys": len({f.tobytes() for f in frames_rooms()}), "on": run_split(frames_rooms())})
    block("4_prob_override", "with prob_override > 0 should_accept_cell returns True for worse candidates at that rate; with 0 never",
          lambda: {"p0": sum(make_explore({"prob_override": 0.0}).should_accept_cell(ge.Cell(score=10, trajectory_len=5), 1, 50) for _ in range(200)),
                   "p0.5": sum(make_explore({"prob_override": 0.5}).should_accept_cell(ge.Cell(score=10, trajectory_len=5), 1, 50) for _ in range(200))})
    block("3_uniform_vs_table_weights", "record only: c02 is POLICY; no c04 prediction", lambda: "not run as a c04 control; see cuts.json c02")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: n3_c04_controls.py <managed pin root containing robustified/>  -- FROZEN; do not edit after a result"); sys.exit(2)
    main(sys.argv[1])
    out = HERE / f"RECEIPT_N3_c04_{_dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')}.json"
    out.write_text(json.dumps(REC, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(REC, indent=1, ensure_ascii=False, default=str))
