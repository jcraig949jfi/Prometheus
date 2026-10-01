"""W2-Y: 'flood ceiling' -- a tighter any-program transport bound than the W2-P/W2-U light cone.
The light cone (T2.earliest) assumes a program can address ANY neighbour (global: any site at 1 hop) and ignores
loss, jitter and dup. Engine facts it misses (engine.py _emit, 482-530):
  * global topology: each of F=fanout copies goes to a UNIFORM random other site (rng.ROUTE), not chosen;
  * dest_mode 'sample' (non-global): each copy goes to a neighbour drawn by routing weights w (init 16 each =
    uniform, engine.py:158); only plastic_route can bias w -> treated optimistically as 'all';
  * loss: copy survives w.p. (1-loss)^(dist if loss_per_hop else 1); delay = lat_base + lat_hop*dist + U{0..jitter};
  * dup: extra copy w.p. dup, delay + 1 + U{0..jitter}, independent loss.
MAXIMAL FLOOD (upper bound for ANY program on 'did the actuator process a cue-descended packet by ro'):
  a site is informed at its first awake tick >= first arrival (sensor: first awake tick in the cue window);
  every informed site emits its copies at EVERY awake tick from then on (perfect memory). Ignored (optimistic):
  cap, collision, economy, decay, noise. Monte-Carlo with this worker's own RNG (not the engine streams), R reps
  per (world, trial), on the row's own placements (sidx/ridx/ro from envs.build).
RELAY: .5 + .5 P.  MAJ: per-rep vote count k (per-sensor floods sharing wake draws) -> maj_acc(k, flip_p).
KA1: with loss=jitter=dup=0 and deterministic dests the flood ceiling equals T2 lc exactly (sync)."""
import numpy as np
import task2_timing as T2  # noqa (sys.path set by caller)


def _dests(ph, nbr, dist, u, rs, R):
    """destinations [R, F] and their hop distances for copies emitted by site u."""
    N = ph.n_sites
    if ph.topology == "global":
        rec = (u + 1 + rs.integers(0, N - 1, size=(R, ph.fanout))) % N
        return rec, np.ones_like(rec)
    if ph.dest_mode == "all" or ph.plastic_route:
        rec = np.broadcast_to(np.asarray(nbr[u]), (R, len(nbr[u])))
        return rec, np.broadcast_to(np.asarray(dist[u]), rec.shape)
    j = rs.integers(0, len(nbr[u]), size=(R, ph.fanout))
    return np.asarray(nbr[u])[j], np.asarray(dist[u])[j]


def flood_P(ph, src_list, a, t0, ro, cl, rs, R=64, opts=None):
    """[R, len(src_list)] bool: sensor i's information processed at actuator a by ro."""
    o = dict(loss=True, jitter=True, dup=True)
    if opts:
        o.update(opts)
    nbr, dist = T2.topo(ph)
    N = ph.n_sites
    base = 1.0 - ph.loss
    H = ro - t0 + 1
    J = ph.lat_jitter if o["jitter"] else 0
    if ph.update_mode == "sync":
        awake = np.broadcast_to((((t0 + np.arange(H)) % ph.update_period) == 0)[None, :, None], (R, H, N))
    else:
        awake = rs.random((R, H, N)) < ph.p16(ph.update_p) / 65536.0
    out = np.zeros((R, len(src_list)), dtype=bool)
    for si, s in enumerate(src_list):
        inf = np.zeros((R, N), dtype=bool)
        pend = np.zeros((R, N), dtype=bool)
        arr = np.zeros((R, H + 1, N), dtype=bool)
        for h in range(H):
            pend |= arr[:, h]
            aw = awake[:, h]
            newly = pend & aw & ~inf
            if h < cl:
                newly[:, s] |= aw[:, s]
            inf |= newly
            pend &= ~aw
            if h == H - 1:
                break
            rr, uu = np.nonzero(inf & aw)
            if rr.size:
                E = rr.size
                if ph.topology == "global":
                    rec = (uu[:, None] + 1 + rs.integers(0, N - 1, size=(E, ph.fanout))) % N
                    dd = np.ones_like(rec)
                elif ph.dest_mode == "all" or ph.plastic_route:
                    rec = np.asarray(nbr)[uu]; dd = np.asarray(dist)[uu]
                else:
                    j = rs.integers(0, np.asarray(nbr).shape[1], size=(E, ph.fanout))
                    rec = np.asarray(nbr)[uu[:, None], j]; dd = np.asarray(dist)[uu[:, None], j]
                ri = np.broadcast_to(rr[:, None], rec.shape)
                for copy in (0, 1):
                    if copy == 1 and (not o["dup"] or ph.dup <= 0):
                        break
                    keep = (rs.random(rec.shape) < ph.dup) if copy else np.ones(rec.shape, dtype=bool)
                    if o["loss"]:
                        sv = base ** dd if ph.loss_per_hop else np.full(dd.shape, base)
                        keep &= rs.random(rec.shape) < sv
                    dl = ph.lat_base + ph.lat_hop * dd
                    if J:
                        dl = dl + rs.integers(0, J + 1, size=rec.shape)
                    if copy:
                        dl = dl + 1 + (rs.integers(0, J + 1, size=rec.shape) if J else 0)
                    tgt = h + np.clip(dl, 1, None)
                    m = keep & (tgt < H)
                    arr[ri[m], tgt[m], rec[m]] = True
        out[:, si] = inf[:, a]
    return out


def ceilings(ph, env, seeds, R=64, seed=0, opts=None, envs=None):
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    fam = env.family
    ns = 1 if fam in ("RELAY", "FLIP") else env.n_maj
    acck = [T2.maj_acc(k, env.flip_p) for k in range(ns + 1)] if fam == "MAJ" else [0.5, 1.0]
    rs = np.random.default_rng(seed)
    vals = []
    for b in range(0, len(seeds), 2):
        a = int(ridx[b])
        ss = [int(x) for x in sidx[b][:ns]]
        for k in range(env.trials):
            if not ep.scored[b, k]:
                continue
            t0 = k * env.period()
            ro = int(ep.ro_tick[b, k])
            kk = flood_P(ph, ss, a, t0, ro, env.cue_len, rs, R, opts).sum(1)
            vals.append(float(np.mean([acck[x] for x in kk])))
    return float(np.mean(vals))
