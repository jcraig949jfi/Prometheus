"""A reference model of the retention rule the Avida ancestry cut claims, for FIXTURES AND CONTROLS ONLY.

It is Nyx's reading of the fossil restated as ~100 lines of Python, so that the packet's observables can be checked
defined, and its controls can be run, without opening a single .spop from the body. It is not Avida: the population
underneath is a toy (uniform parent choice, one-site substitution, random placement). What is modelled faithfully is
the bookkeeping, line for line:

    Arbiter.birth        Genotype::ClassifyNewUnit                 Genotype.cc:282-299
    Arbiter.classify     GenotypeArbiter::ClassifyNewUnit          GenotypeArbiter.cc:278-369   (no-hints path)
    G.__init__           Genotype::Genotype (founder constructor)  Genotype.cc:128-184
    Arbiter.remove_unit  Genotype::RemoveUnit + AdjustGenotype     Genotype.cc:321-331, GenotypeArbiter.cc:372-410
    Arbiter._remove      GenotypeArbiter::removeGenotype           GenotypeArbiter.cc:498-533
    Arbiter.perform_update  GenotypeArbiter::PerformUpdate         GenotypeArbiter.cc:85-103
    World.run            Avida2Driver::Run                         targets/avida/Avida2Driver.cc:91-162
    World.save           cPopulation::SavePopulation + LegacySave  cPopulation.cc:6362-6563, Genotype.cc:356-392

Two switches exist only to build controls: prune=False keeps every genotype ever founded (the history Avida does
NOT keep), and the holder arms reproduce the two reference holders outside the arbiter (cDeme.cc:958,985 passive;
cBirthChamber.cc:160 active).
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
HEADER = ("#filetype genotype_data\n"
          "#format id src src_args parents num_units total_units length merit gest_time fitness gen_born update_born "
          "update_deactivated depth hw_type inst_set sequence cells gest_offset lineage \n"
          "# Structured Population Save\n# SYNTHETIC FIXTURE (nyx.atlas.experiments.avida_ancestry.model)\n\n")


class G:
    def __init__(self, gid: int, seq: str, src: str, src_args: str, parents: List["G"], update: int):
        self.id, self.seq, self.src, self.src_args = gid, seq, src, src_args
        self.parents = list(parents)
        for p in self.parents:
            p.p_refs += 1                                   # Genotype.cc:160
        self.depth = self.parents[0].depth + 1 if self.parents else 0   # Genotype.cc:177
        self.update_born, self.update_deactivated = update, -1
        self.num, self.total, self.a_refs, self.p_refs = 1, 1, 1, 0     # Genotype.cc:143-152
        self.active, self.gone = True, False


def _cls(src: str, src_args: str) -> str:
    return "D" if src.split(":")[0] in ("div", "dup") else "P:" + src_args


class Arbiter:
    def __init__(self, prune: bool = True, record_parents: bool = True):
        self.prune, self.record_parents = prune, record_parents
        self.next_id, self.cur_update = 1, -1              # GenotypeArbiter.cc:46,49
        self.active: Dict[tuple, G] = {}
        self.historic: List[G] = []
        self.ever: List[G] = []                            # ground truth the fossil does not keep

    def birth(self, seq: str, parent: G, extra_parents: Optional[List[G]] = None) -> G:
        if not extra_parents and parent.seq == seq and _cls(parent.src, parent.src_args) == "D":
            parent.total += 1; parent.num += 1; parent.a_refs += 1      # breed true: no edge
            return parent
        return self.classify(seq, [parent] + list(extra_parents or []), "div:int", "(none)")

    def classify(self, seq: str, parents: List[G], src: str, src_args: str) -> G:
        key = (_cls(src, src_args), seq)
        g = self.active.get(key)
        if g is not None:                                  # convergence on a LIVING genotype: absorbed, no edge
            g.total += 1; g.num += 1; g.a_refs += 1
            return g
        g = G(self.next_id, seq, src, src_args, parents if self.record_parents else [], self.cur_update)
        self.next_id += 1
        self.active[key] = g
        self.ever.append(g)
        return g

    def remove_unit(self, g: G) -> None:
        g.a_refs -= 1; g.num -= 1
        if g.num == 0 and g.a_refs == 0:
            self._remove(g)

    def release_active(self, g: G) -> None:                # Genotype::RemoveActiveReference, Genotype.cc:395-402
        g.a_refs -= 1
        if g.a_refs == 0:
            self._remove(g)

    def _remove(self, g: G) -> None:
        if g.a_refs or g.gone:
            return
        if g.active:
            del self.active[(_cls(g.src, g.src_args), g.seq)]
            g.active, g.update_deactivated = False, self.cur_update
            self.historic.append(g)
        if g.p_refs or not self.prune:
            return
        for p in g.parents:
            p.p_refs -= 1
            if not p.a_refs:
                self._remove(p)
        self.historic.remove(g)
        g.gone = True

    def perform_update(self, update: int) -> None:
        self.cur_update = update + 1                       # GenotypeArbiter.cc:87
        if self.prune:
            for g in list(self.historic):
                if g.a_refs + g.p_refs == 0:
                    self._remove(g)


class World:
    """N cells; the driver loop of Avida2Driver.cc with its clock: events fire BEFORE the update counter advances."""

    def __init__(self, seed: int = 20260930, n_cells: int = 30, births_per_update: int = 6, mu: float = 0.35,
                 genome_len: int = 12, prune: bool = True, record_parents: bool = True, sexual: float = 0.0):
        self.rng = random.Random(seed)
        self.arb = Arbiter(prune, record_parents)
        self.cells: List[Optional[G]] = [None] * n_cells
        self.extra_units: List[tuple] = []                 # (cell, genotype) for parasite-like units
        self.births_per_update, self.mu, self.sexual = births_per_update, mu, sexual
        self.ancestor = "".join(self.rng.choice(ALPHABET) for _ in range(genome_len))
        self.update = -1
        self.n_births = self.n_edge_births = 0
        self.files: Dict[str, str] = {}
        self.inject(0, self.ancestor)                      # 'u begin Inject': classified while cur_update is still -1

    # -- events ---------------------------------------------------------------------------------------------
    def inject(self, cell: int, seq: str, src: str = "div:ext", src_args: str = "(none)") -> G:
        g = self.arb.classify(seq, [], src, src_args)      # InjectGenome: classified with NO parents
        self._place(cell, g)
        return g

    def sever(self, src_args: str = "whole-genome duplication") -> None:
        """PopulationActions.cc:153-171: every occupied cell is re-injected with a doubled genome and no parent."""
        for i, g in enumerate(self.cells):
            if g is not None:
                self.inject(i, g.seq + g.seq, "div:ext", src_args)

    def save(self, stem: str = "detail", save_historic: bool = True) -> str:
        rows = []
        order: Dict[int, list] = {}
        for i, g in enumerate(self.cells):
            if g is not None:
                order.setdefault(g.id, [g, []])[1].append(i)
        for cell, g in self.extra_units:
            order.setdefault(g.id, [g, []])[1].append(cell)
        for g, cells in order.values():
            c = ",".join(str(x) for x in cells)
            rows.append(self._row(g) + f"{c} {','.join('0' for _ in cells)} {','.join('0' for _ in cells)} ")
        if save_historic:
            rows += [self._row(g) for g in self.arb.historic]
        name = f"{stem}-{self.update}.spop"
        self.files[name] = HEADER + "\n".join(rows) + "\n"
        return name

    @staticmethod
    def _row(g: G) -> str:
        par = ",".join(str(p.id) for p in g.parents) or "(none)"
        return (f"{g.id} {g.src} {g.src_args} {par} {g.num} {g.total} {len(g.seq)} 0 0 0 -1 {g.update_born} "
                f"{g.update_deactivated} {g.depth} 0 heads_default {g.seq} ")

    # -- dynamics -------------------------------------------------------------------------------------------
    def _place(self, cell: int, g: G) -> None:
        old = self.cells[cell]
        self.cells[cell] = g                               # the newborn is classified BEFORE the occupant dies
        if old is not None:
            self.arb.remove_unit(old)

    def kill(self, cell: int) -> None:
        old, self.cells[cell] = self.cells[cell], None
        if old is not None:
            self.arb.remove_unit(old)

    def _step(self) -> None:
        for _ in range(self.births_per_update):
            occ = [i for i, g in enumerate(self.cells) if g is not None]
            if not occ:
                return
            parent = self.cells[self.rng.choice(occ)]
            seq = parent.seq
            if self.rng.random() < self.mu:
                k = self.rng.randrange(len(seq))
                seq = seq[:k] + self.rng.choice(ALPHABET) + seq[k + 1:]
            extra = None
            if self.sexual and self.rng.random() < self.sexual:
                extra = [self.cells[self.rng.choice(occ)]]
            before = self.arb.next_id
            g = self.arb.birth(seq, parent, extra)
            self.n_births += 1
            self.n_edge_births += int(self.arb.next_id != before and bool(g.parents))
            self._place(self.rng.randrange(len(self.cells)), g)

    def run(self, end: int, events=None) -> "World":
        """events: callable(world) invoked where Avida2Driver calls GetEvents, i.e. with world.update == the update
        just completed (-1 before the first)."""
        while True:
            if events:
                events(self)
            if self.update >= end:
                return self
            self.update += 1
            self._step()
            self.arb.perform_update(self.update)
