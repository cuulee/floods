from resources import util
from resources.satellite.image import image as satImage
from resources.notifications.notify import notify
import os
from PIL import Image

def parseFolder(directory, findPosition=True,type =None):
    #Check if variable was already created because of recursion
    if 'stats' not in locals() or 'stats' not in globals():
        stats = []
    for file in os.listdir(directory):
        path = os.path.join(directory,file)
        if os.path.isdir(path):
            stats =  stats +parseFolder(path,findPosition=findPosition,type = type)
        else:
            if type:
                if path.endswith(type):
                    stats.append(path)
            else:
                stats.append(path)


    return stats

def isVer(path):
    dirAbove = os.path.split(os.path.dirname(path))[1]
    return dirAbove == 'VV'

def isHor(path):
    dirAbove = os.path.split(os.path.dirname(path))[1]
    return dirAbove == 'VH'

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

def getSimPath(path):
    paths = os.path.split(os.path.dirname(path))
    # check directory above if its vh or vv
    if paths[1] == 'VH':
        return os.path.join(paths[0],'VV')


    elif paths[1] == 'VV':
        return os.path.join(paths[0],'VH')

def findPair(files,type):
    pairs = []
    i = 1
    for path in files:
        try:
            if isVer(path):
                vh = getSimPath(path)
                vh = os.path.join(vh,getSimName(path,type))

                if vh in files:
                    # files.remove(path)
                    files.remove(vh)
                    pairs.append([path,vh])
                else:

                    print('cant find match for %s' % path)


            elif isHor(path):
                vv= getSimPath(path)
                vv = os.path.join(vv,getSimName(path,type))

                if vv in files:
                    # files.remove(path)
                    files.remove(vv)
                    pairs.append([vv,path])
                else:

                    print('cant find match for %s' % path)
        except TypeError:
            print('Error finding matching file, Check if file type is correct')

    return pairs

def writeCsv(images,filePath):
    with open(filePath, 'w', newline='') as imageFile:
        writer = csv.writer(imageFile, delimiter=';')
        headers = ['VH','VV','LABEL']
        writer.writerow(header)

def parseImages(images):
    imageInfo = []
    for imagePair in images:
        imagevv = imagePair[0]
        imagevh = imagePair[1]
        print(imagevv)
        image = Image.open(imagevv)
        image.show()
        label = input('Enter f for flood or f for none')
        label = label.lower()
        while label is not 'f' or label is not 'n':
            label = input('Enter f for flood or f for none')
            label = label.lower()
        tmp = [imagevv,imagevh,label]
        imageInfo.append(tmp)


note = notify.getNotify()

locale = 'Simach'

directory = util.checkFolder('Proccessed', Output=True)
brimJpegs = util.checkFolder('JPEGS', path=directory)
brimJpegs = util.checkFolder(locale,path=brimJpegs)
brimTiff = util.checkFolder(locale,path=directory)

# jpgImages = parseFolder(brimJpegs,findPosition=False, type='jpeg')
tiffImages = parseFolder(brimTiff,findPosition=False, type='tif')


# jpgPairs = findPair(jpgImages,'jpeg')
tiffPairs = findPair(tiffImages,'tif')

outputPath = util.checkFolder(locale, path=directory)
outputPath = util.checkFolder('Fused',path=outputPath)
print(outputPath)

for i,pair in enumerate(tiffPairs):
    note.push('fusing %d :%d'%(i+1,len(tiffPairs)))
    imageVV, imageVH = satImage(pair[0],findPosition=True), satImage(pair[1],findPosition=True)
    imageVV.fuseWith(imageVH,outputFolder=outputPath)
    # print(imageVH.path,imageVV.path)
    # imageVH.array()
    # break
