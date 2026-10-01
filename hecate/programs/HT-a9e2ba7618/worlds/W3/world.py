"""Phase 2: TREATMENT, CONTROL, plus the three pilot arms rerun in the same code path."""
import json, time
import numpy as np
import core as C

t0 = time.process_time()
out = open("rows.jsonl", "w")


def emit(row):
    row.update(params=C.PARAMS)
    out.write(json.dumps(row) + "\n"); out.flush()


def run_graph(arm, s, A, truth, spans, **extra):
    lab = C.kuramoto_clusters(A, np.random.default_rng(2000 + s))
    emit(dict(arm=arm, seed=s, spans=spans, ari_osc=C.ari(lab, truth),
              ari_comp=C.ari(C.graph_components(A), truth), n_edges=C.n_edges(A),
              deg_hist=C.degree_hist(A), n_clusters=int(len(set(lab))),
              n_graph_components=int(len(set(C.graph_components(A)))), **extra))


for s in C.SEEDS:
    # POSITIVE_CONTROL
    x, envs, spans = C.clean_separated_signal(s)
    truth = C.ground_truth(envs)
    run_graph("POSITIVE_CONTROL", s, C.cross_scale_graph(C.components(C.scale_stack(x))), truth, spans)
    # CHEAT
    emit(dict(arm="CHEAT", seed=s, spans=spans, ari_osc=C.ari(truth, truth), ari_comp=None,
              n_edges=None, n_clusters=int(len(set(truth)))))
    # noisy signal shared by TREATMENT, NULL_TWIN and (via surrogate) CONTROL
    x, envs, spans = C.noisy_signal(s)
    truth = C.ground_truth(envs)
    ids = C.components(C.scale_stack(x))
    A = C.cross_scale_graph(ids)
    run_graph("TREATMENT", s, A, truth, spans)
    A1 = C.single_scale_graph(ids, 0)
    B = C.match_edge_count(A1, C.n_edges(A), np.random.default_rng(3000 + s))
    run_graph("NULL_TWIN", s, B, truth, spans, n_edges_single_raw=C.n_edges(A1))
    xs = C.phase_surrogate(x, np.random.default_rng(4000 + s))
    run_graph("CONTROL", s, C.cross_scale_graph(C.components(C.scale_stack(xs))), truth, spans)

out.close()
cpu = time.process_time() - t0
json.dump({"world_cpu_s": cpu}, open("world_cpu.json", "w"))
print("cpu_s", round(cpu, 1))
