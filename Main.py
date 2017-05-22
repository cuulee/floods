
from resources.notifications.notifyServer import server as notifyServer
from resources.resource import util
from resources.resource import tracker
from resources.resource import image as satImage


from datetime import datetime
import os, sys



def evalNN(**kwargs):
    from resources.notifications.notify import notify
    import cnn
    note = notify.getNotify()

    if 'eval' in kwargs:
        try:
            evals = int(kwargs['eval'])
        except:
            note.push('Invalid number of eval')
    else:
        evals = 5

    if 'status' in kwargs:
        status = kwargs['status']
    else:
        status ='latest'
    if status == 'select':
        try:
            index = int(kwargs['index'])
        except:
            note.push('Invalid Index')
            return
    else:
        index = None


    cnn.evalNN(status=status,index = index,numEvals= evals)

def trainNN(**kwargs):
    import cnn
    from resources.notifications.notify import notify

    note = notify.getNotify()
    if 'steps' in kwargs:
        try:
            steps = int(kwargs['steps'])
        except:
            note.push('Invalid step')
            return
    else:
        steps = 10
    if 'status' in kwargs:
        status = kwargs['status']
    else:
        status ='latest'
    if status == 'select':
        try:
            index = kwargs['index']
        except:
            note.push('Invalid i/Index')
            return
    else:
        index = None
    if 'model' in kwargs:
        networkName = kwargs['model']
    else:
        networkName = 'incept'

    if 'optim' in kwargs:
        optim = kwargs['optim']
    else:
        optim = 'adam'

    if 'batch' in kwargs:
        batchSize = int(kwargs['batch'])
    else:
        batchSize =35

    if 'reuse' in kwargs:
        reuse = True
    else:
        reuse = False

    cnn.runNN(networkName=networkName, status=status,index=index,steps=steps,optim=optim,reuse = reuse,batchSize=batchSize)

def downloadImage(**kwargs):
    from resources.resource import API
    from resources.notifications.notify import notify
    note = notify.getNotify()
    if 'locale' in kwargs:
        try:
            locale = kwargs['locale']
        except:
            note.push('Valid locale required')
            return
    else:
        note.push('Locale required')
        return
    if 'y' in kwargs:
        try:
            year = int(kwargs['y'])
        except:
            note.push('Valid locale required')
            return
    else:
        note.push('Year required')
        return
    if 'm' in kwargs:
        try:
            month = int(kwargs['m'])
        except:
            note.push('Valid locale required')
            return
    else:
        note.push('Month required')
        return
    if 'd' in kwargs:
        try:
            day = int(kwargs['d'])
        except:
            note.push('Valid locale required')
            return
    else:
        note.push('Day required')
        return
    API.getImages(locale,year,month,day)


def labelImages(images): #Takes in
    try:
        for basename in images:
            tmp = images[basename]
            image = satImage(tmp[0])
            print(image)

            image.show()
            label = input('enter y for flood or n for none: ')
            label = label.lower()
            while label != 'y' and label != 'n':
                label = input('enter y for flood or n for none: ')
                label = label.lower()
            if label == 'y':
                label = '1'
            else:
                label = '0'
            satImage.killDisplay()

            tmp.append(label)

            images.update({basename:tmp})

        return images
    except KeyboardInterrupt:
        print('Exiting')
        satImage.killDisplay()

        sys.exit()

def organise(locale):
    directory = util.checkFolder('JPEGS',Input=True)

    directory = util.checkFolder(locale,path=directory)
    images = tracker.parseFolder(directory,findPosition=False,type='jpg')
    imageData = tracker.findImages(images,'jpg',directory)
    imageData = labelImages(imageData)
    stalker = tracker()

    stalker.add(imageData)
    stalker.saveTracker()


def toJpeg(locale,inputPath =None,outputPath=None, fusion = False):
    directory = util.checkFolder('Proccessed', Output=True)

    if not inputPath:
        inputPath = util.checkFolder(locale,path=directory)
        if fusion:
            inputPath = util.checkFolder('Fused',path=inputPath)



    tiffImages = tracker.parseFolder(inputPath,findPosition=False, type='tif')

    if not outputPath:
        outputPath = util.checkFolder('JPEGS',path =directory)
        outputPath = util.checkFolder(locale,path=outputPath)
        if fusion:
            outputPath = util.checkFolder('Fused',path=outputPath)

    satImage(tiffImages[0]).convertTo('jpeg',outputPath=outputPath)



commands ={'train nn':trainNN,
            'eval nn':evalNN,
            'download': downloadImage
            }

server = notifyServer.getServer(commands = commands)
# server.start()

args = sys.argv[1:]
for i, arg in enumerate(args):
    if arg == '-server':
        server.start()

    elif arg == '-train':
        try:
            import cnn
            argIndex = 1
            model = args[i+argIndex]
            argIndex+=1
            status = args[i+argIndex]
            argIndex+=1

            if status == 'select':
                index = int(args[i+argIndex])
                argIndex+=1

            else:
                index = None
            steps = int(args[i+argIndex])
            argIndex +=1
            optim = args[i+argIndex]
            if optim == 'reuse':
                cnn.runNN(networkName=model, status = status, index = index, steps = steps,reuse=True)
            else:
                argIndex +=1
                batchSize= int(args[i+argIndex])

                cnn.runNN(networkName=model, status = status, index = index, steps = steps, optim =optim, batchSize=batchSize)
        except:
            print('-train requires model, status/ index, steps, optim, batchSize')

    elif arg== '-eval':
        try:
            argIndex = 1
            model = args[i+argIndex]
            argIndex+=1
            status = args[i+argIndex]
            argIndex+=1

            if status == 'select':
                index = int(args[i+argIndex])
                argIndex+=1
            else:
                index = None
            evals = int(args[i+argIndex])
            import cnn
            cnn.evalNN(status=status,index = index,numEvals= evals)
        except:
            print('-eval requires mode, status/index, number of eval')

    elif arg =='-download':
        from resources.resource import API
        argIndex = 1
        locale = args[i+argIndex]
        argIndex+=1
        year = int(args[i+argIndex])
        argIndex+=1
        month = int(args[i+argIndex])
        argIndex+=1
        day = int(args[i+argIndex])
        API.getImages(locale,year,month,day,notify=False)

    elif arg =='-organise':
        locale = args[i+1]
        organise(locale)

    elif arg =='-convert':
        locale = args[i+1]
        toJpeg(locale)
