#!/usr/bin/env python
import optparse
from twisted.protocols.basic import LineReceiver, NetstringReceiver
from twisted.internet.protocol import ClientFactory
from twisted.internet.stdio import StandardIO

class UserInputProtocol(LineReceiver):

    from os import linesep as delimiter  #@UnusedImport

    def __init__(self, callback):
        self.callback = callback

    def lineReceived(self, line):
        self.callback(line)

class GameClientProtocol(NetstringReceiver):

    def connectionMade(self):
        StandardIO(UserInputProtocol(self.sendString))

    def stringReceived(self, line):
        print line

class GameClientFactory(ClientFactory):
    protocol = GameClientProtocol

def parse_args():
    usage = "usage: %prog [options] [hostname]:port"

    parser = optparse.OptionParser(usage)

    _, args = parser.parse_args()

    if not args:
        print parser.format_help()
        parser.exit()

    address = args[0]

    if ':' not in address:
        host, port = '127.0.0.1', address
    else:
        host, port = address.split(':', 1)

    if not port.isdigit():
        parser.error('Ports must be integers.')

    return host, int(port)

def run_client():
    from twisted.internet import reactor
    host, port = parse_args()
    factory = GameClientFactory()
    reactor.connectTCP(host, port, factory)  #@UndefinedVariable
    reactor.run()  #@UndefinedVariable

if __name__ == '__main__':
    run_client()
