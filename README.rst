
======
Snooty
======

About
=====

Snooty is a simple DBus notification daemon for StumpWM which sports a
rudimentary plugin system. Notifications can be displayed either
through ``stumpwm:message``, ``contrib/notifications.lisp``, or both.

Usage
=====

Installation
------------

You can simply execute::

    $ python snooty.py &

or add the above to wherever you launch your userland daemons once X
starts.  Because Snooty is written in Python, it uses ``stumpish`` in
order to communicate with StumpWM, and thus it is necessary that your
``PATH`` be configured accordingly.

Configuration
-------------

Current configuration options are as follows.

``message_format``
    The format of the notification as displayed by
    ``stumpwm:message``.  Currently, the possible formatters include
    ``%a`` for the application name, ``%s`` for the summary or title
    of the notification, and ``%b`` for the body of the notification.

``notifications_format``
    This is the format of the notification for use with
    ``notifications-add`` as provided by
    ``contrib/notifications.lisp``. The available formatters are
    equivalent to the above.

``max_line_width``
    This is the maximum line width for notifications displayed using
    ``stumpwm:message``.

``use_message``
    Should we display notifications using ``stumpwm:message``?

``use_notifications``
    Should we display notifications using ``notifications-add``?

``plugins``
    This is a whitelist of available plugins that should be loaded
    when the daemon starts.
Bugs
----

There are a number of known bugs that can make using this software
annoying.

- *Snooty is not actually a daemon.* 
  I have yet to write the code for daemonizing Snooty and controlling
  the resulting process. To run Snooty in the background using bash,
  zsh, or similar, execute::

   $ python snooty.py & disown

   To stop Snooty, you must find the pid and ``kill`` it.

- *Currently there is no support for translations.*
  I simply haven't gotten around to implementing localizations, thus
  everything is hardcoded in English.

- *Plugins run in the main thread.*
  This means you have to be very careful in how you design them (e.g.,
  using timeouts instead of hogging the processor).

- *When a plugin fails to load, so does the daemon.*
  Any exception raised during the loading of a plugin is not caught,
  and will thus prevent the daemon from starting. This can be
  particularly annoying if you have plugins listed in the ``plugins``
  configuration option that you don't have the dependencies to run
  (e.g., a wicd plugin when you use NetworkManager).

Plugins
-------

By default, Snooty only displays notifications announced through
``org.freedesktop.Notifications.Notify``. To make the daemon more
useful, additional functionality may be provided via plugins. A plugin
is simply a Python package in the ``plugins`` directory, with the
``__init__.py`` file containing a ``run()`` function which acts as an
entry point. The magic variables ``snooty`` and ``this`` are set
within the package when the plugin is loaded. ``snooty`` is a
reference to our instance of the ``Snooty`` class, and ``this`` refers
to the package itself (similar to ``self`` for Python classes). All
included plugins are listed below.

pidgin
~~~~~~

This plugin provides notifications for some of the more common events
in the pidgin instant messaging client, in particular: instant message
received, new conversation started, buddy signed on, and buddy signed
off.

Configuration
+++++++++++++

The available configuration options are the following.

``new_message``
    Send a notification when a new message is received, but the
    conversation does not currently have focus.

``new_conversations_only``
    Only send a notification for a new message when that message
    initiates a new conversation.

``buddy_signed_on``
    Self-explanatory.

``buddy_signed_off``
     Also self-explanatory.

Bugs
++++

- Currently, when ``buddy_signed_on`` is enabled, and the user signs
  on, a flood of notifications occurs. The fix for this is simple, I
  just have to get around to it.

wicd
~~~~

A simple plugin to announce your network connectivity status using
``wicd``. Currently, notifications are given for "Disconnected,"
"Connecting," and "Connected" statuses.
