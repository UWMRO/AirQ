import domeEncoder
import subprocess

class domePos(object):
    
    def __init__(self):
		self.f = open('currentPos.txt','r')
		self.current = 0
		self.azPos = 0

	def readData(self):
		#self.current = the number read in

	def azCalc(self):
		#self.azPos = az position calculated from self.current realtive to location..
		#use to check if telescope az and dome az are aligned, tells you if you
		#can see out the dome


    if __name__ == '__main__':
        g = domePos()
		subprocess.run(['python','domeEncoder.py'])
		a = True
		while a == True		
			#pos = g.current
			#azPos = g.azPos
			pos=1
			azPos=2
