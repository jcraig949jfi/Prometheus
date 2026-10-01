"""PROPOSED patches for z80atlas-verify-2026-09-22/world.py (W2-8). NOT applied to any campaign file.

Each patch is a function that installs a corrected method on a world module object, so the regression tests in ../tests
can run the frozen code and the patched code side by side. To adopt one in a NEW instrument, copy the method body; the
frozen harness stays as it is (historical results were produced by it).

  P1  _competence: cache key = (genome, task spec), not genome alone                       [D1]
  P2  _pair_interact: read every donor oid BEFORE any relabel; on relabel also reset the     [D8, D9]
      per-birth fields (age, born, slot_owner, birth_niche, provisional comp from the donor)
      and count carried register state into ct["nonheritable_state_inherited"]           [D5]
  P3  _mutate (Z8_SLOTTED): honour mutation_operator by instruction boundaries             [D4]
"""
from __future__ import annotations


def _spec_key(spec):
    return (spec.transform, spec.read_order, spec.bridge, spec.n_episodes, spec.budget, spec.neutral,
            getattr(spec, "output_gate", None), getattr(spec, "cue_cost", None))


def apply_p1(world):
    import hashlib

    def _competence(self, g):
        if self.spec.neutral:
            return {"comp": 0.0, "held": 0.0, "reads_at_answer": -1, "answered": 0.0,
                    "halted": 0.0, "ops": 0.0, "neutral": True}
        h = (hashlib.blake2b(g, digest_size=8).digest(), _spec_key(self.spec))     # P1: spec is part of the key
        hit = self.val_cache.get(h)
        if hit is not None:
            return hit
        r = world.tasks.competence(g, self.spec, seed=(self.seed * 7919 + self.epoch),
                                   held_seed=(self.seed * 7919 + self.epoch + 500000))
        if len(self.val_cache) > 20000:
            self.val_cache.clear()
        self.val_cache[h] = r
        return r

    world.Runner._competence = _competence
    return world


