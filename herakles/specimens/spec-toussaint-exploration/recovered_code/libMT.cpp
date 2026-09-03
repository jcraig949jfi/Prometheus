// the following definition triggers the object building
#define MT_IMPLEMENTATION

// uncomment one of the following to include library bindings
#define MT_QT
//#define MT_SHARK
//#define MT_LEDA

// the library binders - always keep to this order!
#include "qt.h"
//#include "leda.h"

// these are all the headers - exclude some if you do not want to use them...
#include "timer.h"
#include "stdfunc.h"
#include "evolution.h"
#include "operonString.h"
#include "genotype.h"
#include "array.h"
#include "graph.h"
#include "stdgraph.h"
#include "netFFN.h"
#include "netDyn.h"
#include "learner.h"
#include "statistics.h"
#include "Qlearner.h"
#include "plant.h"
#include "proPlant.h"
#include "opengl.h"
#include "netMo.h"
#include "proKhepera.h"
#include "kheperaPort.h"
