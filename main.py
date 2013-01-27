from fsm import FiniteStateMachine
import sys

def main(argv):
    fsm = FiniteStateMachine()
    fsm.start()
   
if __name__ == "__main__":
    main(sys.argv[1:])
