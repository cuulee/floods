import os,sys
import tensorflow as tf
from resources.resource import util
import random
from resources.imageTracker import tracker

slim = tf.contrib.slim
stalker = tracker()

#Read an image from the filequeue
def readFile(fileQueue):
    try:

        label = fileQueue[1]
        imageFile  = tf.read_file(fileQueue[0])
        image = tf.image.decode_jpeg(imageFile,channels=1)
        return image,label, fileQueue[0]
    except KeyError:
        print('Error with image tracker')
        raise

#Creates file queue from model dataset
def getFileQueue(datalist,ratio):
    if type(ratio) is not list:
        raise ValueError('Ratio must be a list to boost data set labels by')

    balancedList =stalker.getBalancedList(datalist,ratio)
    filePaths = [image[0] for image in balancedList]
    labels = [int(image[1]) for image in balancedList]
    counter = {0:0,1:0}
    for l in labels:
        value = counter[l]
        value += 1
        counter.update({l:value})

    return tf.train.slice_input_producer([filePaths,labels]), counter
