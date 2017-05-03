from resources.resource import util
from resources.resource import API
from resources.resource import notify

from datetime import datetime
import os


# pushKey = util.configSectionMap("Keys")['pushbullet']
# print(pushKey)
#
# # a = notify()
note = notify.getNotify()
# note.getDevices()


def getImages(locale,startYear,notify=True):
    try:
        localeName = str(locale.lower()) + '.geojson'
        inputLocale = util.checkFolder('Locale', Input=True)
        inputLocale = os.path.join(inputLocale,localeName)
        api = API('gillesk3','rockyou94',notify=notify)

        year = startYear
        endYear = datetime.now().year
        while year < endYear:
            start = datetime(year, 11,15)
            end = datetime(year+1, 1,15)
            print(start, end)
            results = api.query(inputLocale,startDate=start,endDate = end)
            print(len(results))
            if len(results) > 0:
                api.download(results,locale = locale)
            year += 1



    except:
        print('Unable to download images')



getImages('Athlone',2015)

note.push('Fin')
# print('fin')
