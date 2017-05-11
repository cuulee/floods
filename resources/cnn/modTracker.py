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
        self.types = {'new':self.new,'latest':self.latest}
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


    def load(self,model,steps,status):
        if status in self.types:
            return self.types[status](model,steps)

    def latest(self,model,steps):
        if model not in self.models:
            raise ValueError('Model %s was not found in the model list ' % model)

        # latestM = len(self.models[model]) -1
        modelPath = self.latestPath(model)
        oldStep = self.models[model][modelPath][0]
        self.updateModel(model,modelPath,steps)
        return modelPath, oldStep+steps


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

    def addModel(self,model,modelPath,steps):
        if model not in self.models:
            self.models.update({model:{modelPath:[steps]}})
        else:
            paths = self.models[model]
            self.models[model].update({modelPath:[steps]})

    def updateModel(self,model,modelPath,newSteps):



        oldSteps = self.models[model][modelPath][0]
        steps =  oldSteps + newSteps
        self.models[model].update({modelPath:[steps]})



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
