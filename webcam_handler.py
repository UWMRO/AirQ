"""
webcam_handler.py

Used to manage the stream of security camera images
by cleaning up the naming protocol and transferring
the images to a storage directory and a live display
directory. The live images are automatically synced
with a remote server that hostss the latest imagery.
"""

import os, shutil, subprocess, glob, time, sys
from datetime import datetime


class WebcamHandler(object):

    def __init__(self):
        self.storagePath = str(os.getcwd())+"/Webcams/Storage/"
        self.inboxPath = str(os.getcwd())+"/security-cameras/"
        self.livePath = str(os.getcwd())+"/Webcams/Live/"

    def sortFiles(self):
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
        return

    def findNow(self):
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

        subprocess.Popen(['rsync -azrh --progress '+self.livePath+' ovid:public_html/'], stdout=subprocess.PIPE, shell=True)
        return
if __name__ == "__main__":
    wh = WebcamHandler()

    run = True
    while run == True:
        try:
            wh.sortFiles()
            wh.findNow()
        except Exception as e:
            print e
        for i in xrange(60,-1,-1):
            sys.stdout.write('\r')
            sys.stdout.write('Sleeping: %02d seconds remaining' %i)
            sys.stdout.flush()
            time.sleep(1)
        print '\r\n'

        
