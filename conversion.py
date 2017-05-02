from resources.resource import util
from resources.resource import image as satImage
from resources.resource import notify
from resources.resource import tracker

import os,sys
from PIL import Image, ImageFile

import gdal




Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True






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



def fuseImages(locale,notif=True,outputPath=None):
    if notif:
        note = notify.getNotify()
        note.push('Fusing images from %s' % locale)
    else: print('Fusing images from %s' % locale)

    directory = util.checkFolder('Proccessed', Output=True)
    tiff = util.checkFolder(locale,path=directory)
    tiffImages = tracker.parseFolder(tiff,findPosition=False, type='tif')
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

            # image = satImage(image).array()
            # im = Image.fromarray(image)
            #
            # im.thumbnail((1000,1000))
            # im.show()

            image.show()
            label = input('enter y for flood or n for none: ')
            label = 'y'
            label = label.lower()
            while label != 'y' and label != 'n':
                label = input('enter y for flood or n for none: ')
                print (label)
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

# stalker = tracker()
# stalker.files.update({'a':1})
# stalker.saveTracker()


locale = 'Brimach'
# stalker = tracker()
# print(stalker.files)
# stalker.writeCsv()
organise(locale)


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
