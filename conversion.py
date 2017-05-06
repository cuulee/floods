from resources.resource import util
from resources.resource import image as satImage
from resources.resource import notify
from resources.resource import tracker
from resources.notifications.notifyServer import server as notifyServer

import os,sys,time
from PIL import Image, ImageFile

import gdal


# global server
# server = notifyServer.getServer()
#
#
# def stopProgram():
#     from resources.notifications.notify import notify
#     import sys
#     note = notify.getNotify()
#     note.push('Stopping program!')
#     server.exitFlag = 1
#
#     sys.exit(1)
#
# server.addCommands({'stop!':stopProgram})


Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True


def fuseImages(locale,inputPath=None,notif=True,outputPath=None):
    if notif:
        note = notify.getNotify()
        note.push('Fusing images from %s' % locale)
    else: print('Fusing images from %s' % locale)
    if not inputPath:
        inputPath = util.checkFolder('JPEGS', Input=True)
    tiff = util.checkFolder(locale,path=inputPath)
    tiffImages = tracker.parseFolder(tiff,findPosition=False, type='tif')
    tiffPairs = tracker.findPair(tiffImages,'tif')

    if not outputPath:
        outputPath = util.checkFolder(locale, path=inputPath)
        outputPath = util.checkFolder('Fused',path=outputPath)

    try:
        for i,pair in enumerate(tiffPairs):
            if notif:
                note.push('fusing %d :%d'%(i+1,(len(tiffPairs))))

            imageVV, imageVH = satImage(pair[0],findPosition=True), satImage(pair[1],findPosition=True)
            try:
                imageVV.fuseWith(imageVH,outputFolder=outputPath)
            except MemoryError:
                mess='Memory issue, waiting for response'
                if notif:
                    note.push(mess)
                else:
                    print(mess)
                time.sleep(30)
    except KeyboardInterrupt:
        print('Exiting')
        if server:
            server.exitFlag = 1
        sys.exit()

        # print(imageVV.array().shape)
    if notif:
        note.push('Finished fusion')

def toJpeg(locale,inputPath =None,outputPath=None, fusion = False):
    directory = util.checkFolder('Proccessed', Output=True)

    if not inputPath:
        inputPath = util.checkFolder(locale,path=directory)
        if fusion:
            inputPath = util.checkFolder('Fused',path=inputPath)



    tiffImages = tracker.parseFolder(inputPath,findPosition=False, type='tif')

    if not outputPath:
        outputPath = util.checkFolder('JPEGS',path =directory)
        outputPath = util.checkFolder(locale,path=outputPath)
        if fusion:
            outputPath = util.checkFolder('Fused',path=outputPath)

    satImage(tiffImages[0]).convertTo('jpeg',outputPath=outputPath)
    # satImage(tiffImages[0]).getInfo()



    # print(tiffImages)

def labelImages(images): #Takes in
    try:
        for basename in images:
            tmp = images[basename]
            image = satImage(tmp[0])
            print(image)

            image.show()
            label = input('enter y for flood or n for none: ')
            label = label.lower()
            while label != 'y' and label != 'n':
                label = input('enter y for flood or n for none: ')
                label = label.lower()
            if label == 'y':
                label = 'Flood'
            else:
                label = 'None'
            satImage.killDisplay()

            tmp.append(label)

            images.update({basename:tmp})

        return images
    except KeyboardInterrupt:
        print('Exiting')
        satImage.killDisplay()

        sys.exit()

def organise(locale):
    directory = util.checkFolder('JPEGS',Input=True)
    directory = util.checkFolder(locale,path=directory)
    images = tracker.parseFolder(directory,findPosition=False,type='jpg')
    imageData = tracker.findImages(images,'jpg',directory)
    imageData = labelImages(imageData)
    stalker = tracker()
    stalker.add(imageData)
    stalker.saveTracker()

stalker = tracker()
# stalker.files.update({'a':1})
# stalker.saveTracker()



locale = 'Athlone'
inputPath = util.checkFolder('Proccessed',Output=True)
fuseImages(locale,inputPath=inputPath)
# directory = util.checkFolder('JPEGS', Input=True)
# tiff = util.checkFolder(locale,path=directory)
# tiffImages = tracker.parseFolder(tiff,findPosition=False, type='jpg')
# image = satImage(tiffImages[0])
# image.show()
# tiffPairs = tracker.findPair(tiffImages,'jpg')
# organise(locale)
# a = None
# for key in stalker.files:
#     a = key
#     print(stalker.files[a])
#     break

# print(stalker.updatePath('/media/karl/My Files2/Project/Resources/JPEGS'))
# print(stalker.files[a])
# stalker.saveTracker()
# stalker.writeCsv('trackerafter.csv')





# a  =['A','B','C']
# b = [char.lower() for char in a ]
# print(b)


# locale = 'Simach'
#
# directory = util.checkFolder(locale)
# # directory = util.checkFolder('JPEGS',path =directory)
# # jpegs = util.checkFolder(locale,path=directory)
# images = tracker.parseFolder(directory,findPosition=False,type='jpg',ignoreDir=['Old'])
#
#
# thumbnails = util.checkFolder('thumb',path=directory)
# imageData = labelImages(imageData,thumbnails)

# trackerFile = os.path.join(directory,'tracker.csv')
# writeCsv(imageData,trackerFile)

# fuseImages(locale)




# toJpeg(locale,fusion=True)



# #
#     jpegs = util.checkFolder('JPEGS', path=directory)
#     jpegs = util.checkFolder(locale,path=Jpegs)
    # jpgImages = tracker.parseFolder(jpegs,findPosition=False, type='jpeg')
#

# jpgPairs = findPair(jpgImages,'jpeg')





    # print(imageVH.path,imageVV.path)
    # imageVH.array()
    # break
