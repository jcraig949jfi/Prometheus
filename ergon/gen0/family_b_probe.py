"""ERGON GEN-0 / section 9 — the smallest Family-B probe that can decide anything.

Question the brief sets: does equivalence/rewrite structure produced from prior
experience alter future search or reachability? And, if that is not measurable with
egglog alone, record FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER.

Lexis G3 is inherited verbatim and binds the ORDER of work: "state the attainable
range of the readout first." Apollo's battery was disqualified as a G3 substrate by
exactly this rule, having been proved bounded at zero. So before any egglog design,
this probe measures the attainable range of an equational rewriter over RM-D5.

THE STRUCTURAL CONSTRAINT. egglog does equality saturation over TERMS. An RM
genotype is an imperative instruction sequence, and three of its fourteen opcodes
are control flow -- JNZ (backward jump), SKZ and SKG (conditional skips). A
straight-line, jump-free genotype IS a composable state transformer and is
expressible equationally. A genotype containing control flow is not, without
modelling the machine's whole state-transition relation as a theory.

So the attainable range of "egglog alone" is bounded by the jump-free fraction of
the substrate's solution corpus. This probe measures it.

CORPUS NOTE, and it is a constraint not a convenience. The only persisted genotype
corpus in D-5 is results/oracle_solutions.jsonl -- exact-oracle witnesses, which
consumer_fit.py records as INADMISSIBLE as library seeds (inference privilege). They
are used here for a STRUCTURAL CENSUS only: counting which opcodes appear in known
solutions is a property of the substrate, not information handed to a searcher. No
artifact from this file may seed any arm.

Run:  python -m ergon.gen0.family_b_probe
"""
import json
import os
import sys

D5 = os.path.join(os.path.dirname(__file__), '..', '..', 'agent_d5_blind')
sys.path.insert(0, os.path.abspath(os.path.join(D5, 'substrate')))
from rm_vm import OPS, OP_LIST   # noqa: E402

CONTROL_FLOW = {'JNZ', 'SKZ', 'SKG'}
EQUATIONAL = sorted(set(OP_LIST) - CONTROL_FLOW)


def egglog_available():
    try:
        import egglog  # noqa: F401
        return True, getattr(__import__('egglog'), '__version__', 'unknown')
    except Exception as exc:
        return False, str(exc)


def load_witnesses():
    path = os.path.abspath(os.path.join(D5, 'results', 'oracle_solutions.jsonl'))
    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    out = []
    for r in rows:
        w = r.get('witness')
        if w:
            out.append((r['key'], tuple(tuple(i) for i in w)))
    return out


def census():
    """Attainable range of an equational rewriter over the known solution corpus."""
    ws = load_witnesses()
    jump_free, with_cf = [], []
    op_counts, cf_counts = {}, {}
    for key, w in ws:
        ops = {ins[0] for ins in w}
        for o in ops:
            op_counts[o] = op_counts.get(o, 0) + 1
        hit = ops & CONTROL_FLOW
        if hit:
            with_cf.append((key, sorted(hit)))
            for o in hit:
                cf_counts[o] = cf_counts.get(o, 0) + 1
        else:
            jump_free.append(key)
    n = len(ws)
    by_family = {}
    for key, w in ws:
        fam = key.split(':')[0]
        ops = {ins[0] for ins in w}
        d = by_family.setdefault(fam, {'n': 0, 'jump_free': 0})
        d['n'] += 1
        d['jump_free'] += 0 if (ops & CONTROL_FLOW) else 1
    return {
        'n_witnesses': n,
        'n_jump_free': len(jump_free),
        'n_with_control_flow': len(with_cf),
        'jump_free_fraction': round(len(jump_free) / n, 4) if n else None,
        'control_flow_opcode_counts': cf_counts,
        'opcode_appearance_counts': dict(sorted(op_counts.items())),
        'equational_fragment': EQUATIONAL,
        'control_flow_opcodes': sorted(CONTROL_FLOW),
        'by_family': by_family,
        'witness_len_mean': round(sum(len(w) for _, w in ws) / n, 2) if n else None,
    }


