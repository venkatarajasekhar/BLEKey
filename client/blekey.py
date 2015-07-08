#!/usr/bin/python2
import cmd
import pygatt
import pprint as pp
import os

DEFAULT_MAC = "D4:34:E8:CA:6F:6A"
DEFAULT_TIMEOUT = 15


class BLEKeyClient(cmd.Cmd):
    """Derp de derp"""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.macs = []
        self.prompt = '\033[1;30m[n/c]\033[1;m blekey> '

    def emptyline(self):
        pass

    def do_scan(self, arg):
        print("scanning...")
        scan_result = pygatt.util.lescan()
        pp.pprint(scan_result)
        for item in scan_result:
            self.macs.append(item['address'])

    def help_scan(self):
        print("The scan command uses hcitool to probe for BLE devices.")

    def do_connect(self, mac):
        if not mac:
            mac = DEFAULT_MAC
        print("connecting to %s" % mac)
        self.bk = pygatt.BluetoothLEDevice(mac, app_options="-t random")
        self.bk.connect(timeout=DEFAULT_TIMEOUT)
        self.prompt = "\033[1;34m[%s]\033[1;m blekey>" % mac

    def complete_connect(self, text, line, begidx, endidx):
        if not text:
            completions = self.macs[:]
        else:
            completions = [f
                           for f in self.macs
                           if f.startswith(text)
                           ]
        return completions

    def help_connect(self):
        print("Usage: connect <MAC_ADDRESS>")
        print("If you don't know the device's MAC try using scan first.\
              Tab completion is your friend.")

    def do_tx(self, data):
        print("sending...")
        self.bk.char_write(0x0d, [0x01])

    def help_tx(self):
        print("Currently the tx command sends the card read by BLEKey")

    def do_readcards(self, _):
        print("reading last cards...")
        last_cards = self.bk.char_read_hnd(0x0b, timeout=DEFAULT_TIMEOUT)
        for i in range(0, 3):
            start = i * 7
            print ("%d. %d bit card:" % (i, last_cards[start])),
            card_data = reversed(last_cards[start + 1:start + 6])
            fixed = ''.join('{:02x}'.format(x) for x in card_data)
            print ("0x%s" % fixed)
            fixed = None
            card_data = None

    def help_readcards(self):
        print("readcards reads the last three cards")

    def do_disconnect(self, _):
        try:
            self.bk.disconnect()
            self.prompt = '\033[1;30m[n/c]\033[1;m blekey> '
        except AttributeError:
            print("There is no connection to disconnect.")

    def help_disconnect(self):
        print("Usage: disconnect")
        print("Disconnects gatttool from the BLE device.")

    def do_EOF(self, line):
        try:
            self.bk.disconnect()
            del self.bk
        except AttributeError:
            pass
        return True

    def help_EOF(self):
        print("Use exit, quit or ^D to quit the client.")

    do_exit = do_quit = do_EOF
    help_exit = help_quit = help_EOF

if __name__ == '__main__':
    if os.getuid() is not 0:
        print("Warning BLE tools need to be run as root! UID 0 not detected")
    BLEKeyClient().cmdloop()