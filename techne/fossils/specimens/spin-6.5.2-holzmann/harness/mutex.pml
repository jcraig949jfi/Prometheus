/* Peterson's algorithm for two processes; the assertion is that both are never critical */
bool flag[2]; byte turn; byte ncrit;
active [2] proctype P() {
  pid i = _pid; pid j = 1 - _pid;
again:
  flag[i] = true; turn = j;
  (flag[j] == false || turn == i);
  ncrit++;
  assert(ncrit == 1);   /* critical section */
  ncrit--;
  flag[i] = false;
  goto again;
}
