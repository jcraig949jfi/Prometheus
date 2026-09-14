/* maximise 3x + 2y s.t. x + y <= 4, x + 3y <= 6, x,y >= 0 ; optimum 12 at (4,0), verified against all four vertices */
var x >= 0; var y >= 0;
maximize obj: 3*x + 2*y;
s.t. c1: x + y <= 4;
s.t. c2: x + 3*y <= 6;
solve;
printf "OBJECTIVE %g x %g y %g\n", obj, x, y;
end;
