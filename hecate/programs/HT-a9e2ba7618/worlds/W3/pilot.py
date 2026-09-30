"""Phase 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN only (no treatment arm)."""
import json, sys, time
import numpy as np
import core as C

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
t0 = time.process_time()
out = open("pilot_rows.jsonl", "w")


def emit(row):
    row.update(attempt=ATTEMPT, params=C.PARAMS)
    out.write(json.dumps(row) + "\n"); out.flush()


for s in C.SEEDS:
    # POSITIVE_CONTROL: noise-free, well separated, cross-scale rule + oscillators
    x, envs, spans = C.clean_separated_signal(s)
    truth = C.ground_truth(envs)
    A = C.cross_scale_graph(C.components(C.scale_stack(x)))
    lab = C.kuramoto_clusters(A, np.random.default_rng(2000 + s))
    emit(dict(arm="POSITIVE_CONTROL", seed=s, spans=spans,
              ari_osc=C.ari(lab, truth), ari_comp=C.ari(C.graph_components(A), truth),
              n_edges=C.n_edges(A), n_clusters=int(len(set(lab)))))

    # CHEAT: success injected directly into the observable
    emit(dict(arm="CHEAT", seed=s, spans=spans,
              ari_osc=C.ari(truth, truth), ari_comp=None, n_edges=None,
              n_clusters=int(len(set(truth)))))

    # NULL_TWIN: noisy signal, finest-scale rule, edge count matched to cross-scale graph
    x, envs, spans = C.noisy_signal(s)
    truth = C.ground_truth(envs)
    ids = C.components(C.scale_stack(x))
    target = C.n_edges(C.cross_scale_graph(ids))   # integer only; no treatment dynamics
    A1 = C.single_scale_graph(ids, 0)
    B = C.match_edge_count(A1, target, np.random.default_rng(3000 + s))
    lab = C.kuramoto_clusters(B, np.random.default_rng(2000 + s))
    emit(dict(arm="NULL_TWIN", seed=s, spans=spans,
              ari_osc=C.ari(lab, truth), ari_comp=C.ari(C.graph_components(B), truth),
              n_edges=C.n_edges(B), n_edges_single_raw=C.n_edges(A1), n_edges_target=target,
              deg_hist_twin=C.degree_hist(B), n_clusters=int(len(set(lab)))))

out.close()
print("cpu_s", round(time.process_time() - t0, 1))
