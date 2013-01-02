#!/usr/bin/env python

import sys
from wicd import dbusmanager
from wicd import misc
from wicd.translations import _

def status_changed_cb(state, details):
    # Nothing has changed
    if state == this.prev_state:
        return

    if state == misc.CONNECTING:
        wired_connecting = wired.CheckIfWiredConnecting()
        wireless_connecting = wireless.CheckIfWirelessConnecting()
        stat = _('Connecting')
        if wireless_connecting:
            iwconfig = wireless.GetIwconfig()
            essid = wireless.GetCurrentNetwork(iwconfig)
            snooty.simple_notify('wicd', essid, stat)
        if wired_connecting:
            snooty.simple_notify('wicd', _('Wired Network'), stat)

    elif state in (misc.WIRELESS, misc.WIRED) and this.prev_state == misc.CONNECTING:
        wired_ip = wired.GetWiredIP('')
        iwconfig = wireless.GetIwconfig()
        network = wireless.GetCurrentNetwork(iwconfig)
        wireless_ip = wireless.GetWirelessIP('')

        if wired.CheckPluggedIn() and wired_ip:
            snooty.simple_notify('wicd', _('Wired Network'), _('Connected'))
        elif network and wireless_ip:
            snooty.simple_notify('wicd', network, _('Connected'))

    elif state == misc.NOT_CONNECTED and this.prev_state in (misc.WIRELESS, misc.WIRED):
        if this.prev_state == misc.WIRED:
            snooty.simple_notify('wicd', _('Wired Network'), _('Not connected'))
        else: # this.prev_state == misc.WIRELESS
            snooty.simple_notify('wicd', _('Wireless Network'), _('Not connected'))

    this.prev_state = state

def run():
    try:
        dbusmanager.connect_to_dbus()
    except DBusException:
        print >> sys.stderr, 'snooty: wicd: Cannot connect to the daemon.'
        raise

    bus = dbusmanager.get_bus()

    dbus_ifaces = dbusmanager.get_dbus_ifaces()
    this.daemon = dbus_ifaces['daemon']
    this.wired = dbus_ifaces['wired']
    this.wireless = dbus_ifaces['wireless']

    this.prev_state = -1

    bus.add_signal_receiver(status_changed_cb,
                            dbus_interface='org.wicd.daemon',
                            signal_name='StatusChanged')
