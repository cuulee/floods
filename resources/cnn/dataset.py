import os,sys
import tensorflow as tf
from resources.resource import util




from resources.imageTracker import tracker

slim = tf.contrib.slim
stalker = tracker()
def readFile(fileQueue):
    try:
        reader = tf.WholeFileReader()
        imagePath ,imageFile = reader.read(fileQueue)
        image = tf.image.decode_jpeg(imageFile,channels=1)
        return imagePath,image
    except KeyError:
        print('Error with image tracker')
        raise


def getFileQueue():
    fileList = [image[0] for image in stalker.toList() ]
    return tf.train.string_input_producer(fileList)

def getDataset():
    filename_queue = tf.train.string_input_producer(stalker.toList()[0])
