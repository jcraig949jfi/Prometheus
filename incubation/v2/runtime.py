"""runtime.py — the metered meta-runtime: processes, frontiers, meets, verification.

This is the layer whose ORGANIZATION the learner is allowed to change. A search program
(see dsl.py) declares processes (root x generator), a scheduling policy over runtime
observables, and a halt condition. The runtime executes any well-typed program under a
hard meter; everything a program does — generator calls, verification replays — is
counted. Nothing here knows about worlds, witnesses, or which organization is "right".

Cost model (preregistered): meter.ops += len(result) for every succ/pred call and += 1
per primitive application during verification replay. nodes = frontier insertions.

Orientation algebra (mechanical, not advisory): a candidate solution word can only be
CONSTRUCTED from (a) a successor-process rooted at the stage start reaching the stage
goal, (b) a predecessor-process rooted at the stage goal reaching the stage start, or
(c) a meet between one process of each of those two kinds. Any other organization has
no forward word derivable from its histories — programs built that way simply never
produce candidates and die on the meter. Every candidate is verified by replay before
being believed; in domains with unreliable predecessor information, reconstruction
from poisoned backward edges FAILS VERIFICATION and costs the program its meter.
"""
from __future__ import annotations

MEET_VERIFY_CAP = 200        # per run: candidate meets verified before giving up on meets


class Meter:
    __slots__ = ("ops", "budget")

    def __init__(self, budget):
        self.ops = 0
        self.budget = budget

    def charge(self, n):
        self.ops += n
        return self.ops <= self.budget


class Adapter:
    """Learner-visible boundary over (domain, task). Holds closures, not the domain."""

    def __init__(self, domain, task, meter):
        self._succ, self._pred = domain.succ, domain.pred
        self._apply = domain.apply
        self.start = domain.decode(task["start"])
        self.target = domain.decode(task["target"])
        self.via = domain.decode(task["via"]) if "via" in task else None
        self.meter = meter

    def succ(self, s):
        r = self._succ(s)
        self.meter.charge(len(r))
        return r

    def pred(self, s):
        r = self._pred(s)
        self.meter.charge(len(r))
        return r

    def replay(self, word, frm):
        s = frm
        for pid in word:
            self.meter.charge(1)
            s = self._apply(pid, s)
        return s

    def verify(self, word, frm, to):
        return self.replay(word, frm) == to


class Process:
    __slots__ = ("root", "gen", "frontier", "visited", "depth", "expansions",
                 "generated", "inserted")

    def __init__(self, root, gen):
        self.root, self.gen = root, gen          # gen: 'S' successors | 'P' predecessors
        self.frontier = [root]
        self.visited = {root: None}              # state -> (prev_state, pid)
        self.depth = 0
        self.expansions = 0
        self.generated = 0
        self.inserted = 0

    def expand(self, ad):
        fn = ad.succ if self.gen == "S" else ad.pred
        new = []
        for s in self.frontier:
            for pid, ns in fn(s):
                self.generated += 1
                if ns not in self.visited:
                    self.visited[ns] = (s, pid)
                    self.inserted += 1
                    new.append(ns)
            if not ad.meter.charge(0):
                break
        self.frontier = new
        self.depth += 1
        self.expansions += 1
        return new

    def word_root_to(self, state):
        """S-process: forward word root -> state. An edge label may be a TUPLE of
        primitive ids (a macro edge, arm A1): it flattens to its real primitives."""
        segs = []
        while self.visited[state] is not None:
            prev, pid = self.visited[state]
            segs.append(pid)
            state = prev
        return [p for seg in reversed(segs)
                for p in (seg if isinstance(seg, tuple) else (seg,))]

    def word_to_root(self, state):
        """P-process: forward word state -> root (each edge claims apply(pid,ns)=s)."""
        segs = []
        while self.visited[state] is not None:
            prev, pid = self.visited[state]
            segs.append(pid)
            state = prev
        return [p for seg in segs
                for p in (seg if isinstance(seg, tuple) else (seg,))]


def _obs(name, proc):
    if name == "FSIZE":
        return len(proc.frontier)
    if name == "DEPTH":
        return proc.depth
    return proc.generated - proc.inserted        # DUPS


def _sched_pick(sched, procs, it):
    if sched[0] == "ONLY":
        i = sched[1]
    elif sched[0] == "ALT":
        i = it % len(procs)
    else:                                        # ("IF", obs_a, op, obs_b)
        a = _obs(sched[1], procs[0])
        b = _obs(sched[3], procs[1])
        hold = a <= b if sched[2] == "LE" else a > b
        i = 0 if hold else 1
    if procs[i].frontier:
        return i
    for j in range(len(procs)):                  # fall through to a non-empty frontier
        if procs[j].frontier:
            return j
    return None


