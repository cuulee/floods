from resources.notifications.notify import notify
from resources import util
from urllib.parse import urljoin
from websocket import create_connection
import ast

from queue import Queue
import threading
import time
import gc

#Thread to keep checking if message has been recieved from pushbullet
class receivePush(threading.Thread):
    def __init__(self,server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        server = self.server
        try:
            while not server.exitFlag:
                try:
                    push =  ast.literal_eval(server.ws.recv())
                    server.condition.acquire()
                    if push["type"] == 'tickle':
                        if push["subtype"] == 'push':
                            server.pushQueue.put(push)
                            # print('Putting %s on queue' % push)
                    server.condition.notify()
                    server.condition.release()
                except :
                    pass
        except KeyboardInterrupt :
            pass

#Thread to run commands once recieved from recievePush thread
class handlePush(threading.Thread):
    def __init__(self,server,name):
        threading.Thread.__init__(self)
        self.server = server
        self.name = name

    def run(self):
        server = self.server
        try:
            while not self.server.exitFlag:
                self.server.condition.acquire()
                if self.server.pushQueue.empty():
                    self.server.condition.wait()

                self.server.queueLock.acquire()
                if not self.server.pushQueue.empty():
                    push = self.server.pushQueue.get()
                    self.server.condition.release()
                    self.server.notify.getPushes(server=self.server)
                else:
                    self.server.condition.release()
                self.server.queueLock.release()


        except KeyboardInterrupt:
            pass


class server(object):
    exitFlag = 0
    condition = threading.Condition()
    queueLock = threading.Lock()
    # nnLock = threading.Condition()
    pushQueue = Queue(5)

    def __init__(self,APIKey, url= 'wss://stream.pushbullet.com/websocket/',target=None,logging=False, commands=None):
        self.url = url if url.endswith('/') else url + '/'
        self.url += APIKey
        self.notify = notify.getNotify(target,logging,commands)
        self.ws = create_connection(self.url,timeout=15)

        self.receiver = receivePush(self)
        self.handlers =  [handlePush(self,1),handlePush(self,2)]

    #Starts the server in a new thread, this allows it to run in the background
    def start(self):
        print('Stating messaging server')
        self.serverThread = threading.Thread(target=self.startThreads())
        self.serverThread.start()

    #Starts threads
    def startThreads(self):
        self.receiver.start()
        for handle in self.handlers:
            handle.start()

    #Shutdowns the server
    def shutdown(self):
        print('Shutting down messaging server, can take up to 10 seconds')
        self.exitFlag = 1
        self.receiver.join()
        for handle in self.handlers:
            handle.join()
        self.serverThread.join()

        # print('Shutting down messaging server')
    #Used to add new commands to the notify module
    def addCommands(self,commands):
        self.notify.addCommands(commands)
        self.setAllNotify()

    def setAllNotify(self):
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
            instance.notify = self.notify

    #Used to inital server before starting
    @staticmethod
    def getServer(target=None,logging=False, commands=None):
        pushKey = util.configSectionMap("Keys")['pushbullet']
        return server(pushKey,target=None,logging=False, commands=commands)
