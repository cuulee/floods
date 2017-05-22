from resources.resource import util
from resources.resource import image as satImage
from resources.resource import notify
from resources.resource import tracker
from resources.notifications.notifyServer import server as notifyServer

import os,sys,time
from PIL import Image, ImageFile


import threading
import gdal




Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True

#Fuses images vertical and horizontal images together based on locale
#CAN KILL PROGRAM DUE TO VERY HIGH RAM USAGE** CAUTION, REQUIRES HIGH END MACHINE

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
            imageVV.fuseWith(imageVH,outputFolder=outputPath)

    except KeyboardInterrupt:

        sys.exit()

    if notif:
        note.push('Finished fusion')
