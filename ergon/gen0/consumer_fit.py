"""ERGON GEN-0 / section 4 — legitimate consumer fit for the D-5 library slot.

Answers, by EXECUTION rather than by argument, the question the Gen-0 brief puts
before any benchmark: can a candidate artifact enter the D-5 library slot WITHOUT
changing the consumer's scientific meaning?

Classification vocabulary is the brief's:
    CONSUMABLE_AS_IS
    CONSUMABLE_WITH_SEMANTICS_PRESERVING_ADAPTER
    NOT_CONSUMABLE
    TOOL_FIT_FAILURE

READ-ONLY with respect to agent_d5_blind/. Nothing there is written, mutated or
rerun; the frozen modules are imported to read their contract.

WHY A PROBE AND NOT A PARAGRAPH. Ergon doctrine: a check that has never been shown
to fail is not evidence, it is an untested function whose return value happens to be
True. So every classification below is produced by the same function, and section
GATE-FIRE runs it against constructed worlds whose answers are known in advance --
including the two answers this seat least wants, namely a spurious NOT_CONSUMABLE on
an artifact that genuinely fits.

Run:  python -m ergon.gen0.consumer_fit
"""
import json
import os
import random
import sys

D5 = os.path.join(os.path.dirname(__file__), '..', '..', 'agent_d5_blind')
for _sub in ('substrate', 'mutation', 'learner'):
    sys.path.insert(0, os.path.abspath(os.path.join(D5, _sub)))

from rm_vm import OPS, OP_LIST, NREG, MAX_LEN, PALETTE, run   # noqa: E402
from physics import mutate                                    # noqa: E402
import m1                                                     # noqa: E402

CONSUMABLE = 'CONSUMABLE_AS_IS'
ADAPTER = 'CONSUMABLE_WITH_SEMANTICS_PRESERVING_ADAPTER'
NOT_CONSUMABLE = 'NOT_CONSUMABLE'
TOOL_FIT_FAILURE = 'TOOL_FIT_FAILURE'

#: A hole in a library-learning abstraction. Stitch's product is a lambda with
#: variables; this marker stands for one argument position awaiting application.
HOLE = '#HOLE'


# ---------------------------------------------------------------- the contract

def valid_genotype(g):
    """The D-5 library-entry contract, read from the frozen source.

    m1.update_library stores whatever it is given; the binding constraint is that
    the entry must survive m1.m1_rx's ONLY use of it -- mutate(entry, rng) -- and
    the result must be executable by rm_vm.run. So validity is exactly: a nonempty
    tuple of (opcode, reg, typed-b) triples within MAX_LEN.
    """
    if not isinstance(g, tuple) or not (1 <= len(g) <= MAX_LEN):
        return False, 'not a 1..%d tuple of instructions' % MAX_LEN
    for ins in g:
        if not isinstance(ins, tuple) or len(ins) != 3:
            return False, 'instruction is not a 3-tuple: %r' % (ins,)
        op, a, b = ins
        if op not in OPS:
            return False, 'opcode %r not in the frozen set of %d' % (op, len(OP_LIST))
        if not isinstance(a, int) or isinstance(a, bool) or not (0 <= a < NREG):
            return False, 'register operand %r invalid' % (a,)
        if not isinstance(b, int) or isinstance(b, bool):
            return False, 'b operand %r is not an int (a hole cannot be stored)' % (b,)
        kind = OPS[op]
        if kind == 'reg' and not (0 <= b < NREG):
            return False, 'b out of register range'
        if kind == 'const' and not (0 <= b < len(PALETTE)):
            return False, 'b out of palette range'
        if kind == 'jump' and not (1 <= b <= 8):
            return False, 'b out of jump range'
    return True, 'ok'


def has_holes(artifact):
    """True if the artifact carries an unapplied argument position."""
    if not isinstance(artifact, tuple):
        return False
    for ins in artifact:
        if isinstance(ins, tuple) and any(x == HOLE for x in ins):
            return True
    return False


