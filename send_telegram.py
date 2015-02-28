import socket
import telnetlib
import sys
import re


def test(a, b, host='127.0.0.1', port=9999):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(10)
    print sock.send('status_online \r\n')
    print expect(sock, 'SUCCESS')
    print 'status_online'
    sock.send("msg T80S_ALERTS testinho \r\n")
    print expect(sock)
    print 'msg'

def expect(sock, message='\r\n'):
    res = ''
    for i in range(10):
        res += str(sock.recv(1024))
        if res:
            s = re.search(message, res)
        else:
            s = None
        if s:
            break
    if (not s):
        raise StandardError
    if s:
        return s
    else:
        return res


def telegram_msg(peer, msg, ip='127.0.0.1', port=9999, timeout=60):
    t = telnetlib.Telnet(ip, port, timeout)

    print 'Going Online...'
    t.write('status_online \r\n')
    if t.expect(['SUCCESS'], timeout=5)[1]:
        print 'SUCCESS'
    else:
        print 'TIMEOUT'

    print 'Marking as read'
    t.write('mark_read T80S_ALERTS \r\n')
    if t.expect(['SUCCESS'], timeout=5)[1]:
        print 'SUCCESS'
    else:
        print 'TIMEOUT'

    print 'Sending %s to %s' % (msg, peer)
    t.write('msg T80S_ALERTS test \r\n')
    if t.expect(['SUCCESS'], timeout=5)[1]:
        print 'SUCCESS'
    else:
        print 'TIMEOUT'

    t.close()

if __name__ == '__main__':

    # if len(sys.argv) > 2:
    # telegram_msg('', '')

    telegram_msg('T80_ALERTS', 'GRB ALERT process.variation.burst;em.gamma ra 74.741, dec 25.314, alt 49.40 deg - http://192.168.20.5/events//html/ivo%3A%2F%2Fnasa.gsfc.gcn%2FSWIFT%23BAT_GRB_Pos_532871-729', '127.0.0.1')


    from teletap.libteletap import *
    CLIENT = Teletap(binary='/usr/local/bin/telegram-cli', keyfile='/etc/telegram-cli/tg-server.pub', logs='/home/chimera/telegram.log', quiet=False)
