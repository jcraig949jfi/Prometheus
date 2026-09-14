/* Techne harness: PID controlling a THIRD-order loop (two cascaded first-order lags plus the
   controller's own integrator). Setpoint step to 1.0. Low gain converges; very high gain pushes
   the loop into sustained oscillation -- a pathological-behavior receipt. Instability is detected
   by counting late-window setpoint crossings (output saturates at +-50, so an unstable loop
   oscillates rather than diverging to infinity). */
#include "Arduino.h"
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "PID_v1.h"
int main(int argc,char**argv){
  double Kp = (argc>1)? atof(argv[1]) : 2.0;
  double Ki = (argc>2)? atof(argv[2]) : 1.0;
  double Kd = (argc>3)? atof(argv[3]) : 0.05;
  double In=0, Out=0, Set=1.0;
  PID pid(&In,&Out,&Set, Kp, Ki, Kd, DIRECT);
  pid.SetMode(AUTOMATIC); pid.SetOutputLimits(-50,50); pid.SetSampleTime(10);
  double y1=0.0, y2=0.0, dt=0.01;
  int N=6000, late_cross=0; double late_max=0.0, prev_err=Set-y2;
  for(int k=0;k<N;k++){ _advance(10); In=y2; pid.Compute();
    y1 += dt*(-y1 + Out);               /* lag 1 */
    y2 += dt*(-y2 + y1);                /* lag 2 -> controlled variable */
    double err=Set-y2;
    if(k > (int)(0.7*N)){ if((err>0)!=(prev_err>0)) late_cross++; if(fabs(y2)>late_max) late_max=fabs(y2); }
    prev_err=err; }
  printf("Kp=%.1f final=%.4f late_crossings=%d late_max=%.3f\n", Kp, y2, late_cross, late_max);
  if (fabs(y2-Set)<0.15 && late_cross<=3) printf("PID_CONVERGED\n");
  else if (late_cross>=12 || late_max>4.0) printf("PID_UNSTABLE\n");
  else printf("PID_MARGINAL\n");
  return 0; }
