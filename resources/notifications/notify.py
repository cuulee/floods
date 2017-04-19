import requests
import logging
from urllib.parse import urljoin
from resources import util



class notify(object):


    options = {'p' : 'pushes', 'push': 'pushes',
               'd' : 'devices', 'device' :'devices',
               }




    def __init__(self, APIKey, url= 'https://api.pushbullet.com/v2/' ):
        self.logger = logging.getLogger('notify')
        self.url = url if url.endswith('/') else url + '/'
        # self.sesh = requests.Session()
        self.auth = (APIKey,'')

    def push(self,message,title='Update' ,option='p'):
        data = {'type':'note',
                'title':title,
                'body':message
                }
        url = urljoin(self.url, self.options[option])
        response = requests.post(url, data=data, auth=self.auth)
        # jsonFeed = response.json()


    def getDevices(self,option='d'):
        url = urljoin(self.url, self.options[option])
        response = requests.get(url, auth=self.auth)
        devices  = response.json()['devices']
        print(devices)

    @staticmethod
    def getNotify():
        pushKey = util.configSectionMap("Keys")['pushbullet']
        return notify(pushKey)
