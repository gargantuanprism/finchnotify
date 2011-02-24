#!/usr/bin/env python2

import pynotify
import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop
import re
import time
import gtk

# def onlinenotify(name):
# 	if pynotify.init("does it work?"):
# 		n = pynotify.Notification(name, " is online!")
# 		n.show()
# 	else:
# 		print "Nope, doesn't work"

def messnotify(account, sender, message, conversation, flags):
	try:
		notify(purple, account, sender, message)
	except:
		bus, purple = connect()
		notify(purple, account, sender, message)
		
def notify(purple, account, sender, message):			
	senderAlias = purple.PurpleBuddyGetAlias(purple.PurpleFindBuddy(account,sender))
	sanshtml = re.sub('<.*?>','',message)
	if pynotify.init("How about here?"):
		n = pynotify.Notification(senderAlias, sanshtml, "file:///usr/share/pixmaps/pidgin/tray/hicolor/48x48/status/pidgin-tray-pending.png")
		n.show()
	else:
		print "Nope, doesn't work"

# def buddy_online(buddy):
# 	buddyAlias = purple.PurpleBuddyGetAlias(buddy)
# 	onlinenotify(buddyAlias)

def conv_updated(uid, b):
	show_unread()

def msg_received(account, sender, message, conversation, flags):
	show_unread()

# rather than relying on some signal, check how many unread conversations there are
def show_unread():
	convs = purple.PurpleGetConversations()
	count = 0

	for conv in convs:
		count += purple.PurpleConversationGetData(conv, "unseen-count")

	if (count > 0):
		tray.set_from_file("/usr/share/pixmaps/pidgin/tray/hicolor/48x48/status/pidgin-tray-pending.png")
		tray.set_blinking(True)
	else:
		tray.set_from_file("/usr/share/pixmaps/pidgin/tray/hicolor/48x48/status/pidgin-tray-available.png")
		tray.set_blinking(False)

# connect to the dbus service, retrying every 10 seconds if it fails
def connect():
	finch = False
	bus = dbus.SessionBus()

	while (finch == False):
		try:
			obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
			finch = True
		except:
			finch = False
			time.sleep(10)
	
	return bus, dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

# 99% of this was yanked from the DBus HOWTO on pidgin.im
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

# bus.add_signal_receiver(buddy_online,
# 		dbus_interface = "im.pidgin.purple.PurpleInterface",
# 		signal_name = "BuddySignedOn")

bus, purple = connect()

# for notifications
bus.add_signal_receiver(messnotify,
		dbus_interface = "im.pidgin.purple.PurpleInterface",
		signal_name = "ReceivedImMsg")

# for tray icon
bus.add_signal_receiver(msg_received,
		dbus_interface = "im.pidgin.purple.PurpleInterface",
		signal_name = "ReceivedImMsg")

bus.add_signal_receiver(conv_updated,
		dbus_interface = "im.pidgin.purple.PurpleInterface",
		signal_name = "ConversationUpdated")

tray = gtk.StatusIcon()
tray.set_from_file("/usr/share/pixmaps/pidgin/tray/hicolor/48x48/status/pidgin-tray-available.png")

gtk.main()

loop = gobject.MainLoop()
loop.run()