def needs_new_opcode(artifact):
    """The set of opcodes an artifact uses that the frozen VM does not implement."""
    out = set()
    if not isinstance(artifact, tuple):
        return out
    for ins in artifact:
        if isinstance(ins, tuple) and len(ins) == 3 and ins[0] not in OPS:
            if isinstance(ins[0], str):
                out.add(ins[0])
    return out


# ---------------------------------------------------------------- the slot itself

def slot_roundtrip(g, seed=0, trials=32):
    """Push a candidate through the slot's ACTUAL consumption path and report.

    m1.m1_rx's whole use of the library is:
        if extra_pool and rng.random() < 0.5:
            return mutate(extra_pool[rng.randrange(len(extra_pool))], rng)
    i.e. a whole-program mutation seed. This reproduces that path exactly, without
    importing the learner's search, and confirms the product is executable.
    """
    rng = random.Random(seed)
    lib = m1.update_library([], [g])
    if list(lib) != [g]:
        return False, 'update_library did not retain the artifact verbatim'
    for _ in range(trials):
        child = mutate(lib[0], rng)
        ok, why = valid_genotype(child)
        if not ok:
            return False, 'mutate produced an invalid child: %s' % why
        run(child, (1, 0))
    return True, 'seeded, mutated %d times, all children executable' % trials


def primitive_extension_path():
    """Is there ANY way to add a new primitive to the consumer?

    This is the structural question for Family A. A library-learning system's
    product is a new reusable PRIMITIVE that shortens programs and therefore
    shortens search paths. D-5's opcode set is computed at import from a literal
    dict and dispatched by a hardcoded if/elif chain in rm_vm.run.
    """
    hooks = [n for n in dir(m1) if 'regist' in n.lower() or 'add_op' in n.lower()]
    import rm_vm
    vm_hooks = [n for n in dir(rm_vm) if 'regist' in n.lower() or 'add_op' in n.lower()]
    return {
        'n_opcodes': len(OP_LIST),
        'opcodes': list(OP_LIST),
        'op_list_is_derived_from_literal_dict': OP_LIST == sorted(OPS),
        'registration_hooks_in_learner': hooks,
        'registration_hooks_in_vm': vm_hooks,
        'extension_path_exists': bool(hooks or vm_hooks),
    }


# ---------------------------------------------------------------- classification

def classify(artifact, label=''):
    """The single classification function. Every verdict in this file comes from
    here, including the gate-fire worlds."""
    missing = needs_new_opcode(artifact)
    if missing:
        ext = primitive_extension_path()
        if not ext['extension_path_exists']:
            return TOOL_FIT_FAILURE, (
                'artifact requires opcode(s) %s; the consumer has %d frozen opcodes '
                'and no registration hook in the learner or the VM, so a learned '
                'primitive has no slot to enter' % (sorted(missing), ext['n_opcodes']))
        return ADAPTER, 'new opcode required but an extension path exists'

    if has_holes(artifact):
        return NOT_CONSUMABLE, (
            'artifact carries unapplied argument positions. The slot consumes '
            'entries ONLY as whole-program mutation seeds (m1.m1_rx.fresh); there is '
            'no application, instantiation or splice site anywhere in the frozen '
            'search core, so an abstraction cannot be stored or used as an '
            'abstraction. Instantiating its holes would store a CONCRETE genotype, '
            'which changes what is being tested rather than adapting it')

    ok, why = valid_genotype(artifact)
    if not ok:
        return NOT_CONSUMABLE, 'fails the library-entry contract: %s' % why

    ok2, why2 = slot_roundtrip(artifact)
    if not ok2:
        return NOT_CONSUMABLE, 'fails the live slot round-trip: %s' % why2
    return CONSUMABLE, why2


# ---------------------------------------------------------------- gate-fire

