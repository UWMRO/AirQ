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
		self.delay = 60
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
					"""self.log(("found: " + str(line) +'\n'))
					l = line.split('/')
<<<<<<< HEAD
					t = l[2].lstrip('se_').lstrip('s_').rstrip('.jpg\n')
					t = time.strptime(t, "%Y%m%d_%H%M%S_%f")
					t = time.mktime(t)
					print t, time.time(), l
					if (time.time()- t) < 4000:"""
					self.upload(line.rstrip('\n'))
=======
					#t = l[2].lstrip('se_').rstrip('.jpg\n')
					#t = time.strptime(t, "%Y%m%d_%H%M%S_%f")
					#t = time.mktime(t)
					#if (time.time()- t) < 120:
					self.upload(line)
>>>>>>> 6b48605a715fadcb77dc1e7d59aa98436aae8c0d
					
                        if not line:
                                break

	def upload(self,line):
<<<<<<< HEAD
		l = line.split('/')
		name = l[(len(l)-1)].split('_')[0]+".jpg"
=======
		print line
>>>>>>> 6b48605a715fadcb77dc1e7d59aa98436aae8c0d
		cmd = os.path.join(self.dir, line.rstrip('\n'))
		self.log(("uploading: " + str(cmd)))
		print cmd, name

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
