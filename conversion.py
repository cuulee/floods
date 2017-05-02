from resources import util
from resources.satellite.image import image as satImage
from resources.notifications.notify import notify
import os
import csv
from PIL import Image, ImageFile

import image_slicer
Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True

thumbnailSize = 299,299

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

def getBasename(filepath):
    name = os.path.split(filepath)[1]
    return os.path.splitext(name)[0]

def findImages(files,type,directory):
    vvhh = findPair(files,type)
    fusedDir = os.path.join(directory,'Fused')
    imageData = {}
    if os.path.exists(fusedDir):
        fusedFiles = parseFolder(fusedDir,findPosition=False,type='jpeg')

    for i in range(len(vvhh)):
        basename = getBasename(vvhh[i][0])
        for fusedImage in fusedFiles:
            if basename in fusedImage:
                tmp = vvhh[i]
                tmp.append(fusedImage)
                vvhh[i] = tmp

        if basename in imageData:
            print('Error file %s was already in dataset' % basename)
        imageData.update({basename:vvhh[i]})


    return imageData
    # for pair in vvhh:
    #     path = pair[0]
    #     print(getBasename(path))

def writeCsv(images,filePath):
    with open(filePath, 'w', newline='') as imageFile:
        writer = csv.writer(imageFile, delimiter=';')
        headers = ['BASENAME','VH','VV','LABEL']
        writer.writerow(headers)
        for basename in images:
            tmp = [basename]
            for value in images[basename]:
                tmp.append(value)
            writer.writerow(tmp)
    print('finished writing')

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

def fuseImages(locale,notif=True,outputPath=None):
    if notif:
        note = notify.getNotify()
        note.push('Fusing images from %s' % locale)
    else: print('Fusing images from %s' % locale)

    directory = util.checkFolder('Proccessed', Output=True)
    tiff = util.checkFolder(locale,path=directory)
    tiffImages = parseFolder(tiff,findPosition=False, type='tif')
    tiffPairs = findPair(tiffImages,'tif')

    if not outputPath:
        outputPath = util.checkFolder(locale, path=directory)
        outputPath = util.checkFolder('Fused',path=outputPath)

    for i,pair in enumerate(tiffPairs):
        if notif:
            note.push('fusing %d :%d'%(i+1,(len(tiffPairs))))

        imageVV, imageVH = satImage(pair[0],findPosition=True), satImage(pair[1],findPosition=True)
        imageVV.fuseWith(imageVH,outputFolder=outputPath)
        # print(imageVV.array().shape)
    if notif:
        note.push('Finished fusion')

def toJpeg(locale,inputPath =None,outputPath=None, fusion = False):
    directory = util.checkFolder('Proccessed', Output=True)

    if not inputPath:
        inputPath = util.checkFolder(locale,path=directory)
        if fusion:
            inputPath = util.checkFolder('Fused',path=inputPath)



    tiffImages = parseFolder(inputPath,findPosition=False, type='tif')

    if not outputPath:
        outputPath = util.checkFolder('JPEGS',path =directory)
        outputPath = util.checkFolder(locale,path=outputPath)
        if fusion:
            outputPath = util.checkFolder('Fused',path=outputPath)

    satImage(tiffImages[0]).convertTo('jpeg',outputPath=outputPath)
    # satImage(tiffImages[0]).getInfo()



    # print(tiffImages)


def labelImages(images,directory):
    for basename in images:
        image = images[basename][0]

        imagesList = image_slicer.main.split_image(image, 4)
        print(imagesList)
        # im = Image.open(image)
        # test = im.crop((0,0,0,0))
        # test.show()
        # im.thumbnail(thumbnailSize)
        # path = os.path.join(directory,basename)
        # im.save(path + ".thumbnail", "JPEG")
        break



def crop(Path, input, height, width, k, page, area):
    im = Image.open(input)
    imgwidth, imgheight = im.size
    for i in range(0,imgheight,height):
        for j in range(0,imgwidth,width):
            box = (j, i, j+width, i+height)
            a = im.crop(box)
            try:
                o = a.crop(area)
                o.save(os.path.join(Path,"PNG","%s" % page,"IMG-%s.png" % k))
            except:
                pass
            k +=1


locale = 'Simach'

directory = util.checkFolder('Proccessed', Output=True)
directory = util.checkFolder('JPEGS',path =directory)
jpegs = util.checkFolder(locale,path=directory)
images = parseFolder(jpegs,findPosition=False,type='jpg')
imageData = findImages(images,'jpg',jpegs)


thumbnails = util.checkFolder('thumb',jpegs)

iamgeData = labelImages(imageData,thumbnails)

# trackerFile = os.path.join(directory,'tracker.csv')
# writeCsv(imageData,trackerFile)

# fuseImages(locale)




# toJpeg(locale,fusion=True)



# #
#     jpegs = util.checkFolder('JPEGS', path=directory)
#     jpegs = util.checkFolder(locale,path=Jpegs)
    # jpgImages = parseFolder(jpegs,findPosition=False, type='jpeg')
#

# jpgPairs = findPair(jpgImages,'jpeg')





    # print(imageVH.path,imageVV.path)
    # imageVH.array()
    # break
