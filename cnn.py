from resources.resource import nets
from resources.resource import tracker
from resources.resource import dataset
from resources.resource import preprocess
from resources.resource import modelDeploy
from resources.resource import image as satImage

from tensorflow.python.ops import control_flow_ops
import os,sys
import tensorflow as tf
import numpy as np
import psutil
from PIL import Image
slim = tf.contrib.slim


netsList = {'incept':nets.inceptResV2}
scopeList ={'incept':nets.inceptResV2ArgScope}

networkName = 'incept'
isTraining = True
learningRate = 0.01
learningRateDecayFactor = 0.94
batchSize = 30
preprocessThread = 2
numClones =1
cloneCpu = False
tasks = 0
workerReplias = 1
numPSTasks = 0
optim = 'adam'
trainDir = '/tmp/tfmodel/'


#Not sure where weightDecay is used
def getNetFunc(name,numClasses,weightDecay=0.0,isTraining=False):


    if name not in netsList:
        raise ValueError('Network: %s not found' %name)

    func = netsList[name]

    def netFunc(images):
        argScope = scopeList[name](weightDecay=weightDecay)
        with slim.arg_scope(argScope):
            return func(images,numClasses,isTraining=isTraining)

    if hasattr(func,'defaultImageSize'):
        netFunc.defaultImageSize = func.defaultImageSize

    return netFunc

def displayImageTensor(imageTensor):
    tensor = np.squeeze(imageTensor,axis=(2,))
    im = Image.fromarray(tensor)

    im.show()

def killDisplay():
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()

def configLearningRate(sampleSize,globalStep):
    decaySteps = int(sampleSize/batchSize*2.0)
    return tf.train.exponential_decay(learningRate, globalStep,
                                      decaySteps, learningRateDecayFactor,
                                      staircase=True,
                                      name='exponentialDecayLearningRate')

def configOptimizer(learningRate, optim):
    if optim =='adam':
        optimizer = tf.train.AdamOptimizer(learningRate)
    elif optim =='rmsprop':
        optimizer = tf.train.RMSPropOtimizer(learningRate)
    else:
        raise ValueError('Optimizer %s was not found' % optim)
    return optimizer

def initFunc():
    return None

with tf.Graph().as_default():

    # Use for parallelism, cant beat google
    deployConfig = modelDeploy.DeploymentConfig(
        num_clones=numClones,
        clone_on_cpu=cloneCpu,
        replica_id=tasks,
        num_replicas=workerReplias,
        num_ps_tasks=numPSTasks)

    with tf.device(deployConfig.variables_device()):
        globalStep = slim.create_global_step()

    #Load dataset from tracker class
    stalker = tracker()
    network = getNetFunc(networkName,numClasses=stalker.numLabels(),isTraining=isTraining)

    fileQueue = dataset.getFileQueue()

    image,label,path = dataset.readFile(fileQueue)

    height,width = netsList[networkName].defaultImageSize, netsList[networkName].defaultImageSize
    image = tf.image.resize_images(image,[height,width],method=0)
    # image = preprocess.preprocessImage(image,netsList[networkName].defaultImageSize,netsList[networkName].defaultImageSize,isTraining=True)

    images,labels = tf.train.batch([image,label],batch_size=batchSize, num_threads=preprocessThread, capacity=2*batchSize)
    labels = slim.one_hot_encoding(labels, len(stalker.labels))
    batchQueue = slim.prefetch_queue.prefetch_queue([images,labels])

    def cloneFuc(batchQueue):
        # Can be usesd for data parallelism
        images,labels = batchQueue.dequeue()
        logits,endPoints = network(images)


        # Set loss function
        if 'AuxLogits' in endPoints:
            tf.losses.softmax_cross_entropy(logits=endPoints['AuxLogits'],
                                            onehot_labels=labels, label_smoothing=0.0, weights=0.4,scope='auxLoss')
        tf.losses.softmax_cross_entropy(logits=logits,
                                        onehot_labels=labels, label_smoothing=0.0, weights=1.0)
        return endPoints

    summaries = set(tf.get_collection(tf.GraphKeys.SUMMARIES))

    clones = modelDeploy.create_clones(deployConfig,cloneFuc,[batchQueue])

    fCloneScope = deployConfig.clone_scope(0)
    updateOps = tf.get_collection(tf.GraphKeys.UPDATE_OPS,fCloneScope)

    endPoints = clones[0].outputs
    for endPoint in endPoints:
        x = endPoints[endPoint]
        summaries.add(tf.summary.histogram('activations/'+ endPoint,x))
        summaries.add(tf.summary.scalar('sparsity/' + endPoint, tf.nn.zero_fraction(x)))

    #     # Add summaries for losses.
    for loss in tf.get_collection(tf.GraphKeys.LOSSES, fCloneScope):
        summaries.add(tf.summary.scalar('losses/%s' % loss.op.name,loss))


    #     # Add summaries for variables.
    for variable in slim.get_model_variables():
        summaries.add(tf.summary.histogram(variable.op.name, variable))

    movingAverageVariable, variableAvg = None,None
    sampleSize = len(stalker.toList())
    with tf.device(deployConfig.optimizer_device()):
        learningRate = configLearningRate(len(stalker.toList()), globalStep )
        optimizer = configOptimizer(learningRate, optim)
        summaries.add(tf.summary.scalar('learningRate',learningRate))

    varToTrain = tf.trainable_variables()
    totalLoss, clonesGradients = modelDeploy.optimize_clones(clones,optimizer,var_list=varToTrain)

    summaries.add(tf.summary.scalar('totalLoss',totalLoss))

    gradUpdates = optimizer.apply_gradients(clonesGradients,global_step=globalStep)

    updateOps.append(gradUpdates)

    updateOps = tf.group(*updateOps)
    trainTensor = control_flow_ops.with_dependencies([updateOps],totalLoss,name='trainOp')

    summaries |= set(tf.get_collection(tf.GraphKeys.SUMMARIES,fCloneScope))

    summaryOp = tf.summary.merge(list(summaries),name='summaryOp')

    slim.learning.train(trainTensor,logdir=trainDir,is_chief=True,init_fn=initFunc(),
                        summary_op=summaryOp, number_of_steps=None, log_every_n_steps=10,
                        save_summaries_secs=600, save_interval_secs=600, sync_optimizer=None)
