#!/usr/bin/env python

import socket, select, argparse
import struct

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

def getArgs():
    parser = argparse.ArgumentParser(description='a broadcast server')
    parser.add_argument('-c', '--ip', type=str, help='ip address to be listened', default='0.0.0.0')
    parser.add_argument('-p', '--port', type=int, help='port to be listened', default=3456)
    return parser.parse_args()

def main():
    args = getArgs()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args.ip, args.port))
    s.listen(1)
    s.setblocking(0)
    
    epoll = select.epoll()
    epoll.register(s.fileno(), select.EPOLLIN)
    
    try:
        conn = {}; txbuf = {}; rxbuf = {}
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == s.fileno():
                    c, addr = s.accept()
                    c.setblocking(0)
                    conn[c.fileno()] = c
                    txbuf[c] = ''
                    rxbuf[c] = ''
                    epoll.register(c.fileno(), select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    c = conn[fileno]
                    n = c.send(txbuf[c])
                    txbuf[c] = txbuf[c][n:]
                    if not len(txbuf[c]):
                        epoll.modify(fileno, select.EPOLLIN)
                elif event & select.EPOLLIN:
                    c = conn[fileno]
                    try:
                        rxbuf[c] += c.recv(1024)
                    except Exception as e:
                        print e
                        c.close()
                        epoll.unregister(fileno)
                        del rxbuf[c]
                        del txbuf[c]
                        del conn[fileno]
                        continue
                    if not len(rxbuf[c]):
                        c.close()
                        epoll.unregister(fileno)
                        del rxbuf[c]
                        del txbuf[c]
                        del conn[fileno]
                        continue
                    l, msg, rxbuf[c] = msgUnpack(rxbuf[c])
                    if l:
                        for sock in conn.values():
                            if sock == c: continue
                            txbuf[sock] += msgPack(msg)
                            epoll.modify(sock.fileno(), select.EPOLLOUT)
                else:
                    print fileno, event
    
    except KeyboardInterrupt:
        epoll.close()
        s.close()

if __name__ == '__main__':
    main()
