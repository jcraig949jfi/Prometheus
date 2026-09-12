/* Techne harness: estimate a hidden constant (10.0) from noisy measurements. The filtered
   error must be far below the raw measurement noise. */
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "SimpleKalmanFilter.h"
int main(){
  SimpleKalmanFilter kf(2.0f, 2.0f, 0.01f);   /* meas err, est err, process noise */
  srand(1); double truth=10.0, sraw=0, sflt=0; int N=2000;
  for(int k=0;k<N;k++){ double noise=((rand()%2001)/1000.0-1.0)*3.0; /* +-3 */
    double meas=truth+noise; double est=kf.updateEstimate((float)meas);
    sraw+=(meas-truth)*(meas-truth); sflt+=(est-truth)*(est-truth); }
  double rmsraw=sqrt(sraw/N), rmsflt=sqrt(sflt/N);
  printf("rms_raw=%.4f rms_filtered=%.4f ratio=%.3f\n", rmsraw, rmsflt, rmsflt/rmsraw);
  printf(rmsflt < rmsraw*0.5 ? "KALMAN_OK\n" : "KALMAN_WEAK\n");
  return 0; }
