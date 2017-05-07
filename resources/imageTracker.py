from resources.resource import util
import pickle
import os
import csv
from PIL import Image
# order of files array is [vv,vh,fused,label]
#sort out paths issue

#Currently only works for jpeg/locale/vv/filelocation type structure
#only needs to be looked into for the updatepath func


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

    def changeLabel(self,old2new):
        if type(old2new) is not dict:
            print('Input must be dict of old label key - new label key')
            return False

        for basename in self.files:
            tmp = self.files[basename]
            label = tmp[3]
            if label in old2new:
                #Update label if havent alread
                if label in self.labels:
                    index = self.labels.index(label)
                    self.labels[index] = old2new[label]
                #Change label to new one
                label = old2new[label]

            tmp[3] = label
            self.files[basename] = tmp
        return True

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

    @staticmethod
    def getLocale(path):
        return os.path.split( os.path.split( os.path.split(path)[0])[0])[1]

    @staticmethod
    def getParentDir(path):
         return os.path.split(os.path.dirname(path))[1]

    def updatePath(self,path):
        # if not os.path.exists(path):
        #     print('Please input a valid path')
        #     return False
        for basename in self.files:
            tmp = self.files[basename]
            for i in range(len(tmp)-1):
                oldpath = tmp[i]
                if oldpath is not '':
                    imageName = os.path.split(oldpath)[1]
                    locale = self.getLocale(oldpath)
                    parent = self.getParentDir(oldpath)
                    pathConnnection = os.path.join(locale,parent)
                    newpath = os.path.join(path,pathConnnection)
                    newPath = os.path.join(newpath,imageName)
                    tmp[i] = newPath
            self.files[basename] = tmp
        return True

    def getLocaleList(self,locale):
        tmp = self.toList()
        tmp = [image[0] for image in tmp if self.getLocale(image[0]) == locale]
        return tmp

    def getLabelList(self,label):
        listImage = self.toList()
        tmp = []
        counter = {'0':0, '1':0}
        for image in listImage:
            count = counter[image[1]]
            count +=1
            counter.update({image[1]:count})
            if str(image[1]) == str(label):
                tmp.append(image)
        print(counter)
        return tmp

    def numLabels(self):
        return len(self.labels)

    def loadCsv(self,name):
        filePath = util.checkFolder('JPEGS',Input = True)
        filePath = os.path.join(filePath,name)
        images = {}
        with open(filePath,'r') as imageFile:
            read = csv.reader(imageFile,delimiter=';')
            first = True
            for row in read:
                if first:
                    first = False
                else:
                    basename = row.pop(0)
                    images.update({basename:row})
        return images



    def writeCsv(self,name=None):
        filePath= util.checkFolder('JPEGS',Input=True)
        if not name:
            name = 'tracker.csv'
        filePath= os.path.join(filePath,name)
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
        if len(imageList)==0:
            print('Check that image paths are correct')
        return imageList

    def reset(self, csvFile = None):
        self.files = {}
        self.labels = []
        self.add(self.loadCsv(csvFile))


    def getLabel(self,path):
        basename = self.getBasename(path)
        if basename in self.files:
            return self.files[basename][3]
        else: return None

    @staticmethod
    def getBasename(filepath):
        name = os.path.split(filepath)[1]
        return os.path.splitext(name)[0]

    @staticmethod
    def rotate(path,degree,image):
        if os.path.exists(path):
            return path
        else:
            imR = image.rotate(degree)
            imR.save(path)
            return path


    @staticmethod
    def getRotate(filepath):
        images = []
        dirpath = os.path.split(filepath)[0]
        dirpath = util.checkFolder('Rotate',path=dirpath)
        name = tracker.getBasename(filepath)

        name45 = os.path.join(dirpath, name + '45' + '.jpg')
        name90 =   os.path.join(dirpath, name + '90' + '.jpg')
        name135 =  os.path.join(dirpath, name +'135' + '.jpg')
        imageOG = Image.open(filepath)

        images.append(tracker.rotate(name45,45,imageOG))
        images.append(tracker.rotate(name90,90,imageOG))
        images.append(tracker.rotate(name135,135,imageOG))
        return images

    @staticmethod
    def getRotateList(images):
        print('Rotating images')
        tmp = []
        for image in images:
            value = image[1]
            tmp.append(image)
            rotatedIm = tracker.getRotate(image[0])
            for im in rotatedIm:
                tmp.append([im,value])
        print('Finished rotating images')

        return tmp


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
