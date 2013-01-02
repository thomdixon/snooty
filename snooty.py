#!/usr/bin/env python

__author__ = 'Thomas Dixon'
__license__ = 'GPL'

import imp
import sys
import os
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from subprocess import Popen, PIPE
from textwrap import TextWrapper
from ConfigParser import ConfigParser

PLUGINS_DIR = 'plugins'

class Snooty(dbus.service.Object):
    '''Snooty is a simple notification daemon for StumpWM.'''
    def __init__(self, config):
        self.config = config
        self._wrapper = TextWrapper(width=self.config.getint('snooty', 'max_line_width'))
        loop = DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName('org.freedesktop.Notifications',
                                        bus=dbus.SessionBus(mainloop=loop))
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/Notifications')

    @dbus.service.method('org.freedesktop.Notifications')
    def Notify(self,
               app_name,
               replaces_id,
               app_icon,
               summary, 
               body, 
               actions,
               hints,
               expire_timeout):
        dev_null = open(os.devnull, 'w')

        app_name = app_name.encode('unicode_escape')
        summary = summary.encode('unicode_escape')
        body = body.encode('unicode_escape')
        
        # Print the notification as a message
        if self.config.getboolean('snooty', 'use_message'):
            fill = self._wrapper.fill
            message = self.config.get('snooty', 'message_format')
            message = message.replace('%a', fill(app_name))
            message = message.replace('%s', fill(summary))
            message = message.replace('%b', fill(body))

            echo = Popen(['echo', '-e', message], stdout=PIPE)
            Popen(['stumpish', '-e', 'echo'], stdin=echo.stdout, stdout=dev_null)

        # Then add it to the Notifications in the mode-line
        if self.config.getboolean('snooty', 'use_notifications'):
            notification = self.config.get('snooty', 'notifications_format')
            notification = notification.replace('%a', app_name)
            notification = notification.replace('%s', summary)
            notification = notification.replace('%b', body)
            echo = Popen(['echo', '-e', notification], stdout=PIPE)
            Popen(['stumpish', '-e', 'notifications-add'],
                  stdin=echo.stdout, 
                  stdout=dev_null)

        dev_null.close()

    def simple_notify(self, app_name, summary, body):
        self.Notify(app_name, 0, None, summary, body, None, None, 0)

if __name__ == '__main__':
    config = ConfigParser()
    config.read('snooty.conf')
    
    snooty = Snooty(config)
        
    # Load plugins
    plugins_whitelist = map(lambda x: x.strip(), 
                            config.get('snooty', 'plugins').split(','))
    plugins = []
    for i in os.listdir(PLUGINS_DIR):
        if not i in plugins_whitelist:
            continue
        path = os.path.join(PLUGINS_DIR, i)
        if not os.path.isdir(path) or not '__init__.py' in os.listdir(path):
            print >> sys.stderr, 'snooty: skipping', i
            continue
        module = imp.load_module('__init__', *imp.find_module('__init__', [path]))
        module.this = module
        module.snooty = snooty
        module.run()
        plugins.append(i)
    if plugins:
        print >> sys.stderr, 'snooty: loaded plugins:', ', '.join(plugins)
        
    # Go time
    gobject.MainLoop().run()
