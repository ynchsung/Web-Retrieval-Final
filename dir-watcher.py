#!/usr/bin/env python3
#
#  dir-watcher.py
#
#  Copyright 2015 PCMan <pcman.tw@gmail.com>
#

import sys
import json
import http.client
from gi.repository import GLib, Gio # glib/gio

def send_request(file_list, typ):
    h = http.client.HTTPConnection('linux10.csie.org', 7122)
    h.request(method="POST", url="/monitor?type=%s"%(typ,), body=json.dumps(file_list))
    h.close()

def file_changed(file_monitor, gf, other, event_type):
    file_path = gf.get_path()
    if event_type == Gio.FileMonitorEvent.CHANGED:
        send_request([file_path], "changed")
    elif event_type == Gio.FileMonitorEvent.DELETED:
        send_request([file_path], "removed")
    elif event_type == Gio.FileMonitorEvent.CREATED:
        send_request([file_path], "added")


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

