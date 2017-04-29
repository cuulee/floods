from resources import util
from resources.satellite.image import image as satImage
import os
import Image


def parseFolder(directory, findPosition=True):
    #Check if variable was already created because of recursion
    if 'stats' not in locals() or 'stats' not in globals():
        stats = []
    for file in os.listdir(directory):
        path = os.path.join(directory,file)
        if os.path.isdir(path):
            stats =  stats +parseFolder(path)
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

    name = os.path.basename(path)
    if name.endswith(vh):
        return name[:-6] + 'VV.tif'

    elif name.endswith(vv):
        return name[:-6] + 'VH.tif'

    elif name.endswith('tif'):
        return name

def getSimPath(path):
    paths = os.path.split(os.path.dirname(path))
    # check directory above if its vh or vv
    if paths[1] == 'VH':
        return os.path.join(paths[0],'VV')
        pass

    elif paths[1] == 'VV':
        return os.path.join(paths[0],'VH')
        pass

def findPair(files):
    pairs = []
    i = 1
    for path in files:
        if isVer(path):
            vh = getSimPath(path)
            vh = os.path.join(vh,getSimName(path))

            if vh in files:
                # files.remove(path)
                files.remove(vh)
                pairs.append([path,vh])
            else:

                print('cant find match for %s' % path)


        elif isHor(path):
            vv= getSimPath(path)
            vv = os.path.join(vv,getSimName(path))

            if vv in files:
                # files.remove(path)
                files.remove(vv)
                pairs.append([vv,path])
            else:

                print('cant find match for %s' % path)

    return pairs


def writeCsv(images,filePath):
    with open(filePath, 'w', newline='') as imageFile:
        writer = csv.writer(imageFile, delimiter=';')
        headers = ['VH','VV','LABEL']
        writer.writerow(header)

def parseImages(images):
    imageInfo = []
    for imagePair in images:
        imagevv = images[0]
        imagevh = images[1]

        image = Image.open(imagevv)
        image.show()
        label = input('Enter f for flood or f for none')
        label = label.lower()
        while label not 'f' or label not 'n':
            label = input('Enter f for flood or f for none')
            label = label.lower()        label = label.lower()
        tmp = [imagevv,imagevh,label]
        imageInfo.append(tmp)







directory = '/media/karl/My Passport/Sat/Proccessed'
athlone = util.checkFolder('Athlone', path=directory)



images = parseFolder(athlone,findPosition=False)




pairs = findPair(images)
firstPair = pairs[0]

ima = satImage(firstPair[0])
ima.convertTo('jpeg',outputPath='/home/karl/Documents/floods')
# satImage.toJpeg(ima.path,'/home/karl/Documents/floods')

# print(ima.getInfo())
