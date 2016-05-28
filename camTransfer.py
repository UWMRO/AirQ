#! /usr/bin/python

import subprocess
import time
import matplotlib
import matplotlib.dates as dt
import dateutil
import re
import os

class WebTransfer(object):

	def __init__(self):
		self.dir = '/home/mro/Pictures/Picture/'
		self.delay = 30
		self.se_current = 0
		
	def run(self):
		while True:
			self.sync()
			time.sleep(self.delay)

	def sync(self):
		command = "rsync  --ignore-existing -razv -e 'ssh -i /home/mro/.ssh/id_rsa -l jwhueh' --progress /home/mro/Pictures/Picture/ analysis:/raid/MRO/Webcam/Picture/"
                out = subprocess.Popen(command, stdout = subprocess.PIPE, shell=True)
                while True:
                        line = out.stdout.readline()
                        if line:
                                self.log(line)
				if re.search('jpg', line):
					l = line.split('/')
					t = l[2].lstrip('se_').rstrip('.jpg\n')
					t = time.strptime(t, "%Y%m%d_%H%M%S_%f")
					t = time.mktime(t)
					if (time.time()- t) < 120:
						self.upload(line)
					
                        if not line:
                                break

	def upload(self,line):
		if re.search('se_',line):
			name = 'se.jpg'
		if re.search('s_',line):
			name = 's.jpg'
		cmd = os.path.join(self.dir, line.rstrip('\n'))
		print cmd
		os.system('scp %s ovid:public_html/MRO/%s' % (cmd, name))
		return
	
	def log(self, text):
		fout = open('cam.log','a')
		fout.write(str(text))
		fout.close()
		return
			

if __name__ == "__main__":
	w = WebTransfer()
	w.run()
