;; Techne harness: PAIP chapter 4 GPS, the school problem, exactly as the book runs it.
(load "lisp/auxfns.lisp")
(load "lisp/gps.lisp")
(use *school-ops*)
(let ((plan (gps '(son-at-home car-needs-battery have-money have-phone-book) '(son-at-school))))
  (format t "~%PLAN: ~S~%" plan))
