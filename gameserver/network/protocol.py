import simplejson as json
from twisted.internet import protocol

class JsonReceiver(protocol.Protocol):

    def dataReceived(self, data):
        self.objectReceived(json.loads(data))

    def objectReceived(self, obj):
        raise NotImplementedError

    def sendObject(self, obj=None, **kwargs):
        dict = {}
        if obj is not None:
            dict.update(obj)
        if kwargs is not None:
            dict.update(kwargs)
        self.transport.write(json.dumps(dict))
