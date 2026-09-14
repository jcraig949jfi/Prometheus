C Techne harness: Robertson stiff kinetics through DLSODE with a method flag from argv.
C MF=21 (BDF + user Jacobian) is the stiff method; MF=10 (Adams) is the PATHOLOGY.
      PROGRAM ROB
      EXTERNAL FEX, JEX
      DOUBLE PRECISION ATOL(3), RTOL, RWORK(200), T, TOUT, Y(3)
      INTEGER IWORK(50), NEQ, ITOL, ITASK, ISTATE, IOPT, LRW, LIW, MF
      INTEGER IOUT
      CHARACTER*8 ARG
      CALL GETARG(1, ARG)
      READ(ARG,*) MF
      NEQ = 3
      Y(1) = 1.0D0
      Y(2) = 0.0D0
      Y(3) = 0.0D0
      T = 0.0D0
      TOUT = 0.4D0
      ITOL = 2
      RTOL = 1.0D-4
      ATOL(1) = 1.0D-6
      ATOL(2) = 1.0D-10
      ATOL(3) = 1.0D-6
      ITASK = 1
      ISTATE = 1
      IOPT = 0
      LRW = 200
      LIW = 50
      DO 40 IOUT = 1,12
        CALL DLSODE(FEX,NEQ,Y,T,TOUT,ITOL,RTOL,ATOL,ITASK,ISTATE,
     1              IOPT,RWORK,LRW,IWORK,LIW,JEX,MF)
        WRITE(6,20)T,Y(1),Y(2),Y(3),ISTATE
  20    FORMAT(' T =',D12.4,'   Y =',3D14.6,'   ISTATE=',I3)
        IF (ISTATE .LT. 0) GO TO 80
  40    TOUT = TOUT*10.0D0
      WRITE(6,60)IWORK(11),IWORK(12),IWORK(13)
  60  FORMAT(' NSTEP =',I6,'  NFE =',I6,'  NJE =',I6)
      WRITE(6,*) 'RESULT OK MF=', MF
      STOP
  80  WRITE(6,90)ISTATE
  90  FORMAT(' ERROR HALT.. ISTATE =',I3)
      WRITE(6,*) 'RESULT FAILED MF=', MF, ' NSTEP=', IWORK(11)
      STOP
      END
      SUBROUTINE FEX (NEQ, T, Y, YDOT)
      INTEGER NEQ
      DOUBLE PRECISION T, Y(3), YDOT(3)
      YDOT(1) = -.04D0*Y(1) + 1.D4*Y(2)*Y(3)
      YDOT(3) = 3.D7*Y(2)*Y(2)
      YDOT(2) = -YDOT(1) - YDOT(3)
      RETURN
      END
      SUBROUTINE JEX (NEQ, T, Y, ML, MU, PD, NRPD)
      INTEGER NEQ, ML, MU, NRPD
      DOUBLE PRECISION PD(NRPD,3), T, Y(3)
      PD(1,1) = -.04D0
      PD(1,2) = 1.D4*Y(3)
      PD(1,3) = 1.D4*Y(2)
      PD(2,1) = .04D0
      PD(2,3) = -PD(1,3)
      PD(3,2) = 6.D7*Y(2)
      PD(2,2) = -PD(1,2) - PD(3,2)
      RETURN
      END
