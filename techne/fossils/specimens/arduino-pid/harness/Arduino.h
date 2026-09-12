#ifndef ARDUINO_H
#define ARDUINO_H
#include <stdint.h>
static unsigned long _ms=0; inline unsigned long millis(){return _ms;} inline void _advance(unsigned long d){_ms+=d;}
#endif