def run_stage(ad, stage, frm, to, trace):
    """Execute one STAGE program between terminals (frm, to). Returns word or None."""
    _tag, specs, sched, halt = stage
    procs = [Process(frm if root == "A" else to, gen) for root, gen in specs]
    trace["spawned"] += len(specs)
    trace["gens"].update(gen for _r, gen in specs)
    trace["roots"].update(root for root, _g in specs)
    # meet-compatible pair, if the program built one
    fwd = next((p for p, (r, g) in zip(procs, specs) if r == "A" and g == "S"), None)
    bwd = next((p for p, (r, g) in zip(procs, specs) if r == "Z" and g == "P"), None)
    trace["_procs"] = list(zip(procs, specs))
    it = 0
    last = None
    while True:
        if ad.meter.ops > ad.meter.budget:
            trace["halt"] = "budget"
            return None
        i = _sched_pick(sched, procs, it)
        it += 1
        if i is None:
            trace["halt"] = "exhausted"
            return None
        if last is not None and i != last:
            trace["switches"] += 1
        last = i
        proc = procs[i]
        new = proc.expand(ad)
        trace["expansions"][i] = trace["expansions"].get(i, 0) + 1
        if ad.meter.ops > ad.meter.budget:       # strict: no goal credit past budget
            trace["halt"] = "budget"
            return None
        if halt in ("GOAL", "ANY"):
            spec = specs[i]
            if spec == ("A", "S") and to in proc.visited:
                w = proc.word_root_to(to)
                trace["verify_calls"] += 1
                if ad.verify(w, frm, to):
                    trace["halt"] = "goal_fwd"
                    return w
                trace["verify_failures"] += 1
            if spec == ("Z", "P") and frm in proc.visited:
                w = proc.word_to_root(frm)
                trace["verify_calls"] += 1
                if ad.verify(w, frm, to):
                    trace["halt"] = "goal_bwd"
                    return w
                trace["verify_failures"] += 1
        if halt in ("MEET", "ANY") and fwd is not None and bwd is not None \
                and proc in (fwd, bwd):
            other = bwd if proc is fwd else fwd
            for u in new:
                if u in other.visited:
                    if trace["meets_verified"] >= MEET_VERIFY_CAP:
                        break
                    trace["meets_verified"] += 1
                    trace["verify_calls"] += 1
                    w = fwd.word_root_to(u) + bwd.word_to_root(u)
                    if ad.verify(w, frm, to):
                        trace["halt"] = "meet"
                        return w
                    trace["verify_failures"] += 1


def new_trace():
    return {"spawned": 0, "gens": set(), "roots": set(), "expansions": {},
            "switches": 0, "meets_verified": 0, "verify_calls": 0,
            "verify_failures": 0, "halt": None}


AUDIT_SAMPLE = 50


def audit_backward(trace, ad):
    """Post-run executable failure analysis: replay a sample of claimed backward
    edges (apply(pid, state) must reproduce the recorded parent). Metered. Returns
    the number of inconsistent edges found. Zero when predecessor information is
    truthful; the learner uses this as failure evidence, never a world label."""
    bad = checked = 0
    for proc, (root, gen) in trace.get("_procs", []):
        if gen != "P":
            continue
        for state, link in proc.visited.items():
            if link is None:
                continue
            prev, pid = link
            ad.meter.charge(1)
            if ad._apply(pid, state) != prev:
                bad += 1
            checked += 1
            if checked >= AUDIT_SAMPLE:
                return bad, checked
    return bad, checked


class MacroAdapter(Adapter):
    """Adapter for the v1-macro control (A1): the successor relation is augmented with
    one mined macro edge whose execution is charged at its true primitive length."""

    def __init__(self, domain, task, meter, macro):
        super().__init__(domain, task, meter)
        self._macro = tuple(macro)
        self._dapply = domain.apply

    def succ(self, s):
        r = self._succ(s)
        self.meter.charge(len(r))
        v = s
        for pid in self._macro:
            self.meter.charge(1)
            v = self._dapply(pid, v)
        return list(r) + [(self._macro, v)]


def run_program(domain, task, prog, budget, audit=False, meter=None, adapter=None):
    """Execute a full program (STAGE or SEQ) on a task. Returns result record.
    A pre-charged meter may be supplied (routing wrappers pay for their probes);
    a custom adapter may be supplied (the macro control)."""
    meter = meter if meter is not None else Meter(budget)
    ad = adapter if adapter is not None else Adapter(domain, task, meter)
    trace = new_trace()
    trace["_audit"] = audit
    if prog[0] == "SEQ":
        if ad.via is None:
            trace["halt"] = "illtyped"
            return _result(None, meter, trace, ad)
        w1 = run_stage(ad, prog[1], ad.start, ad.via, trace)
        if w1 is None:
            return _result(None, meter, trace, ad)
        w2 = run_stage(ad, prog[2], ad.via, ad.target, trace)
        if w2 is None:
            return _result(None, meter, trace, ad)
        return _result(list(w1) + list(w2), meter, trace, ad)
    word = run_stage(ad, prog, ad.start, ad.target, trace)
    return _result(word, meter, trace, ad)


def _result(word, meter, trace, ad):
    solved = word is not None
    if trace.pop("_audit", False):
        bad, checked = audit_backward(trace, ad)
        trace["bwd_inconsistent"] = bad
        trace["bwd_audited"] = checked
    trace.pop("_procs", None)
    if solved and ad.via is not None:            # final via check, metered
        s = ad.start
        hit = s == ad.via
        for pid in word:
            meter.charge(1)
            s = ad._apply(pid, s)
            if s == ad.via:
                hit = True
        solved = hit and s == ad.target
    t = dict(trace)
    t["gens"] = sorted(t["gens"])
    t["roots"] = sorted(t["roots"])
    return {"solved": solved, "word": list(word) if word else None,
            "ops": meter.ops, "budget": meter.budget,
            "budget_exhausted": trace["halt"] == "budget", "trace": t}
