import pyudev

while True:
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block')
    for action, device in monitor:
        print('{0}: {1}'.format(action, device))