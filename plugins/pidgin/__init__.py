#!/usr/bin/env python

import dbus
import ConfigParser

def received_im_cb(account, sender, message, conversation, flags):
    buddy = purple.PurpleFindBuddy(account, sender)
    alias = purple.PurpleBuddyGetAliasOnly(buddy) or sender
    stripped = purple.PurpleMarkupStripHtml(message)
    conv = purple.PurpleFindConversationWithAccount(1, sender, account)
    
    # Don't send a notification if we're looking at the conversation
    if conv and purple.PurpleConversationHasFocus(conv):
        return

    new_conv_only = this.config.getboolean('pidgin', 'new_conversations_only')
    if conv and new_conv_only:
        return

    snooty.simple_notify('Pidgin', alias  + ' says:', stripped)

def buddy_signed_on_cb(buddy):
    alias = purple.PurpleBuddyGetAliasOnly(buddy)
    snooty.simple_notify('Pidgin', str(alias), 'has signed on')

def buddy_signed_off_cb(buddy):
    alias = purple.PurpleBuddyGetAliasOnly(buddy)
    snooty.simple_notify('Pidgin', str(alias), 'has signed off')

def run():
    bus = dbus.SessionBus()
    obj = bus.get_object('im.pidgin.purple.PurpleService', '/im/pidgin/purple/PurpleObject')
    this.purple = dbus.Interface(obj, 'im.pidgin.purple.PurpleInterface')
    
    config = ConfigParser.ConfigParser()
    config.read('plugins/pidgin/pidgin.conf')
    this.config = config

    if this.config.getboolean('pidgin', 'new_message'):
        bus.add_signal_receiver(received_im_cb,
                                dbus_interface='im.pidgin.purple.PurpleInterface',
                                signal_name='ReceivedImMsg')
    
    if this.config.getboolean('pidgin', 'buddy_signed_on'):
        bus.add_signal_receiver(buddy_signed_on_cb,
                                dbus_interface='im.pidgin.purple.PurpleInterface',
                                signal_name='BuddySignedOn')

    if this.config.getboolean('pidgin', 'buddy_signed_off'):
        bus.add_signal_receiver(buddy_signed_off_cb,
                                dbus_interface='im.pidgin.purple.PurpleInterface',
                                signal_name='BuddySignedOff')
