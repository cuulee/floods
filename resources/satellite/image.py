import os, gc, traceback,  sys
import gdal
from osgeo import gdalconst
import datetime
import subprocess
from resources.resource import util
from subprocess import Popen
# from arcgis.gis import GIS
from IPython.display import display
from skimage import io
import pywt
import numpy as np
from PIL import Image, ImageFile
import numpy as np
import psutil
from pympler import asizeof

Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True


def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.CE_None:'None',
            gdal.CE_Debug:'Debug',
            gdal.CE_Warning:'Warning',
            gdal.CE_Failure:'Failure',
            gdal.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    print('Error Number: %s' % (err_num) )
    print ('Error Type: %s' % (err_class))
    print ('Error Message: %s' % (err_msg))

gdal.PushErrorHandler(gdal_error_handler)

class image:

    displaySize = 1000,1000


    def __init__(self,path, findPosition=False ):
        try:
            if not os.path.exists(path):
                raise IOError("Can't find image")
            self.path = path
            self.name = os.path.basename(path)

            self.dataset = gdal.Open(path)
            if findPosition:
                self.getSat()
        except IOError as e :
            print(str(e))

    def __str__(self):
        try:
            return getattr(self, "path")
        except AttributeError:
            return 'None'

    # gets meta data of image
    def getMeta(self):
        if not hasattr(self,'meta'):
            self.meta = self.dataset.GetMetadata()
        return self.meta

    #Converts pixel coordinates to real world point
    def toLongLat(self,points):
        iFile = 'coords.txt'
        oFile = 'longlat.txt'
        with open(iFile, 'w') as inputF:
            for point in points:
                tmp = "%s %s \n" %(str(point[0]) ,str(point[1]))
                inputF.write(tmp)

        transform = "gdaltransform '%s'  <%s >%s" % (self.path, iFile, oFile)
        os.system(transform)
        with open(oFile, 'r') as outF:
            coords = []
            for line in outF:
                longlat = line.split(' ')
                coords.append((list(map(float, longlat[:-1]))))
        os.remove(iFile)
        os.remove(oFile)
        return(coords)

    #Converts real world points to pixels in image
    def toPixel(self,points):
        if type(points[0]) is not list:
            points = [points]
        iFile = 'coords.txt'
        oFile = 'longlat.txt'
        with open(iFile, 'w') as inputF:
            for point in points:
                tmp = "%s %s \n" %(str(point[0]) ,str(point[1]))
                inputF.write(tmp)

        transform = "gdaltransform -i '%s'  <%s >%s" % (self.path, iFile, oFile)
        os.system(transform)

        with open(oFile, 'r') as outF:
            coords = []
            for line in outF:
                longlat = line.split(' ')
                coords.append(list(map(round,map(float, longlat[:-1]))))
        os.remove(iFile)
        os.remove(oFile)
        return(coords)

    #Gets corner pixels of image
    def getCorners(self):
        gt = self.dataset.GetGeoTransform()
        cols = self.dataset.RasterXSize
        rows = self.dataset.RasterYSize
        points= []
        xarr=[0,cols]
        yarr=[0,rows]
        for px in xarr:
            for py in yarr:
                x=gt[0]+(px*gt[1])+(py*gt[2])
                y=gt[3]+(px*gt[4])+(py*gt[5])
                points.append([x,y])
            yarr.reverse()

        return points

    #Gets centre of image
    def getCentroid(self):
        points = self.getCorners()
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid = [sum(x) / len(points), sum(y) / len(points)]
        return centroid

    #Sets the long lat of image centroid and returns values in long/lat order
    def getSat(self):
        try:
            centroid = self.getCentroid()
            #toLongLat look for an array of points to convert
            centroid = self.toLongLat([centroid])
            self.long, self.lat = float(centroid[0][0]), float(centroid[0][1])
            return self.long,self.lat
        except:
            return

    # Prints the info of image
    def getInfo(self):
        print(gdal.Info( self.dataset))


    #Parses date in the standard name format by esa
    def getDate(self,string):
        try:
            year = int(string[6:10])
            month = int(string[10:12])
            day = int(string[12:])
            date = datetime.date(year,month,day)
            return date
        except ValueError:
            return datetime.now()

    #Converts image to some format, only has jpeg
    def convertTo(self,type, outputPath=None):
        types = {'jpeg' :['.jpeg', self.toJpeg ]}

        if not outputPath:
            outputPath = util.checkFolder('Tiff', Output=True)
            outputPath = os.path.join(outputPath,'test.tiff')

        elif os.path.exists(os.path.dirname(outputPath)):
            outputName = self.name.split('.')[0] + types[type][0]
            outputPath = os.path.join(outputPath,outputName)

        print('Converting image to %s' %types[type][0][1:])
        types[type][1](self.path,outputPath)
        print('Finished image to %s' %types[type][0])


    # Converts image to jpeg
    @staticmethod
    def toJpeg(inputPath, outputPath):
        convert = ['gdal_translate','-of', 'JPEG' , '-outsize', '25%', '25%' ,  '-ot', 'Byte', '-scale',inputPath, outputPath ]
        proc = subprocess.Popen(convert)
        proc.wait()


    #Kills the image after displaying it
    @staticmethod
    def killDisplay():
        for proc in psutil.process_iter():
            if proc.name() == "display":
                proc.kill()

    #Display image on screen
    def show(self,size=None):
        if not size:
            size = self.displaySize
        im = Image.fromarray(self.array())

        im.thumbnail((1000,1000))
        im.show()

    # Colours image depedning on colour-relief file
    def colourImage(self, colour, *args):
        colour = os.path.join(util.checkFolder('Colour') , colour)
        if os.path.exists(colour):
            output = util.checkFolder('Outputs')
            output = util.checkFolder('Colour',output)
            if len(args) is not 0:
                oType = args[0].upper()
                output =  util.checkFolder(oType,output)
                name = self.name.split('.')[0] + '.' + oType.lower()
                oFile = os.path.join(output,name)
                gdaldem = ['gdaldem', 'colour-relief' , self.path, colour, oFile, 'of', oType ]
            else:
                output =  checkFolder(self.name.split('.')[1],output)
                name = self.name
                oFile = os.path.join(output,name)
                gdaldem = ['gdaldem', 'color-relief',  self.path, colour, oFile ]
            proc = subprocess.Popen(gdaldem)
            proc.wait()
            print("Colour relief for %s was created"% oFile)

        else : print('Could not find colour file %s' %colour)

    #returns image as an array
    def array(self,band=None):

        try:
            if not band:

                tmp = np.asarray(self.dataset.GetRasterBand(1).ReadAsArray())
                return tmp
            else:
                return np.asarray(self.dataset.GetRasterBand(band).ReadAsArray())
        except ValueError:
            return None

    #Gets intersection of two borders
    def getIntersection(self,r1Coords,r2Coords):
        tmp = []
        if r1Coords[0][0] < r2Coords[0][0]:
            tmp.append(r1Coords[0])
        else: tmp.append(r2Coords[0])
        if r1Coords[1][1] < r2Coords[1][1]:
            tmp.append(r1Coords[1])
        else: tmp.append(r2Coords[1])
        if r1Coords[2][0] > r2Coords[2][0]:
            tmp.append(r1Coords[2])
        else: tmp.append(r2Coords[2])
        if r1Coords[3][1] > r2Coords[3][1]:
            tmp.append(r1Coords[3])
        else: tmp.append(r2Coords[3])
        return tmp

    def getMinMax(self,pixels,points):
        tmpPoints = [points[0] for p in points]
        tmpPixels = [p for p in pixels]
        for point in points:
            index = points.index(point)

            if point[0] >= tmpPoints[0][0]:
                tmpPoints[0] = point
                tmpPixels[0] = pixels[index]

            if point[0] <= tmpPoints[2][0]:
                tmpPoints[2] = point
                tmpPixels[2] = pixels[index]

            if point[1] >= tmpPoints[1][1]:
                tmpPoints[1] = point
                tmpPixels[1] = pixels[index]

            if point[1] <= tmpPoints[3][1]:
                tmpPoints[3] = point
                tmpPixels[3] = pixels[index]
        return tmpPixels, tmpPoints


    def checkBoundaries(self,image, LTRB):
        # Used to make sure pixels are in correct places
        maxX = image.dataset.RasterXSize
        maxY = image.dataset.RasterYSize
        if LTRB[0] < 0:
            LTRB[0] = 0
        if LTRB[0] > maxX:
            LTRB[0] = maxX

        if LTRB[1] < 0:
            LTRB[1] = 0
        if LTRB[1] > maxY:
            LTRB[1] = maxY

        if LTRB[2] < 0:
            LTRB[2] = 0
        if LTRB[2] > maxX:
            LTRB[2] = maxX

        if LTRB[3] < 0:
            LTRB[3] = 0
        if LTRB[3] > maxY:
            LTRB[3] = maxY

        if LTRB[0] > LTRB[2]:
            tmp = LTRB[0]
            LTRB[0] = LTRB[2]
            LTRB[2] = tmp

        if LTRB[1] > LTRB[3]:
            tmp = LTRB[1]
            LTRB[1] = LTRB[3]
            LTRB[3] = tmp

        return LTRB[0],LTRB[1], LTRB[2], LTRB[3]

    #Gets intersection of two images
    def getIntersect(self,image2):
        # load data
        image1 = self
        band1 = image1.dataset.GetRasterBand(1)
        band2 = image2.dataset.GetRasterBand(1)
        gt1 = image1.dataset.GetGeoTransform()
        gt2 = image2.dataset.GetGeoTransform()
        # Position for top left and bottom right coordinate for boundaries
        #         LTRB = [[0,0],[3,1],[2,0],[1,1]]
        LTRB = [[0,0],[1,1],[2,0],[3,1]]


        r1 = image1.getCorners()
        r1Coords = image1.toLongLat(r1)
        r1, r1Coords = self.getMinMax(r1,r1Coords)

        r2 = image2.getCorners()
        r2Coords = image2.toLongLat(r2)
        r2, r2Coords = self.getMinMax(r2,r2Coords)

        intersection = self.getIntersection(r1Coords, r2Coords)

        if r1 != r2:
                right1 = image1.toPixel([intersection[2]])[0][0]
                bottom1 = image1.toPixel([intersection[3]])[0][1]
                tmp, tmp, right1, bottom1, = self.checkBoundaries(image1, [0,0,right1,bottom1])

                right2 = image2.toPixel(intersection[2])[0][0]
                bottom2 = image2.toPixel([intersection[3]])[0][1]
                tmp, tmp, right2, bottom2, = self.checkBoundaries(image2, [0,0,right2,bottom2])


                left1 = right1 - right2
                if left1 <0:
                    left1 = 0


                left2 = right2 - right1
                if left2 <0:
                    left2 = 0


                top1 = bottom1 - bottom2
                if top1 <0:
                    top1 = 0


                top2 = bottom2 - bottom1
                if top2 <0:
                    top2 = 0

                #                 print(left1,top1,right1,bottom1)

                #                 left2 = image2.toPixel([intersection[0]])[0][0]
                #                 top2 = image2.toPixel([intersection[1]])[0][1]

                #                 print(left2,top2,right2,bottom2)
                array1 = band1.ReadAsArray(left1,top1,right1-left1,bottom1-top1)
                array2 = band2.ReadAsArray(left2,top2,right2-left2,bottom2-top2)
                #                 print(right1-left1, bottom1-top1)
                #                 print(right2-left2, bottom2-top2)

        else: # same dimensions from the get go
            right1 = image1.dataset.RasterXSize # = col2
            bottom1 = image1.dataset.RasterYSize # = row2
            array1 = band1.ReadAsArray()
            array2 = band2.ReadAsArray()

        return array1, array2, right1-left1, bottom1-top1, right2-left2,bottom2-top2, intersection

    #Creates tiff image from array and x,y
    @staticmethod
    def createTiff(array, outputPath, col, row):
        driver  = gdal.GetDriverByName('GTiff')
        image = driver.Create(outputPath, col, row, 1, gdalconst.GDT_UInt16 )
        imageBand = image.GetRasterBand(1)
        imageBand.WriteArray(array)

    #Creats and intersection of two images and can save if told
    def createIntersectionOf(self, image,outPutNames, saveImages= False, outputFolder=None): #Creates two images in the same area
        src = self.dataset
        # We want a section of source that matches this:
        matchDs = image.dataset
        image1Array, image2Array, col1, row1, col2, row2, intersectLongLat = self.getIntersect(image)

        # Output / destination
        if saveImages:
            image1Filename = outPutNames[0]
            image2Filename = outPutNames[1]
            if not outputFolder:
                output = util.checkFolder("Transform",Output=True)
            else:
                output = outputFolder
            image1Output = os.path.join(output,image1Filename)
            image2Output = os.path.join(output,image2Filename)


            self.createTiff(image1Array, image1Output, col1,row1)
            self.createTiff(image2Array, image2Output, col2,row2)
            print('Created intersection images in :%s' % output)
            return True
        else:
            return [image1Array, image2Array]

    #Fuses two images together that don't cover the exact same area using fusion of daubechies wavelet coefficients
    #CAN KILL PROGRAM DUE TO VERY HIGH RAM USAGE** CAUTION, REQUIRES HIGH END MACHINE
    def polymerization(self, image2, mode=None, saveImages=False, level=None, clean=True, intersectOutputPath = None,   outputFolder = None ):
        if not intersectOutputPath:
            intersectOutputPath = util.checkFolder('Fusion', Input=True)
        try:
            outputNames = [self.name, image2.name]
        except:
            outputNames=[self.name,'IntersectOf'+self.name]
        intersectState = self.createIntersectionOf(image2,outputNames,
                                                   saveImages=saveImages,
                                                   outputFolder=intersectOutputPath)
        if not mode:
            mode = 'db7'
        if not level:
            level = 7

        if type(intersectState) is list:
            array1 = intersectState[0]
            array2 = intersectState[1]
            # No need to delete image that weren't saved
            clean = False


        else:
            image1 = os.path.join(intersectOutputPath, outputNames[0] )
            array1 = io.imread(image1,True, 'gdal')

            image2 = os.path.join(intersectOutputPath, outputNames[1])
            array2 = io.imread(image2,True, 'gdal')


        fusedImage = self.fuseImages(array1, array2, mode,level)
        if not outputFolder:
            outputFolder = util.checkFolder('Fusion', Output=True)

        oName = os.path.join(outputFolder,'Fused'+self.name)
        io.imsave(oName,fusedImage)
        if clean:
            try:
                os.remove(image1)
                os.remove(image2)
            except FileNotFoundError:
                pass

        print('Created fused image  :%s' % oName)



    #Fuse one image with another, used to fuse vertical and horizontal polarities
    #CAN KILL PROGRAM DUE TO VERY HIGH RAM USAGE** CAUTION, REQUIRES HIGH END MACHINE
    def fuseWith(self,image2, outputFolder=None, mode = None, level = None):

        array1 = self.array()
        array2 = image2.array()

        if not mode:
            mode = 'db7'
        if not level:
            level = 7

        try:
            fusedImage = self.fuseImages(array1, array2, mode,level)
        except MemoryError:
            print('Unable to fuse %s' % self.name)
            raise
            return
        if not outputFolder:
            outputFolder = util.checkFolder('Fusion', Output=True)
        oName = os.path.join(outputFolder,'Fused'+self.name)
        io.imsave(oName,fusedImage)
        print('Created fused image  :%s' % oName)

    #Fuses two array together using wavelets
    def fuseImages(self, array1, array2, mode, level): # Return fused images as array

        coeff1 = np.asarray(pywt.wavedec2( array1, mode, level=level))
        coeff2 = np.asarray(pywt.wavedec2( array2, mode, level=level))

        coApprx1 = coeff1.pop(0)
        coApprx2 = coeff2.pop(0)
        sumCoApp = coApprx1 + coApprx2
        coApprx = sumCoApp/2
        meanCoeff = np.asarray([coApprx])
        for levelA in coeff1:
            levelB = list(coeff2.pop(0))
            tempLevel = []
            for axisA in levelA:
                axisB = levelB.pop(0)
                sumAxis = axisA + axisB
                meanAxis = sumAxis/2
                tempLevel.append(meanAxis)
            tempLevel = np.asarray(tempLevel)
            meanCoeff.append(tuple(tempLevel))

        del coApprx1
        del coApprx2
        del coApprx
        gc.collect()
        try:
            return pywt.waverec2(meanCoeff,mode)
        except MemoryError:
            print(meanCoeff.dtype)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print( "*** print_tb:")
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            print( "*** print_exception:")
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            raise
