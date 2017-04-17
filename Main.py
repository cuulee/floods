from resources import util
from resources.satellite.api import API
from datetime import datetime
import os

api = API('gillesk3','rockyou94')
inputLocale = util.checkFolder('Locale', Input=True)
inputLocale = os.path.join(inputLocale,'simbach.geojson')
# start1=datetime.now() - relativedelta(years=1)

year = 2016
while year < 2017:
    start = datetime(year, 5,25)
    end = datetime(year, 6,15)
    print(start, end)
    results = api.query(inputLocale,startDate=start,endDate = end)
    print(len(results))
    if len(results) > 0:
        api.download(results)
    year += 1

print('fin')
