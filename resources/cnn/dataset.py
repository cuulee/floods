import os,sys
import tensorflow as tf
from resources.resource import util




from resources.imageTracker import tracker

slim = tf.contrib.slim
stalker = tracker()
def readFile(fileQueue):
    try:

        label = fileQueue[1]
        imageFile  = tf.read_file(fileQueue[0])
        image = tf.image.decode_jpeg(imageFile,channels=1)
        return image,label, fileQueue[0]
    except KeyError:
        print('Error with image tracker')
        raise


def getFileQueue():
    images = stalker.toList()
    allImages = stalker.getRotateList(images)
    balancedList =stalker.getBalancedList(allImages,[100,100])
    filePaths = [image[0] for image in balancedList]
    labels = [int(image[1]) for image in balancedList]
    counter = {0:0,1:0}
    for l in labels:
        value = counter[l]
        value += 1
        counter.update({l:value})
    # filesPaths = [image[0] for image in stalker.toList() ]
    # labels = [int(stalker.getLabel(image)) for image in filesPaths]
    return tf.train.slice_input_producer([filePaths,labels]), counter

def getDataset():
    filename_queue = tf.train.string_input_producer(stalker.toList()[0])
