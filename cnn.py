from resources.resourceNet import nets
from resources.resource import tracker
from resources.resourceNet import modTracker

from resources.resourceNet import dataset
from resources.resource import notify
from resources.resourceNet import modelDeploy
from resources.resource import image as satImage
from resources.resource import util
from tensorflow.python.ops import control_flow_ops
import os,sys
import tensorflow as tf
import numpy as np
import psutil
import math
from PIL import Image
slim = tf.contrib.slim


netsList = {'incept':nets.inceptResV2}
scopeList ={'incept':nets.inceptResV2ArgScope}



#Returns network function for a model
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


#Display an tensor image to verify if read in correctly
def displayImageTensor(imageTensor):
    tensor = np.squeeze(imageTensor,axis=(2,))
    im = Image.fromarray(tensor)

    im.show()


#Configures learning rate
def configLearningRate(sampleSize,globalStep):
    decaySteps = int(sampleSize/batchSize*2.0)
    return tf.train.exponential_decay(learningRate, globalStep,
                                      decaySteps, learningRateDecayFactor,
                                      staircase=True,
                                      name='exponentialDecayLearningRate')

#Configures optimizer
def configOptimizer(learningRate, optim):
    if optim =='adam':
        optimizer = tf.train.AdamOptimizer(learningRate)
    elif optim =='rmsprop':
        optimizer = tf.train.RMSPropOptimizer(learningRate)
    else:
        raise ValueError('Optimizer %s was not found' % optim)
    return optimizer

def initFunc():
    return None


#Evaluates a network, uses modeltracker to get unseen dataset
def evalNN(networkName='incept',status='latest',batchSize=35,index = None,numEvals=None):
    modelStalker = modTracker()
    stalker = tracker()
    trainDir,fullSteps = modelStalker.load(networkName,status = status, index = index)

    datalist = modelStalker.modelData[trainDir][1]

    with tf.Graph().as_default():

        #LOOK INTO MODEL CLASS****
        # Use for parallelism, cant beat google
        deployConfig = modelDeploy.DeploymentConfig(
            num_clones=numClones,
            clone_on_cpu=cloneCpu,
            replica_id=tasks,
            num_replicas=workerReplias,
            num_ps_tasks=numPSTasks)

        with tf.device(deployConfig.variables_device()):
            globalStep = slim.create_global_step()


        network = getNetFunc(networkName,numClasses=stalker.numLabels(),isTraining=False)
        fileQueue, counter = dataset.getFileQueue(datalist,[100,90])

        tmp = ''
        sampleSize = 0
        for l in counter:
            value = counter[l]
            sampleSize += value
            tmp += ' Label %d , Value %d' % (l,value)

        modelName = networkName + ': ' + os.path.basename(trainDir)
        checkpoint = tf.train.latest_checkpoint(trainDir)
        note.push('Running %s' % modelName)
        note.push('Dataset size : %s' %tmp)

        image,label,path = dataset.readFile(fileQueue)

        height,width = netsList[networkName].defaultImageSize, netsList[networkName].defaultImageSize
        image = tf.image.resize_images(image,[height,width],method=0)
        # image = preprocess.preprocessImage(image,netsList[networkName].defaultImageSize,netsList[networkName].defaultImageSize,isTraining=True)

        images,labels = tf.train.batch([image,label],batch_size=batchSize, num_threads=preprocessThread, capacity=2*batchSize)

        logits,_ = network(images)

        restoreVars = slim.get_variables_to_restore()
        prediction = tf.argmax(logits,1)

        names_to_values, names_to_updates = slim.metrics.aggregate_metric_map({
        'Accuracy': slim.metrics.streaming_accuracy(prediction, labels),
                    })

        for name, value in names_to_values.items():
            summary_name = 'eval/%s' % name
            op = tf.summary.scalar(summary_name, value, collections=[])
            op = tf.Print(op, [value], summary_name)
            tf.add_to_collection(tf.GraphKeys.SUMMARIES, op)

        if not numEvals:
            numEvals = math.ceil(len(datalist) / float(batchSize))
        evalDir = util.checkFolder('eval',path=trainDir)

        note.push('Starting for %d evals' %numEvals)
        slim.evaluation.evaluate_once(master='',
                                      checkpoint_path=checkpoint,
                                      logdir=evalDir,
                                      num_evals=numEvals,
                                      eval_op=list(names_to_updates.values()),
                                      variables_to_restore=restoreVars)



        note.push('Finished eval')

