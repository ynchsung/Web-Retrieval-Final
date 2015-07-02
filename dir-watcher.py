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
    h = http.client.HTTPConnection('127.0.0.1', 7122)
    h.request(method="POST", url="/monitor?type=%s"%(typ,), body=json.dumps(file_list))
    h.close()

# queued file changes
files_to_add = []
files_to_change = []
files_to_remove = []

timeout_id = 0 # timeout handler

# called when timeout
def handle_queued_changes():
    global files_to_add, files_to_change, files_to_remove, timeout_id
    timeout_id = 0

    if files_to_add:
        send_request(files_to_add, "added")
        files_to_add = []
    if files_to_remove:
        send_request(files_to_remove, "removed")
        files_to_remove = []
    if files_to_change:
        send_request(files_to_change, "changed")
        files_to_change = []
    return False


def file_changed(file_monitor, gf, other, event_type):
    if timeout_id == 0: # timeout handler is not installed
        GLib.timeout_add(3000, handle_queued_changes) # delay for 3 seconds

    file_path = gf.get_path()
    if event_type == Gio.FileMonitorEvent.CHANGED:
        if file_path not in files_to_change: # avoid frequent changes of the same file
            files_to_change.append(file_path)
    elif event_type == Gio.FileMonitorEvent.DELETED:
        files_to_remove.append(file_path)
    elif event_type == Gio.FileMonitorEvent.CREATED:
        files_to_add.append(file_path)


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

