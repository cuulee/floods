from resources.resource import util
from resources.resourceNet import nets
import pickle
import os
import csv
from PIL import Image
from random import shuffle



class tracker(object):
    models = {}
    modelData = {}

    def __init__(self,trackerPath=None):
        self.loadTracker()

    #Loads saved tracker with models
    def loadTracker(self):
        trackerName = 'modelTracker.pkl'
        trackerPath = util.checkFolder('trackers')
        self.path = os.path.join(trackerPath,trackerName)
        self.types = {'new':self.new,'latest':self.latest,'select':self.select}
        if os.path.isfile(self.path):
            try:
                with open(self.path, 'rb') as input:
                    track =  pickle.load(input)
                    self.models = track.models
                    self.modelData = track.modelData
            except:
                return
        else: return

    def saveTracker(self):
        with open(self.path, 'wb') as output:
            pickle.dump(self,output, pickle.HIGHEST_PROTOCOL)


    def load(self,model,status,steps=None,index = None):
        if status in self.types:
            if not index:
                return self.types[status](model,steps)
            elif index and status=='select':
                return self.types[status](model,steps,index)

    #Returns the latest model
    def latest(self,model,steps):
        if model not in self.models:
            raise ValueError('Model %s was not found in the model list ' % model)

        # latestM = len(self.models[model]) -1
        modelPath = self.latestPath(model)
        oldStep = self.get(model,modelPath,'steps')

        if not steps:
            steps = 0
        return modelPath, oldStep+steps

    #Gets attribute for model
    def get(self,model,path,att):
        if att == 'steps':
            return self.getSteps(path)
        elif att in self.models[model][path]:
            return self.models[model][path][att]
        else:
            raise ValueError('%s was not found in model %s: %s' %(att,model,path))

    #Updates attribut
    def updateAtt(self,model,path,att,value):
        self.models[model][path].update({att:value})

    # Returns model at index i
    def select(self,model,steps,index):
        if model not in self.models:
            raise ValueError('Model %s was not found in the model list ' % model)


        modelPath = util.checkFolder('models')
        modelPath = util.checkFolder(model,path=modelPath)
        folders = [f for f in os.listdir(modelPath) if os.path.isdir(os.path.join(modelPath, f))]
        found = False
        for folder in folders:
            try:
                num = folder
                if str(num) == str(index):
                    found = True
                    break
            except:
                pass
        if found:
            modelPath= os.path.join(modelPath,str(index))
            oldStep = self.get(model,modelPath,'steps')
            if not steps:
                steps = 0

            return modelPath, oldStep+steps
        else:
            raise ValueError('%s model index: %d was not found in %s directory' %(model,index, modelPath))

    #Returns the most recent model path
    @staticmethod
    def latestPath(model):
        modelPath = util.checkFolder('models')
        modelPath = util.checkFolder(model,path=modelPath)
        latest = 0
        folders = [f for f in os.listdir(modelPath) if os.path.isdir(os.path.join(modelPath, f))]
        for folder in folders:
            try:
                num = int(folder)
                latest = num
            except:
                pass

        return  util.checkFolder(str(latest),path=modelPath)

    #Returns a new model
    def new(self,model,steps):
        if model not in nets.netModel:
            raise ValueError('Model %s was not found in the model list in nets' % model)

        modelPath = util.checkFolder('models')
        modelPath = util.checkFolder(model,path=modelPath)
        latest = 0
        folders = [f for f in os.listdir(modelPath) if os.path.isdir(os.path.join(modelPath, f))]
        for folder in folders:
            try:
                num = int(folder)
                latest = num
            except:
                pass

        latest += 1
        modelPath = util.checkFolder(str(latest),path=modelPath)
        self.addModel(model,modelPath)
        return modelPath, steps
        # modelPath = util.checkFolder(model,)


    #Adds model to model dictionary
    def addModel(self,model,modelPath):
        if model not in self.models:
            self.models.update({model:{modelPath:{}}})
        else:
            paths = self.models[model]
            self.models[model].update({modelPath:{}})


    #Resets tracker
    def reset(self):
        self.models = {}
        self.modelData = {}

    #Adds data for model, useful when retraining
    def addData(self,modelPath,dataset,update = False):
        if modelPath in self.modelData and not update:
            print('model data has already been added, set update - True to overwrite')
        elif modelPath in self.modelData and update:
            if type(dataset) is list:
                self.modelData.update({modelPath:dataset})
            else:
                print('model data must be in list format')
        elif modelPath not in self.modelData:
            self.modelData.update({modelPath:dataset})

    #Gets current step of model
    def getSteps(self,modelPath):

        files = [f for f in os.listdir(modelPath) if os.path.isfile(os.path.join(modelPath, f))]
        maxSteps = 0
        for f in files:
            try:
                f = f.split('-')[1].split('.')[0]
                step = int(f)
                if step > maxSteps:
                    maxSteps = step

            except:
                pass
        return maxSteps
