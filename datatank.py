import json
import requests, requests_cache
from geojson import GeoJSONCoder

# select basic sqlite caching backend
requests_cache.configure('http_cache')

class Resource(object):
    def __init__(self, uri, name=None, package=None):
        self.uri = uri
        self.name = name
        self.package = package
        self.lbl = ''.join([self.name, ' (', self.package, ')'])

    def __unicode__(self):
        # TODO not working?
        return self.lbl

    # TODO caching does not take into account Accept-headers!!!

    def csv(self):
        print self.uri
        r = requests.get(self.uri, headers={'Accept' : 'text/csv'})
        return r.text

    def json(self, syntax='plain'):
        r = requests.get(self.uri, headers={'Accept' : 'application/json'})
        data = r.json

        if syntax == 'geo':
            G = GeoJSONCoder()
            data = G.convert(self.uri)

        return data

class DataTankWrapper(object):
    def __init__(self, uri):
        self.uri = uri

    def _fetch(self, uri, cache=True):
        if cache:
            with requests_cache.enabled():
                r = requests.get(uri, headers={'Accept' : 'application/json'})
        else:
            with requests_cache.disabled():
                r = requests.get(uri, headers={'Accept' : 'application/json'})

        return r.json

    def resources(self):
        u  = '/'.join([self.uri, 'TDTInfo/Resources'])
        data = self._fetch(u).get('Resources')
        del data['TDTInfo']
        del data['TDTStats']
        del data['TDTAdmin']

        dt_resources = []

        for package_name, resources in data.iteritems():
            for resource_name, values in resources.iteritems():
                #r = {}
                #r['package'] = '/'.join([self.uri, package_name])
                r_uri = '/'.join([self.uri, package_name, resource_name])
                r = Resource(r_uri, resource_name, package_name)
                dt_resources.append(r)

        return dt_resources

A = DataTankWrapper('http://api.antwerpen.be/v1')
res = A.resources()
print res
#print json.dumps(res, sort_keys=True, indent=4)
