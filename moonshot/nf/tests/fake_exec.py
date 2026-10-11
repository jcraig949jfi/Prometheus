"""Test fixture: a module of the approved commit that is NOT the approved executor, yet emits a valid epoch (it calls
the real one). The publisher must refuse its output on provenance (C-012-T003 test_coordinator)."""
import sys

from moonshot.epoch.fabric_exec import main

if __name__ == "__main__":
    sys.exit(main())
