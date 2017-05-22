import os,sys
import shutil
import configparser
from math import radians, cos, sin, asin, sqrt

# sys.path.insert(0,'/home/karl/Documents/floods/')


Config = configparser.ConfigParser()
Config.read("./Settings.ini")




def checkFolder(folder, Input = False, Output=False, path=None ):
    try:
        folder = str(folder)
        rootDir = configSectionMap("Paths")['root']
        if os.path.exists(folder):
            print('Directory already exists')
            return
        #If not directory was given, use root
        if Input:
            folderPath=os.path.join(rootDir,'Inputs')
            folderPath= os.path.join(folderPath,folder)
        elif Output:
            folderPath= os.path.join(rootDir,'Outputs')
            folderPath= os.path.join(folderPath,folder)
        elif path:
            folderPath = os.path.join(path, folder)

        else:
            folderPath = os.path.join(rootDir, folder)

        if not (os.path.exists(folderPath)):
            print('Folder Not Found, Creating Directory: %s' % folder)
            os.makedirs(folderPath)

        return folderPath
    except:
        raise

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def parseFolder(directory, findPosition=True):
    #Check if variable was already created because of recursion
    if 'stats' not in locals() or 'stats' not in globals():
        stats = {}
    for file in os.listdir(directory):
        path = os.path.join(directory,file)
        if os.path.isdir(path):
            stats.update(parseFolder(path))
        else:
            try:
                image = SatImage(path,findPosition=findPosition)
                long, lat = image.long, image.lat
                stats.update({image.path: [lat,long]})
            except AttributeError:
                print("%s is not an image" % file)
    return stats

def comparePoint(images,distance, backgroundImages = None, moreInfo = False):
    close = []
    backgroundFound = {}
    for image in images:
        # use background folder to compare images with if provided
        if backgroundImages:
            otherImages = backgroundImages
        else:
            otherImages = images

        for otherImage in otherImages:
            #Check if names are the same
            sameName = os.path.basename(image) == os.path.basename(otherImage)
            if image is not otherImage and not sameName:
                lat1,lon1 = images[image][0], images[image][1]
                lat2, lon2 = otherImages[otherImage][0], otherImages[otherImage][1]
                dis = self.haversine(lat1 ,lon1,lat2,lon2)

                if dis <= distance:
                    tmp1 = [image,otherImage]
                    tmp2 = [otherImage,image]
                    #Check if pair appears in table
                    if tmp1 not in close and tmp2 not in close:
                        close.append([image,otherImage])
                        backgroundFound.update({image:1})
    if moreInfo:
        noBackground = []
        for image in images:
            if image not in backgroundFound:
                noBackground.append(image)

        return [close,backgroundFound, noBackground]
    return close

def moveFile(path, dst):
    # name = os.path.basename(path)
    # folderName = name[14:18]
    # folderPath = self.checkFolder(folderName, path=dst)
    # fileDst = os.path.join(folderPath,name)
    shutil.copy(path, dst )
    os.remove(path)

def sortImages(similiarImages, hasBackground, noBackground):
    #VERIFY BEFORE USING AGAIN **************
    close = {}
    for images in similiarImages:
        if images[0]  not in close:
            close.update({images[0] : [1,[images[1]]]} )
        else:
            tmp = close[images[0]]
            count = tmp[0]
            count += 1
            tmpList = tmp[1]
            tmpList.append(images[1])
            close.update( {images[0]:[count,tmpList] })


    sFileName = 'ImageStats.txt'
    infoFolder = self.checkFolder('Info')
    writeFile = os.path.join(infoFolder,sFileName)

    #Check how many imageStats file are there
    if os.path.isfile(writeFile):
        dirFiles = os.listdir(checkFolder('Info'))
        foundFile = False
        index = -1
        while not foundFile:

            lastFile = dirFiles[index]
            if sFileName[:-4] in lastFile:
                # Finds the index of the numbers
                numIndex = lastFile.index(sFileName[:-4]) + len(sFileName[:-4])
                endIndex = lastFile.index('.txt')
                num = lastFile[numIndex:endIndex]
                try:
                    num = int(num) +1
                    newFileName = sFileName[:-4] + str(num) + '.txt'
                    writeFile = os.path.join(infoFolder, newFileName)
                    foundFile = True

                except ValueError:
                    'Error: could not find int in %s' % lastFile
                    return False
            else:
                index = index -1

    with open(writeFile, 'w') as file:
        file.write('Total Count \n')
        file.write('Files in folder: %s \n' % len(inputImages))
        file.write('No background: %s ** ' % len(noBackground))
        file.write('Has background: %s' % len(hasBackground))
        file.write('\n')


        file.write('No background images \n')
        for key in noBackground:
            file.write('Name : %s \n' %key)
            dst = self.checkFolder('NoBackground', Input=True)
            moveFile(key,dst)

        file.write('**********\n')
        file.write('Has background image')
        for key in hasBackground:
            file.write('Name : %s \n' %key)
            dst = self.checkFolder('HasBackground', Input=True)
            moveFile(key,dst)

        file.write('**********\n')
        file.write('Similiar images')

        for key in close:
            if key in noBackground:
                print('WRONGGGGGG')
                print(key)

            if key not in hasBackground:
                print('Super Wrong')
                print(key)
            tmp = close[key]
            count = tmp[0]
            bList = tmp[1]
            files = ''
            for i in bList:
                files += i + ' ** '
            file.write("%s -- Count: %s -- Files: %s \n" %(key, count, files))
            file.write('\n')

    return True

def configSectionMap(section):
    tmp = {}

    options = Config.options(section)
    for option in options:
        try:
            tmp[option] = Config.get(section, option)
            if tmp[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            tmp[option] = None
    return tmp
