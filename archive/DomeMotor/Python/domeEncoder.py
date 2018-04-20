#!/usr/bin/env python

#Basic imports
from ctypes import *
import sys
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, EncoderPositionChangeEventArgs, InputChangeEventArgs
from Phidgets.Devices.Encoder import Encoder
from Phidgets.Phidget import PhidgetLogLevel
import subprocess
import os


class domeEncoder(object):
    def __init__(self):
        self.dict = {}
	self.log = open('encoderLog.txt','w')
	if 'currentPos.txt' in os.listdir(os.getcwd()):	
		subprocess.Popen(['rm','currentPos.txt'])
	self.currentPos = 'currentPos.txt'
	with open(self.currentPos,'w') as f:
		f.write('0')
		


    #Information Display Function
    def displayDeviceInfo(self):
	self.log.write("|------------|----------------------------------|--------------|------------|\n")
        self.log.write("|- Attached -|-              Type              -|- Serial No. -|-  Version -|\n")
        self.log.write("|------------|----------------------------------|--------------|------------|\n")
        self.log.write("|- %8s -|- %30s -|- %10d -|- %8d -|" % (encoder.isAttached(), encoder.getDeviceName(), encoder.getSerialNum(), encoder.getDeviceVersion()))
        self.log.write("|------------|----------------------------------|--------------|------------|\n")

        #print("|------------|----------------------------------|--------------|------------|")
        #print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
        #print("|------------|----------------------------------|--------------|------------|")
        #print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (encoder.isAttached(), encoder.getDeviceName(), encoder.getSerialNum(), encoder.getDeviceVersion()))
        #print("|------------|----------------------------------|--------------|------------|")

    #Event Handler Callback Functions
    def encoderAttached(self,e):
        attached = e.device
        self.log.write("Encoder %i Attached!\n" % (attached.getSerialNum()))
	#print("Encoder %i Attached!" % (attached.getSerialNum())

    def encoderDetached(self,e):
        detached = e.device
        self.log.write("Encoder %i Detached!\n" % (detached.getSerialNum()))
        #print("Encoder %i Detached!" % (detached.getSerialNum()))

    def encoderError(self,e):
        try:
            source = e.device
            self.log.write("Encoder %i: Phidget Error %i: %s\n" % (source.getSerialNum(), e.eCode, e.description))
            #print("Encoder %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            self.log.write("Phidget Exception %i: %s\n" % (e.code, e.details))
            #print("Phidget Exception %i: %s" % (e.code, e.details))

    def encoderInputChange(self,e):
        source = e.device
        self.log.write("Encoder %i: Input %i: %s\n" % (source.getSerialNum(), e.index, e.state))
        #print("Encoder %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

    def encoderPositionChange(self,e):
        source = e.device
        self.log.write("Encoder %i: Encoder %i -- Change: %i -- Time: %i -- Position: %i\n" % (source.getSerialNum(), e.index, e.positionChange, e.time, encoder.getPosition(e.index)))
        #print("Encoder %i: Encoder %i -- Change: %i -- Time: %i -- Position: %i" % (source.getSerialNum(), e.index, e.positionChange, e.time, encoder.getPosition(e.index)))
    #    getDomePos(e)
        self.log.write( "Dome at %i\n" % ((float((encoder.getPosition(e.index))/float(1500))*360.0)%360.0))
	with open(self.currentPos,'w') as fin:    
		fin.write("%i" % ((float((encoder.getPosition(e.index))/float(1500))*360.0)%360.0))
		fin.flush()


    #def getDomePos(e):
     #   self.domePos = ( float(encoder.getPosition(e.index)) / float(self.stepsIn360) ) * 360.0

    #def home(e):
        #if the home switch is activated,
        #e.setPosition(0,0)
if __name__ == "__main__":
    g = domeEncoder()
    #Create an accelerometer object
    try:
        encoder = Encoder()
    except RuntimeError as e:
        g.log.write("Runtime Exception: %s\n" % e.details)
        g.log.write("Exiting....\n")
        #print("Runtime Exception: %s" % e.details)
        #print("Exiting....")
        exit(1)
    #Main Program Code
    try:
    	#logging example, uncomment to generate a log file
        #encoder.enableLogging(PhidgetLogLevel.PHIDGET_LOG_VERBOSE, "phidgetlog.log")

        encoder.setOnAttachHandler(g.encoderAttached)
        encoder.setOnDetachHandler(g.encoderDetached)
        encoder.setOnErrorhandler(g.encoderError)
        encoder.setOnInputChangeHandler(g.encoderInputChange)
        encoder.setOnPositionChangeHandler(g.encoderPositionChange)
    except PhidgetException as e:
        g.log.write("Phidget Error %i: %s\n" % (e.code, e.details))
        #print("Phidget Error %i: %s" % (e.code, e.details))
        exit(1)

    g.log.write("Opening phidget object....\n")
    #print("Opening phidget object....")

    try:
        encoder.openPhidget()
    except PhidgetException as e:
        g.log.write("Phidget Error %i: %s\n" % (e.code, e.details))
        #print("Phidget Error %i: %s" % (e.code, e.details))
        exit(1)

    g.log.write("Waiting for attach....\n")
    #print("Waiting for attach....")

    try:
        encoder.waitForAttach(10000)
    except PhidgetException as e:
        g.log.write("Phidget Error %i: %s\n" % (e.code, e.details))
        #print("Phidget Error %i: %s" % (e.code, e.details))
        try:
            encoder.closePhidget()
        except PhidgetException as e:
            g.log.write("Phidget Error %i: %s\n" % (e.code, e.details))
            #print("Phidget Error %i: %s" % (e.code, e.details))
            exit(1)
        exit(1)
    else:
        g.displayDeviceInfo()

    g.log.write("Press Enter to quit....\n")
    #print("Press Enter to quit....")

    chr = sys.stdin.read(1)

    g.log.write("Closing...\n")
    #print("Closing...")

    try:
        encoder.closePhidget()
    except PhidgetException as e:
        g.log.wite("Phidget Error %i: %s" % (e.code, e.details))
        g.log.write("Exiting....")
        #print("Phidget Error %i: %s" % (e.code, e.details))
        #print("Exiting....")
        exit(1)

    g.log.write("Done.\n")
    #print("Done.")
    exit(0)
