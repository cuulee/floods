from resources.notifications.notify import notify
from resources import util
from urllib.parse import urljoin
from websocket import create_connection
import ast

from queue import Queue
import threading
import time
import gc

class serverThread (threading.Thread):
    def __init__(self, name, func):
        threading.Thread.__init__(self)
        self.func = func
        self.name = name

    def run(self):
        print ("Starting " + self.name)
        # Get lock to synchronize threads
        threadLock.acquire()
        print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


def receivePush(server):
    try:
        while not server.exitFlag:
            result =  ast.literal_eval(server.ws.recv())
            server.condition.acquire()
            server.pushQueue.put(result)
            # print('Putting %s on queue' % result)
            server.condition.notify_all()
            server.condition.release()
    except KeyboardInterrupt:
        pass

def handlePush(server):
    try:
        while not server.exitFlag:
            server.condition.acquire()
            if server.pushQueue.empty():
                server.condition.wait()

            if not server.pushQueue.empty():
                push = server.pushQueue.get()
                if push["type"] == 'tickle':
                    if push["subtype"] == 'push':

                        server.notify.getPushes(server=server)

            server.condition.release()
    except KeyboardInterrupt:
        pass

class server(object):
    exitFlag = 0
    # queueLock = threading.Lock()
    condition = threading.Condition()
    pushQueue = Queue(5)

    def __init__(self,APIKey, url= 'wss://stream.pushbullet.com/websocket/',target=None,logging=False, commands=None):
        self.url = url if url.endswith('/') else url + '/'
        self.url += APIKey
        self.notify = notify.getNotify(target,logging,commands)
        self.ws = create_connection(self.url)

        self.receiver = threading.Thread(target=receivePush, args=(self,))
        self.handler = threading.Thread(target=handlePush, args=(self,))

    def start(self):
        print('Stating messaging server')
        self.serverThread = threading.Thread(target=self.startThreads())

        self.serverThread.start()

    def startThreads(self):
        self.receiver.start()
        self.handler.start()

    def shutdown(self):
        print('Shutting down messaging server, can take up to 10 seconds')
        self.exitFlag = 1
        self.receiver.join()
        self.handler.join()
        self.serverThread.join()

        # print('Shutting down messaging server')

    def addCommands(self,commands):
        self.notify.addCommands(commands)
        self.setAllNotify()

    def setAllNotify(self):
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
            instance.notify = self.notify


    @staticmethod
    def getServer(target=None,logging=False, commands=None):
        pushKey = util.configSectionMap("Keys")['pushbullet']
        return server(pushKey,target=None,logging=False, commands=commands)
        # return notify(pushKey,target=target,logging=logging)

    def getServerThread():
        return threading.Thread(target=server.getServer)
