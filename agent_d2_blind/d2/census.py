"""Grammar census engine (PREREG-CENSUS phase 1).

Reports three diversity notions separately and never conflates them:
  syntactic (program count)
  structural-behavioural (distinct output terms on the frozen probe battery)
  semantic-behavioural (distinct extensional behaviour of those outputs)

Semantic equality is probe-relative. No claim of program equivalence is made.
"""
import time
from . import classify
from .core import nodes

# frozen physics constants for both uses of the evaluator
LIMIT = 2000
DMAX = 16


class Census:
    def __init__(self, basis, A, I12, I24):
        self.b = basis
        self.A = A
        self.I12 = I12
        self.I24 = I24
        self.behav = {}          # prog term -> (24-tuple of results)
        self.term_id = {}        # output program term -> int id (>=0)
        self.behav_id12 = {}
        self.behav_id24 = {}
        self.evals = 0

    def _behav(self, prog):
        r = self.behav.get(prog)
        if r is None:
            out = []
            for i in self.I24:
                res = self.b.run(prog, i, LIMIT, DMAX)
                out.append(res if res[0] == "err" else ("ok", res[1]))
            r = tuple(out)
            self.behav[prog] = r
            self.evals += len(self.I24)
        return r

    def _sid(self, prog, table, key):
        i = table.get(key)
        if i is None:
            i = len(table)
            table[key] = i
        return i

    def scan(self, enum, nmax, per_term_labels_upto=0, invalid_distinct=False):
        """One pass over the enumeration. Returns the census record."""
        A = self.A
        b = self.b
        t0 = time.time()
        struct_hashes = set()
        classes = {}             # semkey12 hash -> record
        sem24 = set()
        errkinds = {}
        n_total = 0
        n_dead = 0
        n_any_valid = 0
        per_term = {}            # for the ordering battery (small horizon only)

        ERR_IDS = {}

        def eid(kind):
            i = ERR_IDS.get(kind)
            if i is None:
                i = -(len(ERR_IDS) + 2)
                ERR_IDS[kind] = i
            return i

        for rank, t in enum.stream(nmax):
            n_total += 1
            skey = []
            k12 = []
            k24 = []
            dead = True
            noop = True
            const_val = None
            const_ok = True
            n_nonerr = 0
            pairs = []
            for p in A:
                r = b.apply_transform(t, p, LIMIT, DMAX)
                self.evals += 1
                if r[0] == "err":
                    kind = r[1]
                    errkinds[kind] = errkinds.get(kind, 0) + 1
                    e = eid(kind)
                    skey.append(e); k12.append(e); k24.append(e)
                    noop = False
                    continue
                val = r[1]
                n_nonerr += 1
                if const_val is None:
                    const_val = val
                elif val != const_val:
                    const_ok = False
                if r[0] == "invalid":
                    if invalid_distinct:
                        iv = -1000000 - self._sid(None, self.term_id, ("INV", str(val)))
                        skey.append(iv); k12.append(iv); k24.append(iv)
                    else:
                        skey.append(-1); k12.append(-1); k24.append(-1)
                    noop = False
                    if val != p:
                        pairs.append((p, val))
                    continue
                dead = False
                if val != p:
                    noop = False
                    pairs.append((p, val))
                skey.append(self._sid(val, self.term_id, val))
                bh = self._behav(val)
                k12.append(self._sid(None, self.behav_id12, bh[:12]))
                k24.append(self._sid(None, self.behav_id24, bh))
            if dead:
                n_dead += 1
                if invalid_distinct:
                    struct_hashes.add(hash(tuple(skey)))
            else:
                n_any_valid += 1
                struct_hashes.add(hash(tuple(skey)))
            const = const_ok and n_nonerr >= 2
            h12 = hash(tuple(k12))
            sem24.add(hash(tuple(k24)))
            rec = classes.get(h12)
            sz = b.size(t)
            if rec is None:
                classes[h12] = [1, sz, rank, t, dead, noop, const]
            else:
                rec[0] += 1
                if sz < rec[1] or (sz == rec[1] and rank < rec[2]):
                    rec[1] = sz
                    rec[2] = rank
                    rec[3] = t
            if per_term_labels_upto and sz <= per_term_labels_upto and not dead:
                labs, npairs = classify.labels(pairs)
                per_term[t] = frozenset(labs)

        return {
            "n_total": n_total,
            "n_dead": n_dead,
            "n_live": n_any_valid,
            "n_struct_classes": len(struct_hashes),
            "n_sem_classes_I12": len(classes),
            "n_sem_classes_I24": len(sem24),
            "classes": classes,
            "errkinds": errkinds,
            "per_term_labels": per_term,
            "seconds": round(time.time() - t0, 1),
            "evals": self.evals,
        }

    # ------------------------------------------------------------------
    def class_pairs(self, classes, identity_h=None):
        """Compute (probe,output) pairs once per semantic class representative."""
        b = self.b
        out = {}
        for h, rec in classes.items():
            cnt, minsz, minrank, t, dead, noop, const = rec
            if dead:
                out[h] = ("TRIV_DEAD", [], minsz, minrank, cnt, t, False)
                continue
            pairs = []
            productive = False
            for p in self.A:
                r = b.apply_transform(t, p, LIMIT, DMAX)
                if r[0] == "err":
                    continue
                if r[0] == "ok":
                    productive = True
                if r[1] != p:
                    pairs.append((p, r[1]))
            kind = "LIVE"
            if identity_h is not None and h == identity_h:
                kind = "TRIV_NOOP"
            elif noop:
                kind = "TRIV_NOOP"
            elif const:
                kind = "TRIV_CONST"
            out[h] = (kind, pairs, minsz, minrank, cnt, t, productive)
        return out

    @staticmethod
    def label_at(cp, c=0.9):
        """Apply the family + residual classifiers at consistency threshold c."""
        out = {}
        for h, (kind, pairs, minsz, minrank, cnt, t, prod) in cp.items():
            if kind == "TRIV_DEAD":
                out[h] = (kind, frozenset(), frozenset(), minsz, minrank, cnt, t, prod)
                continue
            labs, _ = classify.labels(pairs, c)
            sec = classify.secondary(pairs, c) if pairs else set()
            if pairs and classify.feature_collapse(pairs):
                sec.add("S7_COLLAPSE")
            out[h] = (kind, frozenset(labs), frozenset(sec), minsz, minrank, cnt, t, prod)
        return out
