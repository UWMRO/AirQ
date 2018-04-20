import domeEncoder
import subprocess
import numpy as np
import time
import os
import re

class domePos(object):
    def __init__(self):
	self.f = 'currentPos.txt'
	#change this to read in file:
	init = np.genfromtxt('dome.init',delimiter=',')
	self.current = init[1]
	self.domeStart = init[0]  #azimuth angle that dome home position is at
	self.azPos = self.current + self.domeStart
	self.homed = (self.current == 0)
	print 'Starting...'	

    def readData(self):
	data = ''
	if os.path.isfile(self.f):
	    with open(self.f) as fin:
	        for line in fin.readlines():
	            data = line
	    try:
	        self.current = float(filter(str.isdigit,data))
	    except:
	        pass
	    self.homed = (self.current == 0.0)
	    time.sleep(0.5)
	else:
	    pass

    def azCalc(self):
	#self.azPos = az position calculated from self.current realtive to location..
	#use to check if telescope az and dome az are aligned, tells you if you
	#can see out the dome
	self.azPos = self.domeStart - self.current
	if self.azPos < 0:
	    self.azPos = 360 + self.azPos
  
if __name__ == '__main__':
    g = domePos()
    p = subprocess.Popen(['sudo','python','domeEncoder.py','&'])
    #print 'Starting...'
    time.sleep(15)
    #print 'domeEncoder.py running'
    print 'Tracking dome position:\n'
    #print 'Press q to quit'
    a = True
    while a == True:
	g.readData()		
        pos = g.current
        azPos = g.azPos
	homed = g.homed
	datas = list([str(pos),str(azPos),str(homed)])
	print datas
	with open('domePos.out','w') as fin:
	    fin.write(''.join(datas))
	userInput = raw_input('Press q to quit\n')
        if userInput == 'q\n':
            print 'Stopping dome tracking'
            p.terminate()
            print 'test: quitting domeEncoder.py'
            #subprocess.Popen(['rm','currentPos.txt'])
            print 'exiting...'
            break

	#take user input q to quit: first use subprocess to press enter to quit domeEncoder.py,
	#then quit this program

	#out file is of format: currentPos, azPos, homed(bool)
