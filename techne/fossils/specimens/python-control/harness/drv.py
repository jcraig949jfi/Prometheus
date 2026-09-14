import numpy as np, control as ct
# double integrator: x1'=x2, x2'=u ; LQR should stabilise it to the origin
A=np.array([[0,1],[0,0]]); B=np.array([[0],[1]]); Q=np.eye(2); Rm=np.array([[1.0]])
K,S,E=ct.lqr(A,B,Q,Rm)
Acl=A-B@K
# simulate from a perturbed state
x=np.array([1.0,0.0]); dt=0.01
for _ in range(2000): x=x+dt*(Acl@x)
print("closed_loop_eig_real_max %.4f"%max(e.real for e in np.linalg.eigvals(Acl)))
print("final_state %.4e %.4e"%(x[0],x[1]))
print("LQR_STABILIZED" if max(e.real for e in np.linalg.eigvals(Acl))<0 and abs(x[0])<1e-2 else "LQR_FAILED")
