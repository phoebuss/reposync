#!/usr/bin/env python
import socket
import struct
from time import sleep

def msgPack(msg):
    return struct.pack('!I%ds' % len(msg), len(msg), msg)

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 3456))
        while True:
            try:
                s.send(msgPack('sync 0 0 0'))
            except Exception:
                s.close();
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', 3456))
                continue
            sleep(60)
    except KeyboardInterrupt:
        s.close()
        return
    except socket.error as e:
        if e.errno == 32:
            print 'Server dropped the connection!'
            return
        elif e.errno == 111:
            print 'Cannot reach the server!'
            return
        else:
            raise e

if __name__ == '__main__':
    main()
