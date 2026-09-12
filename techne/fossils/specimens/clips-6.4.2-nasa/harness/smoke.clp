(deffacts start (patient fever) (patient cough))
(defrule flu-suspect
   (patient fever) (patient cough)
   =>
   (assert (diagnosis flu-suspected))
   (printout t "RULE FIRED: flu-suspected" crlf))
(defrule report
   (diagnosis ?d)
   =>
   (printout t "DIAGNOSIS " ?d crlf))
(reset)
(run)
(exit)
