#!/usr/bin/env python3
#
#  dir-watcher.py
#  
#  Copyright 2015 PCMan <pcman.tw@gmail.com>
#

import sys
from gi.repository import GLib, Gio # glib/gio

def file_changed(file_monitor, gf, other, event_type):
    file_path = gf.get_path()
    if event_type == Gio.FileMonitorEvent.CHANGED:
        print(file_path, "changed")
    elif event_type == Gio.FileMonitorEvent.DELETED:
        print(file_path, "removed")
    elif event_type == Gio.FileMonitorEvent.CREATED:
        print(file_path, "added")


def main():
    if len(sys.argv) < 2:
        return 1
    loop = GLib.MainLoop()
    gf = Gio.File.new_for_commandline_arg(sys.argv[1])
    # create file alteration monitor
    mon = gf.monitor_directory(0, None)
    mon.connect("changed", file_changed)
    # run the main event loop
    loop.run()
    mon.cancel()

if __name__ == '__main__':
    main()

