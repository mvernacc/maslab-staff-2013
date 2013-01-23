import pickle

def calibrate():
    # Manually calibrate the distance readings on the IR sensors and save the results to a file
    stop = False
    vals = []
    print ""
    print "Manual Calibration of IR Distance Sensors"
    print "Type 'q' to quit"
    while not stop:
        s = raw_input("Enter target distance in cm: ")
        if s == "q": break
        dist = int(s)
        volt = 0
        for x in range(10):
            volt = volt + 0#get voltage from sensor
        volt  = volt/10.0
        vals.append( (volt, dist) )
    # sort the list of voltage-distance pairs
    vals = sorted(vals)

    # pickle the list of voltage-distance paris to a file
    f = open('ir_dist_calibration.txt', 'w')
    pickle.dump(vals, f)

class Converter:
    def __init__(self):
        try:
            f = open('ir_dist_calibration.txt', 'r')
            self.vals = pickle.load(f)
        except IOError as e:
            print "Error reading from IR calibration file: {0} {1}".format(e.errno, e.strerror)
        except:
            print "unexpected error reading from IR sensor calibration file"
    
    def get_dist(self, volt):
        i = 0
        while self.vals[i][0] < volt and i < (len(self.vals)-1):
            i = i + 1
        if i == 0: return self.vals[0][1]
        elif i == (len(self.vals)-1): return self.vals[-1][1]
        else:
            # linear interpolation between the two closest calibrated values
            ratio = (self.vals[i-1][0] - volt)/(self.vals[i-1][0] - self.vals[i][0])
            return ( self.vals[i-1][1] + ratio*(self.vals[i][1]-self.vals[i-1][1]) )


calibrate()
