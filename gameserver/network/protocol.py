import simplejson as json
from twisted.protocols import basic

class JsonReceiver(basic.LineOnlyReceiver):

    def lineReceived(self, data):
        try:
            decoded_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            self.invalidJsonReceived(data)
        else:
            self.objectReceived(decoded_data)

    def objectReceived(self, obj):
        raise NotImplementedError

    def invalidJsonReceived(self, data):
        pass

    def sendObject(self, obj=None, **kwargs):
        dict = {}
        if obj is not None:
            dict.update(obj)
        if kwargs is not None:
            dict.update(kwargs)
        self.sendLine(json.dumps(dict))
