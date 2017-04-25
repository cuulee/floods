import requests
import logging
from urllib.parse import urljoin
from resources import util

class device(object):
    def __init__(self, deviceInfo, sesh, url=  'https://api.pushbullet.com/v2/' ):
        try:
            self.id = deviceInfo['iden']
            self.nickname = deviceInfo['nickname']
            self.pushToken = deviceInfo['nickname']
            self.active = deviceInfo['active']
        except KeyError:
            self.id = None
            self.nickname = None
            self.pushToken = None
            self.active = False
        url = url if url.endswith('/') else url + '/'

        self.url = urljoin(url, 'devices/%s' %self.id)
        self.sesh = sesh

    def updateInfo(self, **info):
        data = info
        response = self.sesh.post(self.url,data=data)
        print(response.status_code)
        print('Update successful')

    def deleteDevice(self):
        response = self.sesh.delete(self.url)
        print(response.status_code)




class notify(object):
    try:
        defaultDevice = util.configSectionMap("Devices")['main']
    except:
        defaultDevice = None
    options = {'p' : 'pushes', 'push': 'pushes',
               'd' : 'devices', 'device' :'devices'
               }

    def __init__(self, APIKey, url= 'https://api.pushbullet.com/v2/', target = 'Main' ):
        if target == 'Main':
            self.targetMain = True

        else:
             self.target = target


        self.logger = logging.getLogger('notify')
        self.url = url if url.endswith('/') else url + '/'
        self.sesh = requests.Session()
        self.sesh.auth = (APIKey,'')

    def push(self, message, title='Update', target = None, option='p'):
        data = {'type':'note',
                'title':title,
                'body':message
                }

        if not target and self.targetMain:
            if hasattr(self, 'mainDevice'):
                data.update({'device_iden': self.mainDevice.id})

        else:
            if target:
                data.update({'device_iden':target})

        url = urljoin(self.url, self.options['p'])
        response = self.sesh.post(url, data=data, auth=self.sesh.auth)

    def getNames(self):
        if hasattr(self, 'devices'):
            return [dev.nickname for dev in self.devices]
        else:
            try:
                self.getDevices()
                return [dev.nickname for dev in self.devices]
            except:
                print('Error getting device names')

    # Returns new devices first
    def getDevices(self,option='d'):
        url = urljoin(self.url, self.options[option])
        response = self.sesh.get(url, auth=self.sesh.auth)
        self.devices = [device(dev, self.sesh) for dev in  response.json()['devices'] ]
        print(response.json()['devices'])
        if hasattr(self, 'defaultDevice'):
            try:
                self.mainDevice = [dev for dev in self.devices if self.defaultDevice == dev.nickname][0]
            except:
                print('no main device found')
                self.mainDevice = None


        return self.devices

    @staticmethod
    def getNotify(target=None):
        pushKey = util.configSectionMap("Keys")['pushbullet']
        return notify(pushKey,target=target)
