from resources.notifications.notify import notify

notify = notify.getNotify(target='Main')
devices = notify.getDevices()
print(notify.getNames())
print(len(devices))
