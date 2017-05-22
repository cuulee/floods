from resources.resource import util

from resources.resource import notify
from resources.notifications.notifyServer import server as notifyServer


from datetime import datetime
import os




def wow():
    print('wow')




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


commands ={'train nn':trainNN,
            'wow':wow,
            'eval nn':evalNN,
            'download': downloadImage
            }

server = notifyServer.getServer(commands = commands)
server.start()
