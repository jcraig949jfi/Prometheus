"""Ergon Gen-1: import shim for the frozen D-5 tree.

Read-only. Adds the D-5 package directories to sys.path exactly as the frozen
runners do, so replay imports the SAME modules the evidence run imported.
Nothing in agent_d5_blind/ is modified by importing this.
"""
import sys, os

D5 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                  'agent_d5_blind'))
_SUBDIRS = ('task_generators', 'substrate', 'mutation', 'exact_oracle',
            'learner', 'navigators', 'reachability_oracle',
            'developmental_history')

for _d in _SUBDIRS:
    _p = os.path.join(D5, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

RESULTS = os.path.join(D5, 'results')
LEDGERS = os.path.join(D5, 'ledgers')
FINAL_LIBS = os.path.join(D5, 'developmental_history', 'final_libraries')
