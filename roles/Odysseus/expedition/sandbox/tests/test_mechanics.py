"""Mechanics + forbidden-information tests. Run: python3 -m unittest discover -s tests (from sandbox/)."""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import world as W  # noqa: E402


def fingerprint(st):
    return (st['gen'], [list(r) for r in st['record']], list(st['s']),
            [[o[0] for o in col] for col in st['colonies']])


class TestDeterminism(unittest.TestCase):
    def test_same_seed_same_trajectory(self):
        a = W.new_world(7); b = W.new_world(7)
        ta = W.run(a, 60); tb = W.run(b, 60)
        self.assertEqual(ta, tb)
        self.assertEqual(fingerprint(a), fingerprint(b))

    def test_snapshot_restore_replays_exactly(self):
        a = W.new_world(11)
        W.run(a, 30)
        snap = W.snapshot(a)
        t1 = W.run(a, 40)
        b = W.restore(snap)
        t2 = W.run(b, 40)
        self.assertEqual(t1, t2)
        self.assertEqual(fingerprint(a), fingerprint(b))


class TestForbiddenInformation(unittest.TestCase):
    def test_organism_code_references_only_arguments(self):
        # the organism functions may reference their arguments and the
        # module constant EXPLORE_LEVELS only: no world, rng, seed, ids, labels
        allowed_globals = {'EXPLORE_LEVELS'}
        for fn in (W.organism_choose, W.organism_write):
            co = fn.__code__
            self.assertTrue(set(co.co_names) <= allowed_globals, (fn.__name__, co.co_names))
            self.assertEqual(co.co_freevars, ())
        self.assertEqual(W.organism_choose.__code__.co_varnames[:4], ('genome', 'obs_idx', 'coin', 'rand_site'))
        self.assertEqual(W.organism_write.__code__.co_varnames[:4], ('genome', 'i_write', 'site', 'found'))

    def test_evaluator_state_poisoning_changes_nothing(self):
        # scramble every evaluator-side field and the founder/uid tags: the
        # physical trajectory must be identical
        a = W.new_world(3); W.run(a, 20)
        b = W.snapshot(a)
        b['ev']['wlog'] = [[[(0, 999, 999)] * 5 for _ in r] for r in b['ev']['wlog']]
        b['ev']['last_write'] = [[123456] * 2 for _ in b['ev']['last_write']]
        b['ev']['next_uid'] = 10 ** 9
        b['arm_label_poison'] = 'P_TREATMENT_SECRET'
        for col in b['colonies']:
            for o in col:
                o[1] = -5
        ta = W.run(a, 40); tb = W.run(b, 40)
        self.assertEqual(ta, tb)
        self.assertEqual(fingerprint(a), fingerprint(b))

    def test_no_lookahead(self):
        # changing the environment's FUTURE (from t on) cannot change anything
        # organisms did before t: behaviour through t depends only on the past
        a = W.new_world(5); W.run(a, 25)
        snap = W.snapshot(a)
        ta = W.run(a, 10)
        b = W.restore(snap)
        # rewrite the future: a different physics stream from generation 25+1 on
        tb = [W.step(b)]
        b['rng_phys'] = random.Random(424242)
        tb += W.run(b, 9)
        self.assertEqual(ta[0], tb[0])

    def test_hidden_state_not_in_observation(self):
        # two worlds identical except the hidden patch site: every organism's
        # CHOICE in the first generation is identical (choices can depend only on
        # the record, not on s); outcomes may differ
        p = W.DEFAULTS
        a = W.new_world(9); b = W.snapshot(a)
        b['s'] = [(x + 1) % p['S'] for x in b['s']]
        chosen = []
        for st in (a, b):
            rb = random.Random(1)
            nchoose, iw, iwr, L, R = W.layout(st['p'])
            ch = []
            for g, col in enumerate(st['colonies']):
                oi = W.obs_index(st['record'][g], p['A'])
                for o in col:
                    ch.append(W.organism_choose(o[0], oi if o[0][0] else 0, rb.random(), rb.randrange(4)))
            chosen.append(ch)
        self.assertEqual(chosen[0], chosen[1])

    def test_sigma_is_invisible_to_physics_costs(self):
        # sigma only relabels stored symbols; with no readers the energy
        # economy and success are identical under any sigma
        g = W.planted_genomes('N_a')
        a = W.new_world(4, {'planted': True}, g, [0, 1, 2, 3])
        b = W.new_world(4, {'planted': True}, g, [2, 0, 3, 1])
        self.assertEqual(W.run(a, 50), W.run(b, 50))


class TestModes(unittest.TestCase):
    def test_unreadable_reads_blank_but_writes_persist(self):
        st = W.new_world(2, {'record_mode': 'unreadable', 'planted': True}, W.planted_genomes('P'))
        W.run(st, 30)
        self.assertTrue(any(c != W.BLANK for r in st['record'] for c in r))

    def test_norecord_has_no_writes(self):
        st = W.new_world(2, {'record_mode': 'none', 'planted': True}, W.planted_genomes('P'))
        st['p']['eps'] = 0.0
        W.run(st, 30)
        self.assertTrue(all(c == W.BLANK for r in st['record'] for c in r))


if __name__ == '__main__':
    unittest.main()
