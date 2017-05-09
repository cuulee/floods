from resources.notifications.notifyServer import server as notifyServer
# from resources.notifications.notify import notify
from resources import util
import threading
import time




def serverThreadFunc(server,condition):

    print('starting server thread')
    server.start()





server = notifyServer.getServer()
server.start()

def wow():
    import time
    while True:
        print('going for a sleep')
        time.sleep(5)

def lol():
    print('still working')

server.addCommands({'wow':wow, 'l':lol})
# server.shutdown()
    # serverThread = threading.Thread(target=server.start())
    # serverThread.start()
# server.shutdown()
#
#     while True:
#         pass
#     server.shutdown()
# except KeyError:
#     server.shutdown()




# server = notifyServer.getServer(commands={'wow':wow})
# note = notify.getNotify()
# note.push('Yo')