def apply_p2(world):
    """Full copy of Runner._pair_interact with the P2 changes marked `# P2`."""
    p11, z8taint, C, G = world.p11, world.z8taint, world.C, world.G

    def _pair_interact(self, i, a, b):
        z8 = world.z8
        ga, gb = self._genome(a), self._genome(b)
        n = self.L
        tape = bytearray(world._pow2(2 * n))
        tape[0:len(ga)] = ga
        tape[n:n + len(gb)] = gb
        ctxs = {}
        st0 = ((None if a.regs is None else list(a.regs), a.fz, a.fc),
               (None if b.regs is None else list(b.regs), b.fz, b.fc))
        prov, prov_lit = bytearray(len(tape)), bytearray(len(tape))
        track = self.track_material
        if track:
            otape = bytearray([z8taint.UNKNOWN]) * len(tape)
            otape[0:len(ga)] = a.orig[:len(ga)]
            otape[n:n + len(gb)] = b.orig[:len(gb)]
        for who, start, org in ((0, 0, a), (1, n, b)):
            ctx = z8.Ctx(tape, start, n, policy=z8.ARENA, rng=self.rng, copy_mut_rate=self.copy_mut, sense=who)
            ctx.regs, ctx.fz, ctx.fc = org.regs, org.fz, org.fc
            ctx.prov, ctx.prov_lit, ctx.who = prov, prov_lit, who + 1
            if track:
                _pc, org.reg_taint = z8taint.run_tainted(ctx, start, self.t["slice"], self._ops_mask(), orig=otape,
                                                         here=org.niche, reg_taint=org.reg_taint)
            else:
                z8.run(ctx, start, self.t["slice"], ops_enabled=self._ops_mask())
            org.regs, org.fz, org.fc = ctx.regs, ctx.fz, ctx.fc
            org.ops += ctx.ops
            org.last_tel = ctx.telemetry()
            ctxs[id(org)] = ctx
            self.ct["ops"] += ctx.ops
            self.ct["slices"] += 1
            self.ct["copy_bytes"] += ctx.copy_bytes
        na, nb = bytes(tape[0:n]), bytes(tape[n:2 * n])
        pre_id = {id(a): (a.oid, a.anc, a.comp, a.held, a.probe), id(b): (b.oid, b.anc, b.comp, b.held, b.probe)}  # P2
        for org, old, new in ((a, ga, na), (b, gb, nb)):
            pre_mut = new
            new = self._mutate(new)
            if track:
                h0 = 0 if org is a else n
                org.orig = world._mutated_orig(pre_mut, new, otape[h0:h0 + n], org.niche)
            self.mem[org.slot:org.slot + self.slot_size] = bytes(self.slot_size)
            self.mem[org.slot:org.slot + len(new)] = new
            org.length = len(new)
            fid_self = world._fidelity(old, new)
            other = gb if org is a else ga
            donor = b if org is a else a
            fid_other = world._fidelity(other, new)
            donor_wrote = ctxs[id(donor)].writes_other
            if p11.predecessor_accepts(fid_other, fid_self, donor_wrote, n):
                self.ct["replication_events"] += 1
                self.ct["births_endogenous"] += 1
                src = donor
                src_oid, src_anc, s_comp, s_held, s_probe = pre_id[id(src)]                  # P2: pre-relabel identity
                vs = 0 if org is a else 1
                kw = dict(n=n, tape_len=len(tape), ga=ga, gb=gb, st_a=st0[0], st_b=st0[1],
                          budget=self.t["slice"], ops_mask=self._ops_mask(), cmr=self.copy_mut, victim_side=vs,
                          seed=(self.seed, G.cell_id(self.cell), self.epoch, i, vs))
                res = p11.assay(z8, **kw)
                v0 = 0 if vs == 0 else n
                diag = p11.ordinary_diagnostics(z8, final_half=pre_mut, prov_half=prov[v0:v0 + n],
                                                lit_half=prov_lit[v0:v0 + n], **kw)
                lit_ok = sum(1 for d in res["draws"] if d["C2"] and d["C5"] and d["n_directed"]
                             and d["donor_last_wrote_share"] >= C["P11_AUTHORSHIP"])
                rec = {"pass": res["pass"], "draws_passed": res["draws_passed"],
                       "pass_literal": lit_ok >= C["P11_MAJORITY"],
                       "C2": res["C2_majority"], "C4": res["C4_majority"], "C5": res["C5_majority"], **diag}
                if res["pass"]:
                    self.ct["p11_events"] += 1
                for crit in ("C2", "C4", "C5"):
                    if not rec[crit]:
                        self.ct["p11_fail_" + crit] += 1
                src.births += 1
                src.fidelity = fid_other
                src.repro_span = n
                child_oid = self.next_oid
                self._lin_birth(child_oid, src_oid, org.niche, fid_other, n, res["pass"], causal_pred=True, p11_rec=rec)
                if org.regs is not None:                                                    # P2 -> anticheat D5
                    self.ct["nonheritable_state_inherited"] += 1
                self.slot_owner[org.slot] = child_oid                                        # P2
                self.birth_niche[child_oid] = org.niche                                      # P2
                org.pid, org.anc, org.oid = src_oid, src_anc, child_oid
                org.age, org.born = 0, self.epoch                                            # P2
                org.comp, org.held, org.probe = s_comp, s_held, s_probe                      # P2: provisional, as _on_birth
                self.next_oid += 1
                if self.first_replicator is None:
                    self.first_replicator = {"epoch": self.epoch, "oid": src_oid, "fidelity": round(fid_other, 3),
                                             "genome": other.hex(), "repro_span": n, "donor_writes_other": donor_wrote,
                                             "seeded": self.d["seeded_instrument"], "slot": src.slot,
                                             "base_is_zero": src.slot == 0}
            elif fid_other >= C["PAIR_FID_OTHER_MIN"] and fid_self < C["PAIR_FID_SELF_MAX"]:
                self.ct["births_similar_no_write"] += 1

    world.Runner._pair_interact = _pair_interact
    return world


def apply_p3(world):
    """Z8_SLOTTED: choose the mutated byte among the slot's bytes whose CLASS matches the operator."""
    orig = world.Runner._mutate

    def _mutate(self, g):
        c = self.cell
        if c["representation"] != "Z8_SLOTTED" or c["mutation_operator"] == "BOTH":
            return orig(self, g)
        rate = self.mut_rate
        g = bytearray(g)
        if c["atlas_axis"] == "RECOMBINATION":
            g = bytearray(self._recombine(bytes(g)))
        opcodes = set(self._boundaries(bytes(g)))
        want_op = c["mutation_operator"] == "OPCODE"
        for s in range(max(1, len(g) // 4)):
            if self.rng.random() >= rate * 4:
                continue
            cand = [j for j in range(s * 4, min(s * 4 + 4, len(g))) if (j in opcodes) == want_op]
            if not cand:
                continue
            j = cand[self.rng.randrange(len(cand))]
            if want_op:
                g[j] = self.rng.randrange(256)
            else:
                u = self.rng.random()
                if u < 0.45:
                    g[j] = (g[j] + self.rng.randint(-8, 8)) & 0xFF
                elif u < 0.90:
                    g[j] ^= 1 << self.rng.randrange(8)
                else:
                    g[j] = self.rng.randrange(256)
        return bytes(g)

    world.Runner._mutate = _mutate
    return world
