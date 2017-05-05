
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

def distorted_bounding_box_crop(image,
                                bbox,
                                min_object_covered=0.1,
                                aspect_ratio_range=(0.75, 1.33),
                                area_range=(0.05, 1.0),
                                max_attempts=100,
                                scope=None):

  with tf.name_scope(scope, 'distorted_bounding_box_crop', [image, bbox]):
    # Each bounding box has shape [1, num_boxes, box coords] and
    # the coordinates are ordered [ymin, xmin, ymax, xmax].

    # A large fraction of image datasets contain a human-annotated bounding
    # box delineating the region of the image containing the object of interest.
    # We choose to create a new bounding box for the object which is a randomly
    # distorted version of the human-annotated bounding box that obeys an
    # allowed range of aspect ratios, sizes and overlap with the human-annotated
    # bounding box. If no box is supplied, then we assume the bounding box is
    # the entire image.
    sample_distorted_bounding_box = tf.image.sample_distorted_bounding_box(
        tf.shape(image),
        bounding_boxes=bbox,
        min_object_covered=min_object_covered,
        aspect_ratio_range=aspect_ratio_range,
        area_range=area_range,
        max_attempts=max_attempts,
        use_image_if_no_bounding_boxes=True)
    bbox_begin, bbox_size, distort_bbox = sample_distorted_bounding_box

    # Crop the image to the specified bounding box.
    cropped_image = tf.slice(image, bbox_begin, bbox_size)
    return cropped_image, distort_bbox

def preprocessTrain(image, height, width, bbox,
                         fast_mode=True,
                         scope=None):

     with tf.name_scope(scope, 'distort_image', [image, height, width, bbox]):
        if bbox is None:
          bbox = tf.constant([0.0, 0.0, 1.0, 1.0],
                             dtype=tf.float32,
                             shape=[1, 1, 4])
        if image.dtype != tf.float32:
          image = tf.image.convert_image_dtype(image, dtype=tf.float32)
    # Each bounding box has shape [1, num_boxes, box coords] and
    # the coordinates are ordered [ymin, xmin, ymax, xmax].
        image_with_box = tf.image.draw_bounding_boxes(tf.expand_dims(image, 0),
                                                  bbox)
        tf.summary.image('image_with_bounding_boxes', image_with_box)

        distortImage, distortBox = distorted_bounding_box_crop(image,bbox)

        #Restors 3d
        # distortBox.set_shape([None,None,3])

        imageWDistortBox = tf.image.draw_bounding_boxes(tf.expand_dims(image,0),distortBox)
        tf.summary.image('imagesWithDistortBBox', imageWDistortBox)

        distortImage = tf.image.resize_images(distortImage,[height,width],method=0)

        tf.summary.image('finalDistortImage',tf.expand_dims(distortImage,0))
        distortImage = tf.subtract(distortImage,0.5)
        distortImage= tf.multiply(distortImage,2.0)
        return distortImage


# def preprocessTrain(image,height,width,bbox = None,fastMode=True,scope=None):
#     with tf.name_scope(scope,'distortImage',[image,height,width,bbox]):
#         if bbox is None:
#             bbox = tf.constant([0.0,0.0,1.0,1.0],
#                                dtype=tf.float32,
#                                shape=[1,1,4])
#         if image.dtype != tf.float32:
#             image = tf.image.convert_image_dtype(image,dtype=tf.float32)
#
#         imageWBox = tf.image.draw_bounding_boxes(tf.expand_dims(image,0),bbox)
#
#         tf.summary.image('imageWithBoxes',imageWBox)
#
#         distortImage, distortBox = distorted_bounding_box_crop(image,bbox)
#
#         #Restors 3d
#         # distortBox.set_shape([None,None,3])
#
#         imageWDistortBox = tf.image.draw_bounding_boxes(tf.expand_dims(image,0),distortBox)
#         tf.summary.image('imagesWithDistortBBox', imageWDistortBox)
#
#         distortImage = tf.image.resize_images(distortImage,[height,width],method=0)
#
#         tf.summary.image('finalDistortImage',tf.expand_dims(distortImage,0))
#         distortImage = tf.subtract(distortImage,0.5)
#         distortImage= tf.multiply(distortImage,2.0)
#         return distortImage
#
#
#     pass

def preprocessEval():
    pass

def preprocessImage(image,height,width,isTraining=False,fastMode = True):
    if isTraining:
        return preprocessTrain(image,height,width,fastMode)
    else: return preprocessEval()
