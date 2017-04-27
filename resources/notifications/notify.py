import requests
import logging
from urllib.parse import urljoin
from resources import util
import datetime
from decimal import *
import time
import json
import logging

class device(object):
    def __init__(self, deviceInfo, sesh, url=  'https://api.pushbullet.com/v2/' ):
        try:
            self.id = deviceInfo['iden']
            self.nickname = deviceInfo['nickname']
            self.pushToken = deviceInfo['nickname']
            self.active = deviceInfo['active']
        except (KeyError, TypeError):
            self.id = None
            self.nickname = None
            self.pushToken = None
            self.active = False

        url = url if url.endswith('/') else url + '/'
        self.basUrl = url
        self.url = urljoin(url, 'devices/%s' %self.id)
        self.sesh = sesh

    def __str__(self):
        try:
            return getattr(self, "nickname")
        except :
            return 'None'

    def updateInfo(self, **info):
        data = info
        response = self.sesh.post(self.url,data=data)
        print(response.status_code)
        print('Update successful')

    def deleteDevice(self):
        response = self.sesh.delete(self.url)
        if response.status_code != 200:
            print('Error deleting device')

    def deletePushes(self):
        url = urljoin(self.basUrl, 'pushes')
        response = self.sesh.delete(url)
        if response.status_code != 200:
            print('Error deleting pushes')

class push(object):
    def __init__(self, pushInfo, sesh, url=  'https://api.pushbullet.com/v2/' ):
        try:
            self.id = pushInfo['iden']
            self.active = pushInfo['active']
            self.dismissed = pushInfo['dismissed']
            self.modifiedDate = pushInfo['modified']
            self.body = pushInfo['body']
            self.type = pushInfo['type']
            # self.title = pushInfo['title']

        except KeyError as e:
            pass
        url = url if url.endswith('/') else url + '/'

        self.url = urljoin(url, 'pushes/%s' %self.id)
        self.sesh = sesh

    def __str__(self):
        try:
            return getattr(self, "body")
        except AttributeError:
            try:
                return getattr(self, "title")
            except:
                return 'None'

    def read(self):
        data = {'dismissed':'true'}
        response = self.sesh.post(self.url,data=data)
        if response.status_code != 200:
            print('Error reading push')


    def delete(self):
        response = self.sesh.delete(self.url)
        if response.status_code != 200:
            print('Error deleting push')



class notify(object):
    try:
        defaultDevice = util.configSectionMap("Devices")['main']
    except:
        defaultDevice = None
    options = {'p' : 'pushes', 'push': 'pushes',
               'd' : 'devices', 'device' :'devices'
               }

    minWindow = 40

    def __init__(self, APIKey, url= 'https://api.pushbullet.com/v2/', target = 'Main', logging = False ):
        if target == 'Main':
            self.targetMain = True

        else:
             self.target = target
             self.targetMain = False

        if logging:
            self.logInit()


        self.url = url if url.endswith('/') else url + '/'
        self.sesh = requests.Session()
        self.sesh.auth = (APIKey,'')
        self.getDevices()

    def logInit(self):
        try:
            import http.client as httpClient
        except ImportError:
            import httplib as httpClient
        httpClient.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        self.logger = logging.getLogger("Pushbullet API")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = True

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

    def getPushes(self, active = True):
        now = time.time()
        timeWindow = self.__getTimeWindow()
        data = {'modified_after' :timeWindow,
                'active' : active}

        url = urljoin(self.url, self.options['p'])
        response = self.sesh.get(url,params=data,auth=self.sesh.auth)

        pushes = [push(pushMessage, self.sesh) for pushMessage in  response.json()['pushes'] ]
        activePushes = [p for p in pushes if p.active == True]
        self.checkPushes(activePushes)

    def deleteMainPush(self):
        if hasattr(self, 'mainDevice'):
            self.mainDevice.deletePushes()

    def checkPushes(self,pushes):
        command = {'print' : self.printing}


        for p in pushes:
            if hasattr(p, 'body'):
                body = p.body.lower().strip()
                if body in command and p.dismissed == False:
                    self.runCommand(p,body,command)


    def runCommand(self,p,body,command):
        command[body]()
        p.read()

    def printing(self):
        self.push('OK Printing', title = 'Command')
        print('printing')


    def __getTimeWindow(self):
        return time.mktime( ( datetime.datetime.now() -datetime.timedelta(minutes=self.minWindow) ).timetuple()  )

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
        self.devices = self.activeDevices([device(dev, self.sesh) for dev in  response.json()['devices'] ])
        if hasattr(self, 'defaultDevice'):
            try:
                self.mainDevice = [dev for dev in self.devices if self.defaultDevice == dev.nickname][0]
            except:
                self.mainDevice = device(None,self.sesh)


        return self.devices

    def activeDevices(self, devices):
        tmp = []
        for d in devices:
            if hasattr(d,'id' ):
                if d.id:
                    tmp.append(d)
        return tmp

    @staticmethod
    def getNotify(target=None,logging=False):
        pushKey = util.configSectionMap("Keys")['pushbullet']
        return notify(pushKey,target=target,logging=logging)
