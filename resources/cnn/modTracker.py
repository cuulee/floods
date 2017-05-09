from resources.resource import util
from resources.resource import nets
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

    def loadTracker(self):
        trackerName = 'modelTracker.pkl'
        trackerPath = util.checkFolder('trackers')
        self.path = os.path.join(trackerPath,trackerName)
        self.types = {'new':self.new}
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


    def load(self,model,status,steps):
        if status in self.types:
            return self.types[status](model,steps)

    def latest(self,model,steps):
        if model not in self.models:
            raise ValueError('Model %s was not found in the model list ' % model)

        latestM = len(self.models[model]) -1
        modelPath, oldStep = self.models[model][latestM][0], self.models[model][latestM][1]
        updateModel(model,modelPath,steps)
        return modelPath, oldStep+steps




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
        self.addModel(model,modelPath,steps)
        return modelPath, steps
        # modelPath = util.checkFolder(model,)

    def addModel(self,model,modelPath):
        if model not in self.models:
            self.models.update({model:[modelPath,steps]})
        else:
            paths = self.models[model]
            paths.append([modelPath,steps])
            self.models.update({model:paths})
    def updateModel(self,model,modelPath,newSteps):
        tmp = []
        for models in self.models[model]:
            path = models[0]
            steps = models[1]
            if path == modelPath:
                steps = models[1] + newSteps
            tmp.append([path,steps])
        self.model.update({model,tmp})



    def reset(self):
        self.models = {}
        self.modelData = {}

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
