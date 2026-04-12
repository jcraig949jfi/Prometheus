import sys
import os

# Add src to the path so we can run the arcanum_infinity package
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arcanum_infinity.main_xeno import main

if __name__ == "__main__":
    # We don't need to manually shift sys.argv, main() uses argparse which will handle it.
    main()
