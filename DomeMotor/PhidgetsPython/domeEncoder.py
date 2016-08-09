#Basic imports
from ctypes import *
import sys
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, EncoderPositionChangeEventArgs, InputChangeEventArgs
from Phidgets.Devices.Encoder import Encoder
from Phidgets.Phidget import PhidgetLogLevel
import Phidget

class domeEncoder(Phidget):
    
    def __init__(self):
        self.test = 'yay'
        self.stepsIn360 = 1500
        self.domePos = 0


#Information Display Function
def displayDeviceInfo():
    print("|------------|----------------------------------|--------------|------------|")
    print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    print("|------------|----------------------------------|--------------|------------|")
    print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (encoder.isAttached(), encoder.getDeviceName(), encoder.getSerialNum(), encoder.getDeviceVersion()))
    print("|------------|----------------------------------|--------------|------------|")

#Event Handler Callback Functions
def encoderAttached(e):
    attached = e.device
    print("Encoder %i Attached!" % (attached.getSerialNum()))

def encoderDetached(e):
    detached = e.device
    print("Encoder %i Detached!" % (detached.getSerialNum()))

def encoderError(e):
    try:
        source = e.device
        print("Encoder %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

def encoderInputChange(e):
    source = e.device
    print("Encoder %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

def encoderPositionChange(e):
    source = e.device
    print("Encoder %i: Encoder %i -- Change: %i -- Time: %i -- Position: %i" % (source.getSerialNum(), e.index, e.positionChange, e.time, encoder.getPosition(e.index)))
    print "Dome at %i degrees from close" % getDomePos()

def getDomePos(e):
    self.domePos = ( float(e.getPosition) / float(self.stepsIn360) ) * 360.0

def home(e):
    #if the home switch is activated,
    #e.setPosition(0,0)

    if __name__ == '__main__':
        #Main Program Code
        #Create an accelerometer object
        try:
            encoder = Encoder()
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)
            print("Exiting....")
            exit(1)

        try:
            #logging example, uncomment to generate a log file
            #encoder.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")

            encoder.setOnAttachHandler(encoderAttached)
            encoder.setOnDetachHandler(encoderDetached)
            encoder.setOnErrorhandler(encoderError)
            encoder.setOnInputChangeHandler(encoderInputChange)
            encoder.setOnPositionChangeHandler(encoderPositionChange)
        except PhidgetException as e:
            print("Phidget Error %i: %s" % (e.code, e.details))
            exit(1)

        print("Opening phidget object....")

        try:
            encoder.openPhidget()
        except PhidgetException as e:
            print("Phidget Error %i: %s" % (e.code, e.details))
            exit(1)

        print("Waiting for attach....")

        try:
            encoder.waitForAttach(10000)
        except PhidgetException as e:
            print("Phidget Error %i: %s" % (e.code, e.details))
            try:
                encoder.closePhidget()
            except PhidgetException as e:
                print("Phidget Error %i: %s" % (e.code, e.details))
                exit(1)
            exit(1)
        else:
            displayDeviceInfo()

        print("Press Enter to quit....")

        chr = sys.stdin.read(1)

        print("Closing...")

        try:
            encoder.closePhidget()
        except PhidgetException as e:
            print("Phidget Error %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

        print("Done.")
        exit(0)
