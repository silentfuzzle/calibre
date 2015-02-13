#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2014, Kovid Goyal <kovid at kovidgoyal.net>'

import os, sys

# For some reason Qt 5 crashes on some linux systems if the fork() is done
# after the Qt modules are loaded in calibre.gui2. We also cannot do a fork()
# while python is importing a module. So we use this simple launcher module to
# launch all the GUI apps, forking before Qt is loaded and not during a
# python import.

is_detached = False

def do_detach(fork=True, setsid=True, redirect=True):
    global is_detached
    if fork:
        # Detach from the controlling process.
        if os.fork() != 0:
            raise SystemExit(0)
    if setsid:
        os.setsid()
    if redirect:
        from calibre.constants import plugins
        plugins['speedup'][0].detach(os.devnull)
    is_detached = True

def detach_gui():
    from calibre.constants import islinux, isbsd, DEBUG
    if (islinux or isbsd) and not DEBUG and '--detach' in sys.argv:
        do_detach()

def init_dbus():
    from calibre.constants import islinux, isbsd
    if islinux or isbsd:
        from dbus.mainloop.glib import DBusGMainLoop, threads_init
        threads_init()
        DBusGMainLoop(set_as_default=True)

def calibre(args=sys.argv):
    detach_gui()
    init_dbus()
    from calibre.gui2.main import main
    main(args)

def ebook_viewer(args=sys.argv):
    detach_gui()
    init_dbus()
    from calibre.gui2.viewer.main import main
    main(args)

def gui_ebook_edit(path=None, notify=None):
    ' For launching the editor from inside calibre '
    init_dbus()
    from calibre.gui2.tweak_book.main import gui_main
    gui_main(path, notify)

def ebook_edit(args=sys.argv):
    detach_gui()
    init_dbus()
    from calibre.gui2.tweak_book.main import main
    main(args)

def option_parser(basename):
    if basename == 'calibre':
        from calibre.gui2.main import option_parser
    elif basename == 'ebook-viewer':
        from calibre.gui2.viewer.main import option_parser
    elif basename == 'ebook-edit':
        from calibre.gui2.tweak_book.main import option_parser
    return option_parser()
