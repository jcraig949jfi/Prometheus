"""Ergon Gen-1 -- Precondition A: library persistence. OBSERVATIONAL ONLY.

DESIGN COMMITMENT (brief section 3): this module does not import, wrap, patch,
subclass or otherwise touch agent_d5_blind/learner/m1.py. It observes objects
the frozen learner ALREADY returns (res['scored'], res['solver']) and the
library list the frozen driver ALREADY owns. Admission, eviction, ordering,
mutation, candidate evaluation, library lookup, random draws, budget and
timing-sensitive search semantics are therefore untouched BY CONSTRUCTION, not
by promise. Section 4A parity is still measured, because a claim that has never
been tested is not evidence.

ORACLE BOUNDARY (brief section 13 / 4C). Persisted rows carry ONLY information
the learner itself computes or holds:
  genotype .............. the learner's own object
  score d ............... FastTask distance, computed by the learner in ctx.d
  behavior fingerprint .. FastTask.outputs, exactly what admissions() uses
  library order/size .... the learner's own list
Explicitly EXCLUDED, though present in the oracle-side evidence ledger:
  witness / wlen ........ constructive-compiler output  (oracle)
  stratum ............... difficulty label              (oracle)
  reachability status ... reachability oracle           (oracle)
  solved / first_solve .. outcome, unavailable at admission time
The exclusion is enforced mechanically by ORACLE_FORBIDDEN below and tested.
"""
import hashlib
import json

SCHEMA_VERSION = 'ergon-gen1-libpersist-v1'

# Field-name fragments that must NEVER appear in a persisted record, any depth.
ORACLE_FORBIDDEN = ('witness', 'wlen', 'stratum', 'reachable', 'reachability',
                    'path_len', 'expressibility', 'solved', 'first_solve',
                    'oracle', 'domain_size')


def genotype_hash(g):
    """Stable content hash of a genotype. Canonical JSON, no whitespace drift."""
    return hashlib.sha256(
        json.dumps(g, separators=(',', ':')).encode()
    ).hexdigest()[:16]


def _canon(g):
    """Genotype -> JSON-safe nested lists. Does not mutate the input."""
    return [list(instr) for instr in g]


class LibraryRecorder:
    """Pure observer. Every method takes objects the caller already has."""

    def __init__(self, run_id, lineage, policy='I0-current-d5'):
        self.run_id = run_id
        self.lineage = lineage
        self.policy = policy
        self.events = []
        self.final = []

    def observe_task(self, position, family, seed, nav_seed, library_before,
                     res, admitted, library_after, fingerprints, scores):
        """One task boundary. library_before/library_after are snapshots the
        caller took; admitted is the output of the frozen admissions()."""
        before_h = [genotype_hash(_canon(g)) for g in library_before]
        after_h = [genotype_hash(_canon(g)) for g in library_after]
        before_set = set(before_h)
        after_set = set(after_h)

        admissions_ev = []
        for rank, g in enumerate(admitted):
            cg = _canon(g)
            h = genotype_hash(cg)
            admissions_ev.append({
                'artifact_hash': h,
                'genotype': cg,
                'length': len(cg),
                # 'solver' vs behaviour-distinct is the frozen rule's own
                # branch, visible in admissions(); not an oracle field.
                'admission_reason': ('solver'
                                     if (res['solver'] is not None and rank == 0)
                                     else 'behavior_distinct_best'),
                'source_score': scores.get(h),
                'behavior_fingerprint': fingerprints.get(h),
                'readmission': h in before_set,
            })

        evicted = [h for h in before_h if h not in after_set]

        self.events.append({
            'schema': SCHEMA_VERSION,
            'run_id': self.run_id,
            'lineage': self.lineage,
            'policy': self.policy,
            'position': position,
            'family': family,
            'task_seed': seed,
            'nav_seed': nav_seed,
            'library_before': before_h,
            'library_before_size': len(before_h),
            'admissions': admissions_ev,
            'admission_count': len(admissions_ev),
            'evictions': evicted,
            'eviction_count': len(evicted),
            'library_after': after_h,
            'library_after_size': len(after_h),
        })

    def observe_final(self, library_final):
        """Terminal library, full genotypes, for exact reconstruction."""
        self.final = [{'position_in_library': i,
                       'artifact_hash': genotype_hash(_canon(g)),
                       'genotype': _canon(g)}
                      for i, g in enumerate(library_final)]

    def to_dict(self):
        return {'schema': SCHEMA_VERSION, 'run_id': self.run_id,
                'lineage': self.lineage, 'policy': self.policy,
                'events': self.events, 'final_library': self.final}

    def write(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=1)
            f.flush()
        return path


def reconstruct_library(record):
    """Round-trip (brief 4B): rebuild the exact ordered genotype library from a
    persisted record, using ONLY the record. Non-scientific reconstruction
    tool: it imports nothing from the learner and re-runs no search."""
    if isinstance(record, str):
        with open(record, encoding='utf-8') as f:
            record = json.load(f)
    out = []
    for entry in sorted(record['final_library'],
                        key=lambda e: e['position_in_library']):
        g = tuple(tuple(i) for i in entry['genotype'])
        if genotype_hash(_canon(g)) != entry['artifact_hash']:
            raise ValueError(
                'hash mismatch at %s' % entry['position_in_library'])
        out.append(g)
    return out


def scan_oracle_leakage(record):
    """Brief 4C. Walks the whole record and returns every forbidden key found.
    A lookup that finds nothing must be distinguishable from a lookup that was
    never performed, so this also returns the number of nodes inspected and
    raises on a vacuous scan (ATK-013)."""
    if isinstance(record, str):
        with open(record, encoding='utf-8') as f:
            record = json.load(f)
    # ATK-013. The first version of this guard counted the ROOT node, so
    # seen==1 for any input and scan_oracle_leakage(None) returned a green
    # 'no forbidden fields' verdict over a non-record. Caught by
    # test_leakage_scan_refuses_to_pass_vacuously. The shape is checked first,
    # so a scan of the wrong object raises instead of rendering clean.
    if not isinstance(record, dict):
        raise ValueError('leakage scan requires a record dict, got %s'
                         % type(record).__name__)
    for required in ('events', 'final_library'):
        if required not in record:
            raise ValueError('leakage scan: record has no %r -- refusing a '
                             'vacuous pass' % required)
    hits = []
    seen = [0]

    def walk(node, path):
        seen[0] += 1
        if isinstance(node, dict):
            for k, v in node.items():
                if any(bad in str(k).lower() for bad in ORACLE_FORBIDDEN):
                    hits.append('%s.%s' % (path, k))
                walk(v, '%s.%s' % (path, k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, '%s[%d]' % (path, i))

    walk(record, '$')
    if seen[0] <= 1:
        raise ValueError('leakage scan descended into nothing -- vacuous pass')
    return {'forbidden_fields_found': hits, 'nodes_inspected': seen[0]}
