      program etest
      integer nm,n,ierr,matz,i
      parameter (nm=3,n=3)
      double precision a(nm,n),w(n),z(nm,n),fv1(n),fv2(n)
      double precision expect(3),tol,d
      data a /2.0d0,0.0d0,0.0d0, 0.0d0,3.0d0,0.0d0, 0.0d0,0.0d0,4.0d0/
      matz=0
      call rs(nm,n,a,w,matz,z,fv1,fv2,ierr)
      expect(1)=2.0d0
      expect(2)=3.0d0
      expect(3)=4.0d0
      tol=1.0d-8
      d=0.0d0
      do 10 i=1,n
        d=d+dabs(w(i)-expect(i))
   10 continue
      if (ierr.eq.0 .and. d.lt.tol) then
        write(*,*) 'EISPACK_OK eig=',w(1),w(2),w(3)
      else
        write(*,*) 'EISPACK_BAD ierr=',ierr,' dev=',d
      endif
      end