def gate_fire():
    """Constructed worlds whose classification is known BEFORE the probe runs.

    W1 and W2 are the answers this seat least wants to get wrong: a probe that is
    merely biased toward NOT_CONSUMABLE would report the Gen-0 headline for free.
    """
    native = (('SET', 1, 8), ('OR', 0, 1), ('SET', 1, 6), ('XOR', 0, 1))
    zero_hole_motif = (('SET', 1, 1), ('SHR', 0, 1))
    holed = (('SET', 1, HOLE), ('OR', 0, 1))
    new_prim = (('DOUBLE_AND_MASK', 0, 1), ('OR', 0, 1))
    malformed_float = (('SET', 0, 1.5),)
    malformed_const = (('SET', 0, 99),)
    too_long = tuple([('MOV', 0, 0)] * (MAX_LEN + 1))

    worlds = [
        ('W1 native D-5 genotype', native, CONSUMABLE),
        ('W2 zero-hole motif (a fair Stitch degenerate case)', zero_hole_motif, CONSUMABLE),
        ('W3 abstraction WITH a hole (Stitch proper)', holed, NOT_CONSUMABLE),
        ('W4 artifact needing a learned primitive', new_prim, TOOL_FIT_FAILURE),
        ('W5 malformed: float operand', malformed_float, NOT_CONSUMABLE),
        ('W6 malformed: const index out of palette', malformed_const, NOT_CONSUMABLE),
        ('W7 over-length genotype', too_long, NOT_CONSUMABLE),
    ]
    rows, holes = [], 0
    for name, art, expected in worlds:
        got, why = classify(art, name)
        ok = (got == expected)
        holes += (0 if ok else 1)
        rows.append({'world': name, 'expected': expected, 'got': got,
                     'pass': ok, 'reason': why})
    return rows, holes


# ---------------------------------------------------------------- inference privilege

def inference_privilege_audit():
    """The only persisted genotype corpus in D-5, and whether it may seed a library."""
    path = os.path.abspath(os.path.join(D5, 'results', 'oracle_solutions.jsonl'))
    if not os.path.exists(path):
        return {'corpus_present': False}
    rows = [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]
    methods = sorted({r.get('method') for r in rows})
    return {
        'corpus_present': True,
        'path': 'agent_d5_blind/results/oracle_solutions.jsonl',
        'n': len(rows),
        'methods': methods,
        'oracle_side': True,
        'admissible_as_library_seed': False,
        'reason': (
            'these are exact-oracle witnesses produced by the constructive '
            'compiler, not artifacts the searcher found. m1.py states its input '
            'boundary as the learner view only; seeding the library from them '
            'hands the searcher answers it is being measured for finding, and '
            'the Gen-0 brief requires identical inference privilege across arms'),
    }


def search_discovered_corpus_audit():
    """Was any search-discovered artifact library persisted by D-5?"""
    led = os.path.abspath(os.path.join(D5, 'ledgers', 'm1_rows.jsonl'))
    rows = [json.loads(l) for l in open(led, encoding='utf-8') if l.strip()]
    keys = sorted(rows[0].keys())
    carries = [k for k in keys if 'geno' in k.lower() or 'solver' in k.lower()
               or 'artifact' in k.lower() or 'library_contents' in k.lower()]
    return {
        'ledger': 'agent_d5_blind/ledgers/m1_rows.jsonl',
        'n_rows': len(rows),
        'fields': keys,
        'genotype_bearing_fields': carries,
        'search_discovered_library_persisted': bool(carries),
        'note': ('m1.py builds the library in memory across a lineage and the row '
                 'writer records only library_size_at_start plus outcome metadata. '
                 'The libraries that produced the +10.95pp result were not saved.'),
    }


