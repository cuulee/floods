from resources.notifications.notify import notify



notify = notify.getNotify()
notify.push('new')
# notify.getPushes()
# devices = notify.getDevices()
# print(notify.getNames())
# print(len(devices))
