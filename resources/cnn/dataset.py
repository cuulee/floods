import os,sys
import tensorflow as tf
from resources.resource import util




from resources.imageTracker import tracker

slim = tf.contrib.slim
stalker = tracker()
def readFile(fileQueue):
    try:
        # return fileQueue[1]
        # reader = tf.WholeFileReader()
        label = fileQueue[1]
        # imagePath ,imageFile = reader.read(fileQueue[0])
        imageFile  = tf.read_file(fileQueue[0])
        image = tf.image.decode_jpeg(imageFile,channels=1)
        return image,label, fileQueue[0]
    except KeyError:
        print('Error with image tracker')
        raise


def getFileQueue():
    filesPaths = [image[0] for image in stalker.toList() ]
    labels = [int(stalker.getLabel(image)) for image in filesPaths]
    # print(len(filesPaths))
    # print(len(labels))

    # images = tf.convert_to_tensor(filesPaths, dtype=tf.string)
    # labels = tf.convert_to_tensor(labels, dtype=tf.string)


    return tf.train.slice_input_producer([filesPaths,labels])

def getDataset():
    filename_queue = tf.train.string_input_producer(stalker.toList()[0])
