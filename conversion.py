from resources.resource import util
from resources.resource import image as satImage
from resources.resource import notify
from resources.resource import tracker
from resources.notifications.notifyServer import server as notifyServer

import os,sys,time
from PIL import Image, ImageFile


import threading
import gdal


# server = notifyServer.getServer()
#
#
# serverThread = notifyServer.getServerThread()
# serverThread.start()
#         receiver.join()
#
#
#
# def stopProgram():
#     from resources.notifications.notify import notify
#     import sys
#     note = notify.getNotify()
#     note.push('Stopping program!')
#
#     sys.exit(1)
# server.addCommands({'stop':stopProgram})

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
            # try:
            print(imageVV.path)
            imageVV.fuseWith(imageVH,outputFolder=outputPath)
            # except MemoryError:
            #     mess='Memory issue, waiting for response'
            #     if notif:
            #         note.push(mess)
            #     else:
            #         print(mess)
            #     time.sleep(30)
    except KeyboardInterrupt:
        print('Exiting')
        # if server:
        #     server.exitFlag = 1
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
                label = '1'
            else:
                label = '0'
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
# stalker.saveTracker()
print(len(stalker.toList()))
# images = stalker.toList()
# allImages = stalker.getRotateList(images)
# # print(len(allImages))
# flipImages = stalker.getFlippedList(allImages)
# print(len(flipImages))
# train, evalList = stalker.getTrainEvallist(allImages,5)
# print(len(train))
# print(len(evalList))
# print
# balancedList =stalker.getBalancedList(allImages,[100,100])
# filePaths = [image[0] for image in balancedList]
# labels = [int(image[1]) for image in balancedList]


# counter ={0:0,1:0}
# for l in labels:
#     value = counter[l]
#     value +=1
#     counter.update({l:value})
#
# print(counter)

# for image in im:
#     if len(image) <=2:
#         print(image)
# labels = [int(image[1]) for image in im]
#
# print(labels)
# labels = [int(image[1]) for image in allImages]
# # stalker.writeCsv(name='trackerbeforeAt.csv')
# print(stalker.labels)
# print(len(stalker.getLabelList('1')))
# images = stalker.toList()
# allImages = stalker.getRotateList(images)
# print(images[0])
# filePaths = [image[0] for image in allImages]
# labels = [int(image[1]) for image in allImages)]
# print(stalker.getRoated(images))



# locale = 'Athlone'
# print(len(stalker.toList()))
# stalker.reset('trackerbeforeAt.csv')
# print(len(stalker.toList()))
# stalker.saveTracker()

# organise(locale)

# inputPath = util.checkFolder('Proccessed',Output=True)
# fuseImages(locale,inputPath=inputPath)
