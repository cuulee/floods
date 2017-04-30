from resources.notifications.notifyServer import server as notifyServer
# from resources.notifications.notify import notify
from resources import util

def wow():
    from resources.notifications.notify import notify
    note = notify.getNotify()
    note.push('Hi Mammy!')


server = notifyServer.getServer(commands={'wow':wow})
# note = notify.getNotify()
# note.push('Yo')
