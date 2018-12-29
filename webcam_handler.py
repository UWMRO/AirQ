""" webcam_handler.py
Requests security camera images, archives them, and forwards the latest to remote server. 
Naming convention assumes images come in slower than once per second.

Original by Matt Armstrong (~'17-'18), modified for direct links to webcams by OJF '19

Subprocess([curl... could be replaced with PycURL (default package) or requests (HTTP for Humans)
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
        ## necessary?
        #Minutes between image upload to server
        self.uploadInt = 5
        #Counter for uploadInt timer
        self.uploadCount = 0	                                    


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
        print "Setting up cameras:"
        for camera in self.cameras:
            print camera.name


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


    def post_images(self):
        """ Push image to remote server. """
        for camera in self.cameras:
            if camera.lastImage:
                shutil.copy(camera.lastImage, self.remotePath + camera.name + ".jpg")

        
    def sortFiles(self):
        """
        Create daily folder in archive, sort all jpg's that appear in inbox 
        into latest folder with a cleaned up name (cam_date_time.jpg)
        """
        fileList = []
        print('Starting File Search')
        # Set the directory you want to start from

        if os.path.exists(self.storagePath+datetime.now().strftime("%Y%m%d")+"/") == False:
            print "Changing Date"
            os.mkdir(self.storagePath+datetime.now().strftime("%Y%m%d"))
            return

        for dirName, subdirList, files in os.walk(self.inboxPath):
            #print('Found directory: %s' % dirName)
            #print('subdirlist: %s' % subdirList)
            for fname in files:
                if str(fname).endswith('.jpg'):
                    try:
                        pathName = os.path.join(dirName, fname)
                        fileList.append(pathName)
                        fcam, fdate, ftime, fjunk = fname.split("_")
                        newFName = fcam+'_'+fdate+'_'+ftime+'.jpg'
                        shutil.copy(pathName, self.storagePath+fdate+"/"+newFName)
                        os.remove(pathName)
                        print('Moved %s to Storage' %newFName)
                    except Exception as e:
                        print e
                        print "File error: %s" %fname
                else:
                    print "Removing %s" %fname
                    os.remove(os.path.join(dirName, fname))
            return

    def findNow(self):
        """ 
        Search storage path for images, use naming convention to find cameras,
        then the lastest image for each, which get moved to live directory,
        then upload contents of live directory to remote server.
        """
        now = datetime.now()
        dateStr = now.strftime("%Y%m%d")
        listFolders = os.listdir(self.storagePath)
        for i in range(len(listFolders)):
            listFolders[i] = int(listFolders[i])
        #lastFolder = sorted(listFolders)[-1]
        lastFolder = dateStr
        listLatest = os.listdir(self.storagePath+str(lastFolder)+'/')

        camList = []
        fileInfoList = []       #[fileName, camNum, camDate, camTime]
        camDict = {}
        camLatest = {}

        # Sort the images, make a list of all cameras and files
        for j in range(len(listLatest)):
            fileName = listLatest[j]
            try:
                camNum, camDate, camTime = fileName.split('_')
            except Exception as e:
                print "Error: %s. invalid file: %s" %(str(e),fileName)
                continue
            if camNum not in camList:
                camList.append(camNum)
            camTime = camTime.split('.')[0]
            fileInfoList.append([fileName, camNum, camDate, camTime])

        # Make a dictionary of all the active cameras
        for k in range(len(camList)):
            camDict[str(camList[k])] = []
            camLatest[str(camList[k])] = None

        # Add each camera time to the camera dictionary
        for l in range(len(fileInfoList)):
            for key, item in camDict.iteritems():
                if str(fileInfoList[l][1]) == str(key):
                    camDict[key].append(int(fileInfoList[l][3]))

        # Sort the times for each camera, find the latest image for each
        for key2, item in camDict.iteritems():
            sortedList = sorted(camDict[str(key2)])
            latestImg = sortedList[-1]

            latestFile = self.storagePath+str(lastFolder)+'/'+str(key2)+'_'+str(lastFolder)+'_%06d.jpg' %(latestImg)
            camLatest[str(key2)] = latestFile

        #remove all files in live directory
        try:
            for file in os.listdir(self.livePath):
                #print "Removing "+self.livePath+file
                os.remove(self.livePath+file)
        except Exception as e:
            print e

        #Move latest files to live directory
        for key3, item in camLatest.iteritems():
            shutil.copy(camLatest[str(key3)], self.livePath+str(key3)+'.jpg')
            os.chmod(self.livePath+str(key3)+'.jpg', 0755)
            print "Copied "+camLatest[str(key3)]+" to Live"

        #Upload latest files to remote server, print rsync output and error, reset upload counter
        self.uploadCount = self.uploadCount + 1
        print str(self.uploadInt-self.uploadCount)+' minutes until next upload to remote server'
        if self.uploadCount >= self.uploadInt:
            print "Uploading latest images to remote server"
            p = subprocess.Popen(['rsync -azrh --progress %s %s' %(self.livePath, self.remotePath)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = p.communicate()
            print stdout
            print stderr
            self.uploadCount = 0
	return

    
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

        for i in xrange(60,-1,-1):
            sys.stdout.write('\r')
            sys.stdout.write('Sleeping: %02d seconds remaining' %i)
            sys.stdout.flush()
            time.sleep(1)
        print '\r\n'
