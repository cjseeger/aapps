import json
import requests, requests_cache

# select basic sqlite caching backend
requests_cache.configure('http_cache')

class GeoJSONCoder(object):

    def geometry(self, item):
        # heuristics for detecting item type (Polygon, Point, etc.)

        # item contains a polygon key

        if 'polygon' in item.keys():
            return 'Polygon'

        # item contains a gisx/y or point_lat/lng key

        if set(item.keys()).intersection(set(['gisx', 'point_lat'])):
                return 'Point'


    def as_feature(self, item):

        geom = self.geometry(item)

        f = {
                'type' : 'Feature',
                'geometry' : {},
                'properties' : {}
            }

        # convert Point geometry object
        if geom == 'Point':
            f['geometry'] = { 'type' : 'Point' }

            try:
                coordinates = [float(item.pop('gisx')), float(item.pop('gisy'))]
            except KeyError:
                coordinates = [item.pop('point_lng'), item.pop('point_lat')]


        # convert Polygon geometry object
        # TODO MultiPolygon?
        if geom == 'Polygon':
            f['geometry'] = { 'type' : 'Polygon' }

            polygon = item.pop('polygon')
            points = [pp.split(':') for pp in polygon.split('|')]
            coordinates = [[float(coords[0]), float(coords[1])] for coords in points]

        # add coord pairs to geom objects
        f['geometry']['coordinates'] = [coordinates] # list-of-lists for coord-pairs

        # add the remainder of the fields tot properties
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
        if cache:
            with requests_cache.enabled():
                r = requests.get(uri, headers={'Accept' : 'application/json'})
        else:
            with requests_cache.disabled():
                r = requests.get(uri, headers={'Accept' : 'application/json'})

        # last uri-part is dataset name and dictionary key
        key = uri.split('/')[-1]

        return r.json.get(key)

    def convert(self, uri, cache=True):
        data = self.fetch(uri)
        fc = self.as_feature_collection(data)

        return fc


G = GeoJSONCoder()
u = 'http://api.antwerpen.be/v1/infrastructuur/politie'
u = 'http://api.antwerpen.be/v1/geografie/statistischesector'
#d = G.fetch(u)
gj = G.convert(u)
print json.dumps(gj, sort_keys=True, indent=4)


