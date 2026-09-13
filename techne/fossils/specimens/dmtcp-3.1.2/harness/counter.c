#include <stdio.h>
#include <unistd.h>
int main(void){ for (int i = 1; ; i++) { printf("count %d\n", i); fflush(stdout); sleep(1); } }
