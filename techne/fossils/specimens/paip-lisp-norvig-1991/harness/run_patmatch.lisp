;; Techne harness: PAIP pattern matcher (ch. 6) and unifier (ch. 11).
(load "lisp/auxfns.lisp")
(load "lisp/patmatch.lisp")
(format t "~%PATMATCH: ~S~%" (pat-match '(i need a ?X) '(i need a vacation)))
(format t "PATMATCH-SEGMENT: ~S~%" (pat-match '((?* ?p) need (?* ?x)) '(Mr Hulot and I need a vacation)))
(load "lisp/unify.lisp")
(format t "UNIFY: ~S~%" (unify '(?x + 1) '(2 + ?y)))
