C QUADPACK calls the SLATEC error handler XERROR on failure paths. The real XERROR pulls a
C large SLATEC chain (xerrwv/xsetf/...). For standalone QUADPACK the conventional practice is
C a print-and-continue stub; it affects ONLY the diagnostic path, never the quadrature result.
C RECORDED as a Techne support shim (not upstream source).
      subroutine xerror(mess,nmess,nerr,level)
      character*(*) mess
      integer nmess,nerr,level
      write(*,*) 'XERROR(stub): ', mess(1:min(nmess,60)), ' nerr=', nerr
      return
      end
