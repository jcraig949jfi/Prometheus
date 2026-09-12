import numpy as np
from filterpy.kalman import KalmanFilter
np.random.seed(1)
# constant-velocity 1-D target; measure position with noise sigma=3
dt=1.0; kf=KalmanFilter(dim_x=2,dim_z=1)
kf.F=np.array([[1,dt],[0,1]]); kf.H=np.array([[1,0]])
kf.R=np.array([[9.0]]); kf.Q=np.eye(2)*0.01; kf.P=np.eye(2)*500; kf.x=np.array([[0.],[0.]])
truth=0.0; v=1.0; sraw=0; sflt=0; N=200
for k in range(N):
    truth+=v; z=truth+np.random.randn()*3.0
    kf.predict(); kf.update(np.array([[z]]))
    sraw+=(z-truth)**2; sflt+=(kf.x[0,0]-truth)**2
import math
rr=math.sqrt(sraw/N); rf=math.sqrt(sflt/N)
print("rmse_sensor %.3f rmse_filter %.3f"%(rr,rf))
print("FILTERPY_OK" if rf<rr else "FILTERPY_WEAK")
