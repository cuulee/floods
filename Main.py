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

def evalFirst():
    import cnn
    cnn.evalNN(status='select',index = 1)

commands ={'run nn':defaultNN,
            'rerun nn': rerunNN,
            'full run nn':fullrun,
            'wow':wow,
            'rerun 1 nn': rerunnFirst,
            'eval latest': evalLatest,
            'eval first': evalFirst}

server = notifyServer.getServer(commands = commands)
server.start()
# server.addCommands({'run nn':defaultNN, 'rerun nn': rerunNN,'full run nn':fullrun, 'wow':wow})
