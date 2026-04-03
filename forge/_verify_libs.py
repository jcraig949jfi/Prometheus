"""Verify all 4 external libraries are installed and functional."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print('=== pgmpy ===')
from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
bn = BayesianNetwork([('A','C'),('B','C')])
print(f'  BayesianNetwork: nodes={list(bn.nodes())}')
print(f'  markov_blanket A: {bn.get_markov_blanket("A")}')
dsep = bn.minimal_dseparator('A', 'B')
print(f'  minimal_dseparator A-B: {dsep}')
# Test inference with CPDs
cpd_a = TabularCPD('A', 2, [[0.4], [0.6]])
cpd_b = TabularCPD('B', 2, [[0.5], [0.5]])
cpd_c = TabularCPD('C', 2, [[0.9, 0.7, 0.8, 0.1], [0.1, 0.3, 0.2, 0.9]], evidence=['A','B'], evidence_card=[2,2])
bn.add_cpds(cpd_a, cpd_b, cpd_c)
assert bn.check_model()
infer = VariableElimination(bn)
result = infer.query(['C'], evidence={'A': 1})
print(f'  P(C|A=1): {result.values}')

print('\n=== pysat ===')
from pysat.solvers import Solver
from pysat.formula import CNF
cnf = CNF()
cnf.append([1, 2])
cnf.append([-1, 2])
cnf.append([1, -2])
with Solver(name='g3', bootstrap_with=cnf) as s:
    print(f'  SAT: {s.solve()}, model: {s.get_model()}')
# Test UNSAT
cnf2 = CNF()
cnf2.append([1])
cnf2.append([-1])
with Solver(name='g3', bootstrap_with=cnf2) as s:
    print(f'  UNSAT: {s.solve()} (should be False)')

print('\n=== python-constraint ===')
from constraint import Problem
p = Problem()
p.addVariable('x', [1,2,3])
p.addVariable('y', [1,2,3])
p.addConstraint(lambda x,y: x != y, ('x','y'))
sols = p.getSolutions()
print(f'  Solutions: {len(sols)}, sample: {sols[0]}')

print('\n=== nashpy ===')
import nashpy as nash
import numpy as np
# Prisoner's Dilemma
A = np.array([[3,0],[5,1]])
B = np.array([[3,5],[0,1]])
g = nash.Game(A, B)
eqs = list(g.support_enumeration())
print(f'  Nash equilibria: {len(eqs)}')
for eq in eqs:
    print(f'    P1={eq[0]}, P2={eq[1]}')

print('\nALL LIBRARIES VERIFIED')
