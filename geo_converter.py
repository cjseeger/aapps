import json
import requests, requests_cache

requests_cache.configure('http_cache')

#class DataTankAdaptor(object):
#    def __init__(self, res_uri=None):
#        if res_uri:
#            self.res_uri = res_uri
#            self.resources = self.fetch(res_uri).get('resources')

class GeoJSONCoder(object):

    def as_feature(self, item):

        f = {
                'type' : 'Feature',
                'geometry' : { 'type' : 'Point' },
                'properties' : {}
            }

        try:
            coordinates = [float(item.pop('gisx')), float(item.pop('gisy'))]
        except KeyError:
            coordinates = [item.pop('point_lng'), item.pop('point_lat')]

        f['geometry']['coordinates'] = coordinates

        for k, v in item.iteritems():
            f['properties'][k] = v

        return f

    def as_feature_collection(self, items):
        fc = {'type' : 'FeatureCollection',
                'features' : []
                }

        for i, item in enumerate(items):
            geo_item = self.as_feature(item)
            geo_item['id'] = i
            fc['features'].append(geo_item)

        return fc

    def fetch(self, uri, cache=True):
        r = requests.get(uri, headers={'Accept' : 'application/json'})
        key = uri.split('/')[-1]
        return r.json.get(key)

    def convert(self, uri, cache=True):
        data = self.fetch(uri)
        fc = self.as_feature_collection(data)

        return fc


G = GeoJSONCoder()
u = 'http://api.antwerpen.be/v1/infrastructuur/politie'
gj = G.convert(u)
print json.dumps(gj, sort_keys=True, indent=4)