def verdict(c, egglog_ok):
    """The decision the brief asks for, stated against the measured range."""
    frac = c['jump_free_fraction']
    lines = []
    if not egglog_ok:
        return 'FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER', [
            'egglog does not import in this interpreter; nothing is measurable today']

    lines.append(
        'egglog imports, so the tool is present. The binding constraint is not the '
        'tool, it is the SUBSTRATE ENCODING.')
    lines.append(
        'Attainable range, measured: %d of %d known solution witnesses (%.1f%%) are '
        'jump-free and therefore expressible as equational terms; %d contain control '
        'flow %s and are not, absent a machine-state theory.'
        % (c['n_jump_free'], c['n_witnesses'], 100 * frac,
           c['n_with_control_flow'], sorted(c['control_flow_opcode_counts'])))

    lines.append(
        'But coverage of the corpus is NOT the readout. The Gen-0 question is whether '
        'rewrite structure alters FUTURE SEARCH in the D-5 consumer, and consumer_fit '
        'establishes that the only thing the slot eats is a whole genotype used as a '
        'mutation seed. An equality-saturation engine returns a set of terms EQUIVALENT '
        'to its input. Equivalent genotypes compute the same function, so seeding the '
        'library with them adds no behaviour the library did not already have -- and '
        'D-5 admission is already behaviour-distinct-deduplicated (m1.admissions uses '
        'ft.outputs fingerprints).')
    lines.append(
        'So egglog alone can produce, at best, behaviourally redundant seeds for a slot '
        'that already de-duplicates on behaviour. That is measurable-in-principle and '
        'predictably null; it is not the Family-B hypothesis. The real Family-B claim -- '
        'that rewrite structure makes solutions CHEAPER TO REACH -- needs a rewriter '
        'that shortens or re-parameterises search, i.e. Ruler/babble/Enumo-style '
        'synthesis over a theory that includes RM control flow. That layer is unbuilt.')
    return 'FAMILY_B_REQUIRES_NEW_SYNTHESIS_LAYER', lines


def requirement(c):
    """Section 9: if a real effect is not reachable, write the precise requirement for
    the smallest next Family-B capability. Stated so a successor can build exactly it."""
    return {
        'smallest_next_capability': (
            'an equational theory of RM-D5 over the JUMP-FREE fragment (%d opcodes: %s) '
            'that can (a) ingest a straight-line genotype, (b) saturate under a rule set '
            'derived from prior solved genotypes, and (c) emit the SHORTEST equivalent '
            'straight-line genotype.' % (len(EQUATIONAL), ' '.join(EQUATIONAL))),
        'why_shortest_is_the_right_output': (
            'length is the only rewrite product that can move the D-5 readout. The slot '
            'eats whole genotypes as mutation seeds; a shorter seed of identical '
            'behaviour occupies a different, smaller neighbourhood under the frozen '
            'mutation physics, so it is a REACHABILITY claim rather than an equivalence '
            'claim, and reachability is what D-5 measures.'),
        'preregistered_kill': (
            'if shortest-equivalent seeds do not change per-task CFR against a '
            'length-matched random-genotype control at identical metered budget, '
            'Family B is dead for this consumer regardless of how elegant its '
            'equivalence classes are.'),
        'attainable_range_first': (
            'before that build, compute the length reduction available on the jump-free '
            'fragment. If mean shortest-equivalent length equals mean witness length, '
            'the readout is bounded at zero and the build is disqualified exactly as '
            "Lexis G3 disqualified Apollo's battery."),
        'blocked_on': (
            'nothing external. This is a build, not an acquisition, and it needs no '
            'donor licence question resolved.'),
    }


def main():
    ok, ver = egglog_available()
    print('ERGON GEN-0 -- FAMILY B PROBE (section 9)')
    print('=' * 68)
    print('\n[TOOL] egglog importable: %s (%s)' % (ok, ver))

    c = census()
    print('\n[G3 ATTAINABLE RANGE] measured before any design, per inherited Lexis G3')
    print('  witnesses ................. %d  (mean length %.2f)'
          % (c['n_witnesses'], c['witness_len_mean']))
    print('  jump-free (equational) .... %d  (%.1f%%)'
          % (c['n_jump_free'], 100 * c['jump_free_fraction']))
    print('  with control flow ......... %d  %s'
          % (c['n_with_control_flow'], c['control_flow_opcode_counts']))
    print('  equational fragment ....... %d opcodes: %s'
          % (len(EQUATIONAL), ' '.join(EQUATIONAL)))
    print('  by family (jump_free/n) ... %s'
          % {k: '%d/%d' % (v['jump_free'], v['n']) for k, v in sorted(c['by_family'].items())})

    v, why = verdict(c, ok)
    print('\n[VERDICT] %s' % v)
    for line in why:
        print('  - %s' % line)

    req = requirement(c)
    print('\n[REQUIREMENT FOR THE SMALLEST NEXT FAMILY-B CAPABILITY]')
    for k in ('smallest_next_capability', 'why_shortest_is_the_right_output',
              'preregistered_kill', 'attainable_range_first'):
        print('  %s:\n    %s' % (k, req[k]))

    out = os.path.join(os.path.dirname(__file__), 'family_b_probe_2026-08-31.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'egglog_available': ok, 'egglog_version': ver, 'census': c,
                   'verdict': v, 'reasoning': why, 'requirement': req},
                  fh, indent=2, sort_keys=True)
    print('\nwrote %s' % out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
