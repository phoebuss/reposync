#!/usr/bin/env python
import socket
import struct
import subprocess
import os
from time import sleep
import logging

IP = '127.0.0.1'
PORT = 3456
CURRDIR = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger('reposync').info

def msgPack(msg):
    return struct.pack('!I%ds' % len(msg), len(msg), msg)

def msgUnpack(buf):
    try:
        n, = struct.unpack('!I', buf[:4])
        if n+4 > len(buf): return 0, '', buf
        msg, = struct.unpack('!%ds' % n, buf[4:n+4])
        return n, msg, buf[n+4:]
    except:
        return 0, '', ''

def processMsg(msg):
    try:
        project, oldref, newref, branch = msg.split()
        if branch != 'refs/heads/master': return
        path = CURRDIR + '/' + project

        cmd = 'git rev-list master -1'
        proc = subprocess.Popen(cmd.split(), cwd=path, stdout=subprocess.PIPE)
        ref =  proc.stdout.readline().strip()
        proc.stdout.close()
        proc.wait()

        if ref != newref:
            LOG('Received pull request')
            LOG('------------------------------------------------------------------------')
            LOG('')
            cmd = 'git pull --no-edit origin master:master'
            proc = subprocess.Popen(cmd.split(), cwd=path)
            proc.wait()
            LOG('')
            LOG('------------------------------------------------------------------------')
    except Exception as e:
        LOG(e)
        return

def connectServer(ip, port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
   while True:
       try:
           s.connect((ip, port))
       except socket.error as e:
           if e.errno == 111:
               LOG('Cannot reach the server! Try again!')
               sleep(10)
               continue
           else:
               LOG(e)
               raise e
       break
   s.setblocking(0)
   LOG('Connected')
   return s

def main():
    try:
        s = connectServer(IP, PORT)
        rxbuf = ''
        while True:
            try:
                rxbuf += s.recv(1024)
            except socket.error as e:
                if e.errno == 11:
                    sleep(1)
                    continue
                elif e.errno == 110:
                    LOG('Timeout, reset connection to server')
                    s.close()
                    s = connectServer(IP, PORT) 
                    rxbuf = ''
                    continue
                else:
                    LOG(e)
                    raise e
            l, msg, rxbuf = msgUnpack(rxbuf)
            if (not l):
                LOG('Unknown packet, reset connection to server')
                s.close()
                s = connectServer(IP, PORT) 
                rxbuf = ''
                continue
            while l:
                processMsg(msg)
                l, msg, rxbuf = msgUnpack(rxbuf)
    except KeyboardInterrupt:
        try:
            s
        except NameError:
            s = None
        if (s):
            s.close()
        return

if __name__ == '__main__':
    main()
