# Matt Vernacchia | MASLab Team 4
# defines a IR_Dist class for interacting with the IR Distance sensors. Example code a bottom of file.

import pickle
import arduino
import time
import numpy, pylab # for plotting

class IR_Dist:
    def __init__(self, ardu, port):
        self.ain = arduino.AnalogInput(ardu, port)
        self.vals = None
    def load(self):
        try:
            f = open('ir_dist_calibration.txt', 'r')
            self.vals = pickle.load(f)
        except IOError as e:
            print "Error reading from IR calibration file: {0} {1}".format(e.errno, e.strerror)
        except:
            print "unexpected error reading from IR sensor calibration file"
    def getVolt(self):
        """Returns the analog volatage output of the IR sensor in the arduino's
           voltage units (1 unit = 4.9mV, 1024 units = 5v)"""
        return self.ain.getValue()
    def getDist(self):
        """Returns the distance currently read by the IR distance sensor, in centimeters."""
        return self.convertToDist( self.ain.getValue() )
    def convertToDist(self, volt):
        """ Converts a voltage reading to a distance based on the calibration data"""
        if self.vals == None:
            print "IR_Dist: must calibrate and load before converting voltage to distance"
        i = 0
        while self.vals[i][0] < volt and i < (len(self.vals)-1):
            i = i + 1
        if i == 0: return self.vals[0][1]
        elif i == (len(self.vals)-1): return self.vals[-1][1]
        else:
            # linear interpolation between the two closest calibrated values
            ratio = (self.vals[i-1][0] - volt)/(self.vals[i-1][0] - self.vals[i][0])
            return ( self.vals[i-1][1] + ratio*(self.vals[i][1]-self.vals[i-1][1]) )

    def calibrate(self):
        """Manually calibrate the distance readings on the IR sensors and save the results to a file"""
        vals = []
        print ""
        print "Manual Calibration of IR Distance Sensors"
        print "Type 'q' to quit"
        while True:
            s = raw_input("Enter target distance in cm: ")
            if s == "q": break
            dist = int(s)
            volt = 0
            for x in range(10):
                volt = volt + self.ain.getValue()
            volt  = volt/10.0
            vals.append( (volt, dist) )
        # sort the list of voltage-distance pairs
        vals = sorted(vals)
        # pickle the list of voltage-distance paris to a file
        f = open('ir_dist_calibration.txt', 'w')
        pickle.dump(vals, f)

    def plotCalibrationData(self):
        """ Plots a graph of the calibration data. blocks until the graph window is closed?"""
        if self.vals == None: print "must calibrate and load before plotting"
        volts = numpy.zeros( len(self.vals) )
        dists = numpy.zeros( len(self.vals) )
        for i in range( len(self.vals) ):
            volts[i] = self.vals[i][0]
            dists[i] = self.vals[i][1]
        pylab.plot(dists, volts)
        pylab.xlabel('Distance [cm]')
        pylab.ylabel('Voltage [4.9mV steps]')
        pylab.title('IR Distance Sensor Calibration Data')
        pylab.show()
####### testing #########
ardu = arduino.Arduino()
ir = IR_Dist(ardu, 4)
ardu.run()
time.sleep(1)

#ir.calibrate()
ir.load()
ir.plotCalibrationData()
while True:
    print ir.getDist()
