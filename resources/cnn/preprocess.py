
import tensorflow as tf

def distoredBoundBoxCrop(image,bbox,minObjCov=0.1,
                        aspRatioRange=(0.75, 1.33),areaRange=(0.05, 1.0),
                        maxAttemps=10,scope=None):
    with tf.name_scope(scope,'distoredBoundBoxCrop', [image,bbox]):
        sampleDistortBox = tf.image.sample_distorted_bounding_box(tf.shape(image),
                                                                  bounding_boxes=bbox,
                                                                  min_object_covered=minObjCov,
                                                                  aspect_ratio_range=aspRatioRange,
                                                                  area_range=areaRange,
                                                                  max_attempts=maxAttemps,use_image_if_no_bounding_boxes=True)

        bboxB, bboxSize, distortBox = sampleDistortBox

        croppedImage = tf.slice(image,bboxB,bboxSize)
        return croppedImage,distortBox



def preprocessTrain(image,height,width,bbox = None,fastMode=True,scope=None):
    with tf.name_scope(scope,'distortImage',[image,height,width,bbox]):
        if bbox is None:
            bbox = tf.constant([0.0,0.0,1.0,1.0],
                               dtype=tf.float32,
                               shape=[1,1,4])
        if image.dtype != tf.float32:
            image = tf.image.convert_image_dtype(image,dtype=tf.float32)

        imageWBox = tf.image.draw_bounding_boxes(tf.expand_dims(image,0),bbox)

        tf.summary.image('imageWithBoxes',imageWBox)

        distortImage, distortBox = distoredBoundBoxCrop(image,bbox)

        #Restors 3d
        # distortBox.set_shape([None,None,3])

        imageWDistortBox = tf.image.draw_bounding_boxes(tf.expand_dims(image,0),distortBox)
        tf.summary.image('imagesWithDistortBBox', imageWDistortBox)

        distortImage = tf.image.resize_images(distortImage,[height,width],method=0)

        tf.summary.image('finalDistortImage',tf.expand_dims(distortImage,0))
        distortImage = tf.subtract(distortImage,0.5)
        distortImage= tf.multiply(distortImage,2.0)
        return distortImage


    pass

def preprocessEval():
    pass

def preprocessImage(image,height,width,isTraining=False,fastMode = True):
    if isTraining:
        return preprocessTrain(image,height,width,fastMode)
    else: return preprocessEval()
