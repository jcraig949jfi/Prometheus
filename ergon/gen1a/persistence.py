"""ERGON GEN-1A / section 6 -- the persistence instrument.

Records every library event in a D-5 M1 lineage WITHOUT altering search
semantics, and serialises the result so a library state can be reconstructed
exactly.

WHY THIS SHAPE. The brief requires persistence to be OBSERVATIONAL ONLY: it
must not alter admission, eviction, ordering, mutation, candidate evaluation,
library lookup, random draws, budget, or timing-sensitive semantics. The
temptation is to fork m1_rx and add hooks. That would fork the frozen search
core, and a forked core cannot be shown identical to the one that produced
+10.95pp.

Instead the instrument exploits the fact that the frozen core touches the
library through exactly two surfaces:

    m1_rx.fresh():      extra_pool[rng.randrange(len(extra_pool))]
    m1.update_library:  admission and most-recent-first eviction

So a list SUBCLASS that overrides __getitem__ observes every draw, and a
wrapper around update_library observes every admission and eviction. Neither
consumes randomness, neither changes control flow, and the frozen m1.py is
imported unmodified. Behaviour is identical BY CONSTRUCTION, and section 4A
parity then tests that claim rather than assuming it.

Fingerprints are computed with FastTask.outputs, which the frozen
m1.admissions already uses and which m1.py's own docstring designates as
"pure bookkeeping (fingerprints allowed)". No evaluation counter is touched.

Run:  python -m ergon.gen1a.persistence --selftest
"""
import hashlib
import json
import os
import sys

D5 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                  'agent_d5_blind'))
for _s in ('task_generators', 'substrate', 'mutation', 'exact_oracle',
           'learner', 'navigators'):
    _p = os.path.join(D5, _s)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import m1 as M1                     # noqa: E402  frozen learner, unmodified
from rm_fast import FastTask        # noqa: E402

SCHEMA_VERSION = 'ergon-gen1a-lib-1'


def artifact_hash(genotype):
    """Stable identity for a genotype. Order- and type-sensitive by design:
    ('SET',0,1) and ('SET',0,2) must not collide."""
    payload = json.dumps([list(i) for i in genotype], separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


def genotype_from_json(obj):
    return tuple(tuple(i) for i in obj)


def genotype_to_json(g):
    return [list(i) for i in g]


class RecordingLibrary(list):
    """A list that records every read the frozen search core performs.

    __getitem__ is the ONLY way m1_rx reads the library. Overriding it captures
    every draw without touching rng, budget or control flow. len() is left
    alone: it is called on the same schedule regardless.
    """

    def __init__(self, iterable=()):
        super().__init__(iterable)
        self.draws = []          # (task_index, position_drawn, artifact_hash)
        self._task_index = 0

    def set_task(self, i):
        self._task_index = i

    def __getitem__(self, idx):
        item = super().__getitem__(idx)
        if isinstance(idx, int):
            self.draws.append((self._task_index, idx, artifact_hash(item)))
        return item


class LibraryRecorder:
    """Owns the recording library and the event log for one lineage."""

    def __init__(self, run_id, lineage, policy='D5_BASELINE_MRU'):
        self.run_id = run_id
        self.lineage = lineage
        self.policy = policy
        self.library = RecordingLibrary()
        self.events = []
        self.task_index = 0
        self._admitted_at = {}     # hash -> task index of most recent admission

    # -- observational hooks -------------------------------------------------

    def begin_task(self, family, seed):
        self.library.set_task(self.task_index)
        self.events.append({'ev': 'task_begin', 'i': self.task_index,
                            'family': family, 'seed': seed,
                            'library_size_at_start': len(self.library)})

    def record_admissions(self, new_genotypes, view):
        """Wraps m1.update_library. Calls the FROZEN function for the actual
        mutation of the library, then diffs to recover evictions. The frozen
        function is the authority; this never reimplements its semantics."""
        before = list(self.library)
        before_set = {artifact_hash(g) for g in before}

        ft = FastTask(view)
        for g in new_genotypes:
            h = artifact_hash(g)
            self.events.append({
                'ev': 'admit', 'i': self.task_index, 'hash': h,
                'genotype': genotype_to_json(g), 'len': len(g),
                'fingerprint': [int(x) for x in ft.outputs(g)],
                'readmission': h in before_set,
            })
            self._admitted_at[h] = self.task_index

        M1.update_library(self.library, new_genotypes)   # frozen semantics

        after_set = {artifact_hash(g) for g in self.library}
        for g in before:
            h = artifact_hash(g)
            if h not in after_set:
                self.events.append({
                    'ev': 'evict', 'i': self.task_index, 'hash': h,
                    'reason': 'cap_mru', 'policy': self.policy,
                    'residence_tasks': self.task_index - self._admitted_at.get(h, 0),
                })
        self.task_index += 1

    # -- serialisation -------------------------------------------------------

    def snapshot(self):
        entries = [{'pos': i, 'hash': artifact_hash(g),
                    'genotype': genotype_to_json(g)}
                   for i, g in enumerate(self.library)]
        body = {'schema': SCHEMA_VERSION, 'run_id': self.run_id,
                'lineage': self.lineage, 'policy': self.policy,
                'task_index': self.task_index, 'size': len(self.library),
                'entries': entries}
        body['state_hash'] = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(',', ':'))
            .encode('utf-8')).hexdigest()
        return body

    def draw_counts(self):
        c = {}
        for _i, _pos, h in self.library.draws:
            c[h] = c.get(h, 0) + 1
        return c

    def write(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        base = 'lineage_%s' % self.lineage
        snap = self.snapshot()
        _atomic_write(os.path.join(out_dir, base + '_final_library.json'),
                      json.dumps(snap, indent=2, sort_keys=True))
        with open(os.path.join(out_dir, base + '_events.jsonl'), 'w',
                  encoding='utf-8') as fh:
            for e in self.events:
                fh.write(json.dumps(e, sort_keys=True) + '\n')
        with open(os.path.join(out_dir, base + '_draws.jsonl'), 'w',
                  encoding='utf-8') as fh:
            for i, pos, h in self.library.draws:
                fh.write(json.dumps({'i': i, 'pos': pos, 'hash': h}) + '\n')
        return snap['state_hash']


def _atomic_write(path, text):
    """Fail closed on partial writes: write to a temp file, fsync, rename."""
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def load_snapshot(path):
    """Reload a persisted library. Fails closed on any integrity violation."""
    with open(path, encoding='utf-8') as fh:
        body = json.load(fh)
    claimed = body.pop('state_hash', None)
    recomputed = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(',', ':'))
        .encode('utf-8')).hexdigest()
    if claimed != recomputed:
        raise ValueError('state_hash mismatch: snapshot corrupt or edited')
    if body.get('schema') != SCHEMA_VERSION:
        raise ValueError('unknown schema %r' % body.get('schema'))
    entries = body['entries']
    if [e['pos'] for e in entries] != list(range(len(entries))):
        raise ValueError('entry positions are not a contiguous 0..n-1 ordering')
    if len(entries) != body['size']:
        raise ValueError('size field disagrees with entry count')
    seen = set()
    lib = []
    for e in entries:
        g = genotype_from_json(e['genotype'])
        h = artifact_hash(g)
        if h != e['hash']:
            raise ValueError('artifact hash mismatch at pos %d' % e['pos'])
        if h in seen:
            raise ValueError('duplicate artifact at pos %d' % e['pos'])
        seen.add(h)
        for op, a, b in g:
            if op not in __import__('rm_vm').OPS:
                raise ValueError('unknown opcode %r' % op)
        lib.append(g)
    return lib, body
