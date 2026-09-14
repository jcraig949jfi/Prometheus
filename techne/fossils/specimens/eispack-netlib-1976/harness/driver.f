      program eigdrv
      integer nm,n,matz,ierr
      double precision a(3,3),w(3),z(3,3),fv1(3)
      nm = 3
      n = 3
      matz = 1
      a(1,1)= 2.0d0
      a(1,2)=-1.0d0
      a(1,3)= 0.0d0
      a(2,1)=-1.0d0
      a(2,2)= 2.0d0
      a(2,3)=-1.0d0
      a(3,1)= 0.0d0
      a(3,2)=-1.0d0
      a(3,3)= 2.0d0
      call rs(nm,n,a,w,matz,z,fv1,fv1,ierr)
      write(6,10) ierr
   10 format(' ierr = ',i4)
      write(6,20) w(1),w(2),w(3)
   20 format(' eigenvalues: ',3f12.6)
      stop
      end
