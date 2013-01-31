import sys
from vision import Calibrator

def main(argv):
    if len(argv) == 0: index = 0
    else: index = int(argv[0])
    Calibrator(index).run()

if __name__ == "__main__":
    main(sys.argv[1:])
