      program qtest
      external f
      double precision a,b,epsabs,epsrel,result,abserr
      integer neval,ier,limit,lenw,last
      parameter (limit=50, lenw=200)
      integer iwork(limit)
      double precision work(lenw)
      a=0.0d0
      b=3.0d0
      epsabs=0.0d0
      epsrel=1.0d-8
      call dqags(f,a,b,epsabs,epsrel,result,abserr,neval,ier,
     *           limit,lenw,last,iwork,work)
      if (dabs(result-9.0d0).lt.1.0d-6 .and. ier.eq.0) then
        write(*,*) 'QUADPACK_OK result=',result,' abserr=',abserr
      else
        write(*,*) 'QUADPACK_BAD result=',result,' ier=',ier
      endif
      end
      double precision function f(x)
      double precision x
      f=x*x
      return
      end