#Trains a network, can load new or old models
def runNN(networkName='incept',isTraining=True, status = 'new', index = None, learningRate =0.01, learningRateDecayFactor=0.94,
          batchSize=35, preprocessThread = 2, numClones = 1, cloneCpu = False,
          tasks = 0, workerReplias = 1, numPSTasks = 0, optim = 'adam',
          steps = 5000, trainDir = '/tmp/tf/',reuse= False):

    modelStalker = modTracker()
    stalker = tracker()

    trainDir,fullSteps = modelStalker.load(networkName,status = status, steps=steps,index = index)
    if reuse:
        optim = modelStalker.get(networkName,trainDir,'optim')
        batchSize = modelStalker.get(networkName,trainDir,'batchSize')

    if status == 'new':
        trainSet,evalSet = stalker.getData(isTraining=isTraining)
        modelStalker.addData(trainDir,[trainSet,evalSet],update =True)
        modelStalker.updateAtt(networkName,trainDir,'batchSize',batchSize)
        modelStalker.updateAtt(networkName,trainDir,'optim',optim)

        datalist = trainSet

    elif status == 'load' or status == 'latest' or status == 'select':
        try:
            if isTraining:

                datalist = modelStalker.modelData[trainDir][0]
            else:
                datalist = modelStalker.modelData[trainDir][1]
        except KeyError:
            trainSet,evalSet = stalker.getData(isTraining=isTraining)
            modelStalker.addData(trainDir,[trainSet,evalSet],update =True)
            if isTraining:
                datalist = modelStalker.modelData[trainDir][0]
            else:
                datalist = modelStalker.modelData[trainDir][1]
            modelStalker.saveTracker()




    with tf.Graph().as_default():

        #LOOK INTO MODEL CLASS****
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

        network = getNetFunc(networkName,numClasses=stalker.numLabels(),isTraining=isTraining)
        fileQueue, counter = dataset.getFileQueue(datalist,[90,100])

        tmp = ''
        sampleSize = 0
        for l in counter:
            value = counter[l]
            sampleSize += value
            tmp += ' Label %d , Value %d' % (l,value)

        modelName = networkName + ': ' + os.path.basename(trainDir)

        note.push('Running %s' % modelName)
        note.push('Dataset size : %s' %tmp)

        image,label,path = dataset.readFile(fileQueue)

        height,width = netsList[networkName].defaultImageSize, netsList[networkName].defaultImageSize
        image = tf.image.resize_images(image,[height,width],method=0)

        images,labels = tf.train.batch([image,label],batch_size=batchSize, num_threads=preprocessThread, capacity=2*batchSize)
        labelsOneHot = slim.one_hot_encoding(labels, len(stalker.labels))
        batchQueue = slim.prefetch_queue.prefetch_queue([images,labelsOneHot])

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


        with tf.device(deployConfig.optimizer_device()):
            learningRate = configLearningRate(sampleSize, globalStep )
            optimizer = configOptimizer(learningRate, optim)
            summaries.add(tf.summary.scalar('learningRate',learningRate))

        varToTrain = tf.trainable_variables()
        totalLoss, clonesGradients = modelDeploy.optimize_clones(clones,optimizer,var_list=varToTrain)

        summaries.add(tf.summary.scalar('totalLoss',totalLoss))

        predictions = tf.argmax(endPoints['Predictions'],1)

        accuracy =  slim.metrics.accuracy( tf.to_int32(predictions), tf.to_int32(labels) )
        # Create the summary ops such that they also print out to std output:
        summaries.add(tf.summary.scalar('Accuracy', accuracy))


        # mae_value_op, mae_update_op = slim.metrics.accuracy(predictions, labels)
        # summaries.add(tf.summary.scalar('Prediction',mae_value_op))

        gradUpdates = optimizer.apply_gradients(clonesGradients,global_step=globalStep)

        updateOps.append(gradUpdates)

        updateOps = tf.group(*updateOps)
        trainTensor = control_flow_ops.with_dependencies([updateOps],totalLoss,name='trainOp')

        summaries |= set(tf.get_collection(tf.GraphKeys.SUMMARIES,fCloneScope))

        summaryOp = tf.summary.merge(list(summaries),name='summaryOp')
        note.push('Training for %d steps' %steps)
        modelStalker.saveTracker()
        slim.learning.train(trainTensor,logdir=trainDir,is_chief=True,init_fn=initFunc(),
                            summary_op=summaryOp, number_of_steps=fullSteps, log_every_n_steps=10,
                            save_summaries_secs=600, save_interval_secs=600, sync_optimizer=None)


        note.push('Finished training')
