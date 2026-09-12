;; Techne minimal microKanren query, matched to this microKanren.scm's API:
;; a state is (substitution . counter); the initial state is '(() . 0); a goal
;; applied to a state returns a stream (a possibly-improper list / procedure).
(define empty-state '(() . 0))
;; microKanren.scm uses R6RS `assp`, which Guile does not export by default. It is a library
;; primitive, not part of the algorithm, so Techne supplies it in the HARNESS rather than
;; editing the specimen: (assp pred alist) = first pair whose car satisfies pred, else #f.
(define (assp pred lst)
  (cond ((null? lst) #f) ((pred (caar lst)) (car lst)) (else (assp pred (cdr lst)))))
(define (pull $) (if (procedure? $) (pull ($)) $))
(define (take n $)
  (let loop ((n n) ($ (pull $)))
    (cond ((null? $) '())
          ((= n 0) '())
          (else (cons (car $) (loop (- n 1) (pull (cdr $))))))))
(define one ((call/fresh (lambda (q) (== q 5))) empty-state))
(display "answers-for-q=5: ") (display (length (take 5 one))) (newline)
(define two ((call/fresh (lambda (q) (disj (== q 1) (== q 2)))) empty-state))
(display "disj-answers: ") (display (length (take 9 two))) (newline)
(display "MICROKANREN_OK") (newline)
