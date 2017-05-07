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
    print('ha')

server.addCommands({'wow':wow})
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
