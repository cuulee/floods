from resources import util
from resources.satellite.image import image as satImage
import os


folder = util.checkFolder('Conversion', Input=True)

images = []
for file in util.files(folder):
    filePath = os.path.join(folder,file)
    images.append(satImage(filePath))


for image in images:
    outputPath = util.checkFolder('Jpeg',Output=True)

    image.convertTo('jpeg',outputPath = outputPath )