def main():
    print('ERGON GEN-0 -- D-5 LIBRARY SLOT CONSUMER FIT')
    print('=' * 68)

    ext = primitive_extension_path()
    print('\n[SLOT] frozen opcodes: %d %s' % (ext['n_opcodes'], ext['opcodes']))
    print('[SLOT] primitive-extension path exists: %s  (learner hooks %s / vm hooks %s)'
          % (ext['extension_path_exists'], ext['registration_hooks_in_learner'],
             ext['registration_hooks_in_vm']))
    print('[SLOT] library consumption path: m1.m1_rx.fresh -> mutate(entry, rng); '
          'whole-program seed, no application/splice site')

    print('\n[GATE-FIRE] constructed worlds, answers known in advance')
    rows, holes = gate_fire()
    for r in rows:
        print('  [%s] %-52s %s' % ('PASS' if r['pass'] else 'HOLE',
                                   r['world'], r['got']))
    print('  --> %s (%d holes)' % ('NO HOLES' if holes == 0 else 'HOLES PRESENT', holes))

    print('\n[CANDIDATES] the three the brief names')
    cands = [
        ('A native D-5 executable artifact',
         (('SET', 1, 8), ('OR', 0, 1), ('SET', 1, 6), ('XOR', 0, 1))),
        ('B Stitch-derived abstraction (with holes, its actual product)',
         (('SET', 1, HOLE), ('OR', 0, 1))),
        ('B* Stitch-derived abstraction, degenerate zero-hole motif',
         (('SET', 1, 1), ('SHR', 0, 1))),
        ('C egglog-derived rewritten genotype (hypothetical, RM theory absent)',
         (('SET', 1, 1), ('ADD', 0, 1))),
    ]
    # TYPE-FIT is not PRODUCIBILITY. classify() answers only "would the slot eat
    # this object if handed it". Whether any donor can actually PRODUCE the object
    # is a separate question, and conflating the two is how a compatibility
    # statement gets read as a capability statement.
    producible = {
        'A native D-5 executable artifact': (
            'YES -- by the searcher itself; this is what m1.admissions already emits'),
        'B Stitch-derived abstraction (with holes, its actual product)': (
            'N/A -- type-rejected before producibility matters'),
        'B* Stitch-derived abstraction, degenerate zero-hole motif': (
            'YES, but a zero-hole abstraction is a concrete subprogram. Stitch would '
            'be functioning as a SELECTOR over native artifacts, not as a supplier of '
            'abstractions, and the arm would test the admission rule rather than Stitch'),
        'C egglog-derived rewritten genotype (hypothetical, RM theory absent)': (
            'NO, NOT TODAY -- this input was constructed by hand to test the TYPE. '
            'Producing it requires RM semantics (including JNZ/SKZ/SKG control flow) '
            'as an egglog theory; imperative sequences with jumps are not equational '
            'terms. That build is unstarted. The verdict below is about the type of '
            'the object, and is NOT evidence that egglog can emit one'),
    }
    verdicts = {}
    for name, art in cands:
        got, why = classify(art, name)
        verdicts[name] = {'classification': got, 'reason': why,
                          'producible_today': producible[name]}
        print('  %-62s %s' % (name, got))
        print('       producible today: %s' % producible[name].split(' -- ')[0])

    priv = inference_privilege_audit()
    corp = search_discovered_corpus_audit()
    print('\n[CORPUS] search-discovered library persisted: %s'
          % corp['search_discovered_library_persisted'])
    print('[CORPUS] only persisted genotypes: %s (n=%d, methods=%s) -- admissible as '
          'library seed: %s' % (priv.get('path'), priv.get('n', 0),
                                priv.get('methods'), priv['admissible_as_library_seed']))

    report = {
        'slot': ext,
        'gate_fire': {'rows': rows, 'holes': holes},
        'candidates': verdicts,
        'inference_privilege': priv,
        'search_discovered_corpus': corp,
    }
    out = os.path.join(os.path.dirname(__file__), 'consumer_fit_2026-08-31.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    print('\nwrote %s' % out)
    return 0 if holes == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
