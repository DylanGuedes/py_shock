class Bus(object):
    def __init__(self, jsonstring):
        attrs = json.loads(jsonstring)
        self.lat = attrs['lat']
        self.lon = attrs['lon']
        self.description = attrs['description']
        self.capabilities = attrs['capabilities']
        self.status = attrs['status']


