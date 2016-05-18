#! /usr/bin/python

import subprocess
import time

class WebTransfer(object):

	def __init__(self):
		self.dir = '/home/mro/Pictures/Picture/'
		self.delay = 30
		
	def run(self):
		while True:
			self.sync()
			time.delay()

	def sync(self):
		command = "rsync  --ignore-existing -razv -e 'ssh -i /home/mro/.ssh/id_rsa -l jwhueh' --progress /home/mro/Pictures/Picture/ analysis:/raid/MRO/Webcam/Picture/"
                out = subprocess.Popen(command, stdout = subprocess.PIPE, shell=True)
                while True:
                        line = out.stdout.readline()
                        if line:
                                self.log(line)
                        if not line:
                                break
	
	def log(self, text):
		fout = open('cam.log','a')
		fout.write(str(text))
		fout.close()
			

if __name__ == "__main__":
	w = WebTransfer()
	w.run()
