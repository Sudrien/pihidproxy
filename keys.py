
#!/usr/bin/env python2

import evdev, time
from evdev import InputDevice, categorize, ecodes

import io
from select import select
import os
import sys

if not os.geteuid() == 0:
    sys.exit("\nOnly root can run this script\n")

# Load the configuration file, which is NOT an INI
config = {}
with open(os.path.dirname(os.path.abspath(__file__)) + "/config.conf") as f:
    for line in f:
        name, var = line.partition("=")[::2]
        config[name.strip()] = var.lower().strip().strip('\"')



dev = {}
NULL_CHAR = chr(0)
#print config["devicename"]

while not dev:
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.uniq == config["devicename"]:
                a = InputDevice(device.path)
                dev[a.fd] = a
                a.grab()

        for d in dev.values(): print(d)
    except:
        print "No keyboard - waiting..."
        time.sleep(10)

def write_report(report):
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(bytes(report))

unk = -1 #None

hid_keyboard = [
    0,  0,  0,  0, 30, 48, 46, 32, 18, 33, 34, 35, 23, 36, 37, 38,
    50, 49, 24, 25, 16, 19, 31, 20, 22, 47, 17, 45, 21, 44,  2,  3,
    4,  5,  6,  7,  8,  9, 10, 11, 28,  1, 14, 15, 57, 12, 13, 26,
    27, 43, 43, 39, 40, 41, 51, 52, 53, 58, 59, 60, 61, 62, 63, 64,
    65, 66, 67, 68, 87, 88, 99, 70,119,110,102,104,111,107,109,106,
    105,108,103, 69, 98, 55, 74, 78, 96, 79, 80, 81, 75, 76, 77, 71,
    72, 73, 82, 83, 86,127,116,117,183,184,185,186,187,188,189,190,
    191,192,193,194,134,138,130,132,128,129,131,137,133,135,136,113,
    115,114,unk,unk,unk,121,unk, 89, 93,124, 92, 94, 95,unk,unk,unk,
    122,123, 90, 91, 85,unk,unk,unk,unk,unk,unk,unk,111,unk,unk,unk,
    unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,
    unk,unk,unk,unk,unk,unk,179,180,unk,unk,unk,unk,unk,unk,unk,unk,
    unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,unk,
    unk,unk,unk,unk,unk,unk,unk,unk,111,unk,unk,unk,unk,unk,unk,unk,
    29, 42, 56,125, 97, 54,100,126,164,166,165,163,161,115,114,113,
    150,158,159,128,136,177,178,176,142,152,173,140,unk,unk,unk,unk
    ]

# https://github.com/torvalds/linux/blob/master/drivers/hid/hid-input.c
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h later?



#for i in range(len(hid_keyboard)):
#    if hid_keyboard[i] > -1:
#        print("hid %d: %d %s" % (i, hid_keyboard[i], ecodes.KEY[ hid_keyboard[i] ] ))
#    else:
#        print("hid %d: %d %s" % (i, hid_keyboard[i], ""))

shift_held = False

#loop
while True:
    r, w, x = select(dev, [], [])
    for fd in r:
        for event in dev[fd].read():
            if event.type == ecodes.EV_KEY:
                data = categorize(event)
                if event.code == evdev.ecodes.KEY_LEFTSHIFT or event.code == evdev.ecodes.KEY_RIGHTSHIFT:
                    shift_held = data.keystate != 0
                    continue # don't send
                if data.keystate == 1 or data.keystate == 2:  # Down & hold events
                    if data.scancode in hid_keyboard:
#                        print data
                        if shift_held:
                            write_report(chr(32)+NULL_CHAR + chr ( hid_keyboard.index(data.scancode) ) + NULL_CHAR*5)
                        else:
                            write_report(NULL_CHAR*2 + chr ( hid_keyboard.index(data.scancode) ) + NULL_CHAR*5)
                    else:
                        # media key handler, supposedly. Not working for stuff like mute key.
                        print data
                        write_report(NULL_CHAR*2 + chr ( data.scancode ) + NULL_CHAR*5)
                if data.keystate == 0: # Up events
                    write_report(NULL_CHAR*8)
