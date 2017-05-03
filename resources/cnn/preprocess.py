



def preprocessTrain(image,height,width,bbox,fastMode=True):




def preprocessImage(image,height,width,isTraining=False,fastMode = True):
    if isTraining:
        return preprocessTrain(image,height,width,bbox,fastMode)
    else return preprocessEval
