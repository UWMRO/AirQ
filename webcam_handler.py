""" webcam_handler.py
Requests security camera images, archives them, and forwards the latest to remote server. 
Naming convention assumes images come in slower than once per second.

Original by Matt Armstrong (~'17-'18), modified for direct access to webcams by OJF '19

replace 
  Subprocess(['rsync -azrh --progress *jpg mrouser@ovid.u.washington.edu:public_html/webcams/' with 
  curl -T [image] scp://ovid.u.washington.edu/public_html/webcams/[name].jpg -u mrouser

(found that PycURL (default package) works well, but if I run into problems, try requests (HTTP for Humans)

Exceptions in objects should pass up their problem, not print...
"""

import os, shutil, subprocess, glob, time, sys
import pycurl
from datetime import datetime

class WebCam:
    """ Object to represent one of the security cameras at MRO """

    def __init__(self, name, URL, userName, password):
        self.name = name
        self.URL = URL
        self.userName = userName
        self.password = password
        self.lastImage = None
        

    def save_image(self, savePath):
        """ Uses http://IPAddress/image/jpeg.cgi to request current image, returns full path to new image. """

        imagePath = savePath + "/" + self.name + "_" + datetime.now().strftime("%m%d_%H%M%S") + '.jpg'
        with open(imagePath, 'wb') as f:
            c = pycurl.Curl()
            c.setopt( c.URL, self.URL + "/image/jpeg.cgi" )
            c.setopt( c.USERPWD, self.userName + ":" + self.password )
            c.setopt( c.WRITEDATA, f )
            try:
                c.perform()
            except:
                print "Error retrieving image from", self.name
            else:
                self.lastImage = imagePath
            c.close()

    

class WebCamHandler(object):
    """ Archive and post images to remote server from the MRO webcams.

    Sets up WebCam objects based on a file of format,

      name IP username password
    """

    def __init__(self):
        webcam_definition_file = "webcams.txt"
        
        self.archivePath = str(os.getcwd())+"/Archive/"
        self.archivePath = "/Users/ojf/Downloads/"
        self.remotePath = 'ovid:public_html/webcams/'
        self.remotePath = './'

        self.cameras = []  # list of all WebCam objects
        FILE = open(webcam_definition_file)
        for line in FILE:
            if line[0] == '#':
                continue
            self.cameras.append( WebCam(*line.split()) ) # *args "unwraps" the list from split()
        for camera in self.cameras:
            print "Setting up camera", camera.name


    def retrieve_images(self):
        """ Check for correct daily folder in archive, then save an image from each camera
        """
        path = self.archivePath + datetime.now().strftime("%Y%m%d")

        if os.path.exists( path + "/" ) == False:
            try:
                os.mkdir( path )
            except Exception as e:
                print "Error creating ", path, ": ", e

        for camera in self.cameras:
            camera.save_image(path)
            print "image archived from ", camera.name


    def post_images(self):
        """ Push image to remote server. """
        for camera in self.cameras:
            if camera.lastImage:
                shutil.copy(camera.lastImage, self.remotePath + camera.name + ".jpg")
                print "Posted image from", camera.name

    
if __name__ == "__main__":
    
    wh = WebCamHandler()

    run = True
    while run == True:
        try:
            wh.retrieve_images()
        except Exception as e:
            print e
        try:
            wh.post_images()
        except Exception as e:
            print e

        for i in xrange(300,-1,-1):
            sys.stdout.write('\r')
            sys.stdout.write('Sleeping: %02d seconds remaining' %i)
            sys.stdout.flush()
            time.sleep(1)
        print '\r\n'
