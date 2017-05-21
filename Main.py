from resources.resource import util
from resources.resource import API
from resources.resource import notify
from resources.notifications.notifyServer import server as notifyServer


from datetime import datetime
import os


# pushKey = util.configSectionMap("Keys")['pushbullet']
# print(pushKey)
#
# # a = notify()
# note = notify.getNotify()
# # note.getDevices()
#
#
# def getImages(locale,startYear,notify=True):
#     try:
#         localeName = str(locale.lower()) + '.geojson'
#         inputLocale = util.checkFolder('Locale', Input=True)
#         inputLocale = os.path.join(inputLocale,localeName)
#         api = API('gillesk3','rockyou94',notify=notify)
#
#         year = startYear
#         endYear = datetime.now().year
#         while year < endYear:
#             start = datetime(year, 11,15)
#             end = datetime(year+1, 1,15)
#             print(start, end)
#             results = api.query(inputLocale,startDate=start,endDate = end)
#             print(len(results))
#             if len(results) > 0:
#                 api.download(results,locale = locale)
#             year += 1
#
#
#
#     except:
#         print('Unable to download images')
#
#
#
# getImages('Athlone',2015)
#
# note.push('Fin')
# print('fin')
def wow():
    print('wow')


def defaultNN():
    import cnn
    cnn.runNN(steps=20000,status='new',optim='rmsprop')

def rerunnFirst():
    import cnn
    cnn.runNN(steps=2500, status='select',index = 1)

def rerunNN():
    import cnn
    cnn.runNN(status='latest',optim='rmsprop',steps =7000)

def fullrun():
    import cnn
    cnn.runNN(status='latest',optim='rmsprop',steps=10)

def evalLatest():
    import cnn
    cnn.evalNN(numBatch=1000)

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



commands ={'train nn':trainNN,
            'wow':wow,
            'eval nn':evalNN
            }
#
# commands ={'run nn':defaultNN,
#             'rerun nn':rerunNN,
#             'full run nn':fullrun,
#             'wow':wow,
#             'rerun 1 nn': rerunnFirst,
#             'eval latest': evalLatest,
#             'eval first': evalFirst}

server = notifyServer.getServer(commands = commands)
server.start()
# server.addCommands({'run nn':defaultNN, 'rerun nn': rerunNN,'full run nn':fullrun, 'wow':wow})
