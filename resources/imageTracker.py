
from resources.resource import util
import pickle
import os


class tracker(object):
    files = {}


    def __init__(self,trackerPath=None):

        self.loadTracker()
        if len(self.files) >0:
            print(self.files)

    def loadTracker(self):
        trackName = 'tracker.pkl'
        trackerPath = util.checkFolder('Processed',Output=True)
        self.path = os.path.join(trackerPath,trackName)

        if os.path.isfile(self.path):
            try:
                with open(self.path, 'rb') as input:
                    track =  pickle.load(input)
                    self.files = track.files
            except:
                return
        else: return

    def saveTracker(self):
        with open(self.path, 'wb') as output:
            pickle.dump(self,output, pickle.HIGHEST_PROTOCOL)

    def add(self,images,overwrite = False):
        for basename in images.keys:
            tmp = images[basename]
            if basename in files and overwrite:
                self.files.update({basename:tmp})
            elif basename not in files:
                self.files.update({basename:tmp})


    
