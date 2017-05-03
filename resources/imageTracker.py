from resources.resource import util
import pickle
import os
import csv


class tracker(object):
    files = {}
    labels = []

    def __init__(self,trackerPath=None):

        self.loadTracker()


    def loadTracker(self):
        trackName = 'tracker.pkl'
        trackerPath = util.checkFolder('JPEGS',Input=True)
        self.path = os.path.join(trackerPath,trackName)

        if os.path.isfile(self.path):
            try:
                with open(self.path, 'rb') as input:
                    track =  pickle.load(input)
                    self.files = track.files
                    self.labels = track.labels
            except:
                return
        else: return

    def saveTracker(self):
        with open(self.path, 'wb') as output:
            pickle.dump(self,output, pickle.HIGHEST_PROTOCOL)

    def add(self,images,overwrite = False):
        for basename in images:
            try:
                tmp = images[basename]
                label = tmp[3].lower()
                tmp[3] = label

                if basename in self.files and overwrite:
                    self.files.update({basename:tmp})
                    if label not in self.labels:
                        self.labels.append(lable)
                elif basename not in self.files:
                    self.files.update({basename:tmp})
                    if label not in self.labels:
                        self.labels.append(label)
            except IndexError:
                print(images[basename])

    def numLabels(self):
        return len(self.labels)

    def writeCsv(self):
        filePath= util.checkFolder('JPEGS',Input=True)
        filePath= os.path.join(filePath,'tracker.csv')
        with open(filePath, 'w', newline='') as imageFile:
            writer = csv.writer(imageFile, delimiter=';')
            headers = ['BASENAME','VH','VV','FUSED','LABEL']
            writer.writerow(headers)
            for basename in self.files:
                tmp = [basename]
                for value in self.files[basename]:
                    tmp.append(value)
                writer.writerow(tmp)
        print('finished writing')

    def toList(self):
        imageList = []
        for basename in self.files:
            label = self.files[basename][3]
            for path in self.files[basename]:
                if os.path.exists(path):
                    imageList.append([path,label])
        return imageList

    def reset(self, csvFile = None):
        self.files = {}
        self.labels = []

    @staticmethod
    def getBasename(filepath):
        name = os.path.split(filepath)[1]
        return os.path.splitext(name)[0]

    @staticmethod
    def isVer(path):
        dirAbove = os.path.split(os.path.dirname(path))[1]
        return dirAbove == 'VV'

    @staticmethod
    def isHor(path):
        dirAbove = os.path.split(os.path.dirname(path))[1]
        return dirAbove == 'VH'

    @staticmethod
    #Returns list of files paths in directory
    def parseFolder(directory, findPosition=True,type =None, ignoreDir=[]):
        #Check if variable was already created because of recursion
        if 'stats' not in locals() or 'stats' not in globals():
            stats = []
        for file in os.listdir(directory):
            path = os.path.join(directory,file)
            if os.path.isdir(path):
                folder = str(os.path.split(path)[1])
                if folder not in ignoreDir:
                    stats =  stats + tracker.parseFolder(path,findPosition=findPosition,type = type,ignoreDir=ignoreDir)
            else:
                if type:
                    if path.endswith(type):
                        stats.append(path)
                else:
                    stats.append(path)
        return stats

    @staticmethod
    #retuns the basename for the vv,vh images
    def getSimName(path,type):

        vh = 'VH.%s' % type
        vv = 'VV.%s' % type
        removeLength = len(type) + 3
        name = os.path.basename(path)
        if name.endswith(vh):
            return name[:-removeLength] + vv

        elif name.endswith(vv):
            return name[:-removeLength] + vh

        elif name.endswith(type):
            return name

    @staticmethod
    #Returns the directory where the other band should be
    def getSimPath(path):
        paths = os.path.split(os.path.dirname(path))
        # check directory above if its vh or vv
        if paths[1] == 'VH':
            return os.path.join(paths[0],'VV')


        elif paths[1] == 'VV':
            return os.path.join(paths[0],'VH')

    @staticmethod
    #Finds list of VV,VH images and return them in a list of lists
    def findPair(files,type):
        pairs = []
        i = 1
        for path in files:
            try:
                if tracker.isVer(path):
                    vh = tracker.getSimPath(path)
                    vh = os.path.join(vh,tracker.getSimName(path,type))

                    if vh in files:
                        # files.remove(path)
                        files.remove(vh)
                        pairs.append([path,vh])
                    else:

                        print('cant find match for %s' % path)


                elif tracker.isHor(path):
                    vv= tracker.getSimPath(path)
                    vv = os.path.join(vv,tracker.getSimName(path,type))

                    if vv in files:
                        # files.remove(path)
                        files.remove(vv)
                        pairs.append([vv,path])
                    else:

                        print('cant find match for %s' % path)
            except TypeError:
                print('Error finding matching file, Check if file type is correct')

        return pairs

    @staticmethod
    #Returns dict of basename file name with list of [vv,vh,fused images] in directory path, within a locale directory type
    def findImages(files,type,directory):
        vvhh = tracker.findPair(files,type)
        fusedDir = os.path.join(directory,'Fused')
        imageData = {}
        fusedFiles = None
        if os.path.exists(fusedDir):
            fusedFiles = tracker.parseFolder(fusedDir,findPosition=False,type='jpeg')

        for i in range(len(vvhh)):
            basename = tracker.getBasename(vvhh[i][0])
            tmp = vvhh[i]
            tmp.append('')
            if fusedFiles:
                for fusedImage in fusedFiles:
                    if basename in fusedImage:
                        tmp[2] = fusedImage

            vvhh[i] = tmp

            if basename in imageData:
                print('Error file %s was already in dataset' % basename)
            imageData.update({basename:vvhh[i]})

        return imageData
