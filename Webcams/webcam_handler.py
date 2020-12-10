""" webcam_handler.py [camera definition file]

Requests and archives webcam images, then and forwards the latest to a remote server. 
Uses Pycurl to retrieve images via http, Paramiko to push them to the server via ssh.

Camera definition file format is:

      name URL username password

The URL is the specific call that returns a single image. Note that the
naming convention assumes images come in slower than once per second.

Original by Matt Armstrong (~'17-'18)
modified for direct access to webcams by OJF '19

Note: Will fail if:
- the archive directory doesn't exist
- if the camera definition file has blank lines

ToDo: Exceptions don't print or pass their exceptions up
"""

import os, shutil, subprocess, glob, time, sys
import pycurl # retrieve
from paramiko import SSHClient
from datetime import datetime

class WebCam:
    """ Object to represent one of the webcams at MRO """

    def __init__(self, name, URL, userName, password):
        self.name = name
        self.URL = URL
        self.userName = userName
        self.password = password
        self.lastImage = None
        

    def retrieve_image(self, savePath):
        """ Request (via http) and save current image. Returns full path to new image. """

        imagePath = savePath + "/" + self.name + "_" + datetime.now().strftime("%m%d_%H%M%S") + '.jpg'
        with open(imagePath, 'wb') as f:
            c = pycurl.Curl()
            c.setopt( c.URL, self.URL)
            c.setopt( c.USERPWD, self.userName + ":" + self.password )
            c.setopt( c.WRITEDATA, f )
            try:
                c.perform()
            except:
                print( "Error retrieving image from", self.name )
            else:
                self.lastImage = imagePath
            c.close()

    

class WebCamHandler(object):
    """ Archive and post images to remote server from the MRO webcams.

    Sets up WebCam objects based on a file of format:

      name URL username password

    where the URL returns a single image
    """

    def __init__(self, webcam_definition_file):
        
        self.archivePath = "/home/ojf/Pictures/MRO_Webcams/"
        self.remotePath = 'public_html/webcams/'
        self.remoteHost = 'ovid.u.washington.edu'
        self.user = 'mrouser'
        self.cameras = []  # list of all WebCam objects

        FILE = open(webcam_definition_file)
        for line in FILE:
            if line[0] == '#':
                continue
            self.cameras.append( WebCam(*line.split()) ) # *args "unwraps" the list from split()
        for camera in self.cameras:
            print( "Setting up camera", camera.name )


    def retrieve_and_archive_images(self):
        """ Check for correct daily folder in archive, then save an image from each camera
        """
        path = self.archivePath + datetime.now().strftime("%Y%m%d")

        if os.path.exists( path + "/" ) == False:
            try:
                os.mkdir( path )
            except Exception as e:
                print( "Error creating ", path, ": ", e )

        for camera in self.cameras:
            camera.retrieve_image(path)
            print( datetime.now().strftime("%m/%d %H:%M"), ": image archived from ", camera.name )


    def post_images(self):
        """ Push images to remote server. """
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(self.remoteHost, username=self.user)
        sftp = ssh.open_sftp()
        
        for camera in self.cameras:
            if camera.lastImage:
                sftp.put(camera.lastImage, self.remotePath + camera.name + ".jpg")
                print( datetime.now().strftime("%m/%d %H:%M"), ": Posted image from", camera.name )
        sftp.close()
        ssh.close()


    
if __name__ == "__main__":

    try:
        camera_definition_file = sys.argv[1]
    except IndexError as e:
        print( "Usage:", sys.argv[0], "[camera definition file]")
        exit()

    handler = WebCamHandler(sys.argv[1])

    while True:
        try:
            handler.retrieve_and_archive_images()
        except Exception as e:
            print( e )
        try:
            handler.post_images()
        except Exception as e:
            print( e )

        for i in xrange(300,-1,-1):
            sys.stdout.write('\r')
            sys.stdout.write('Sleeping: %02d seconds remaining' %i)
            sys.stdout.flush()
            time.sleep(1)
        print( '\r\n' )