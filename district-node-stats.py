#!/usr/bin/env python3

import fiona
from shapely.geometry import shape, Point
import json
import urllib.request, urllib.error

#
# Some configuration
#

# The district shape file in WGS84 (EPSG:4326)
DISTRICT_SHAPEFILE = "static-data/StatistischeBezirkeAachen_wgs84/StatistischeBezirkeAachen.shp"

# The name of the polygonproperty which names the districts
DISTRICT_NAME_PROPERTY = "ST_NAME"

# The location of the nodes.json
NODES_JSON_URI = "http://freifunk-aachen.de/map/nodes.json"
NODES_JSON_PATH = "data/ffac-nodes.json"


# Read the city district boundaries from shape file
district_shapes = {}
district_stats = {}
with fiona.open(DISTRICT_SHAPEFILE, "r") as districts:
	for district in districts:
		district_name = district["properties"][DISTRICT_NAME_PROPERTY]
		district_shapes[district_name] = shape(district["geometry"])
		district_stats[district_name] = 0

# Download nodes.json
try:
	request = urllib.request.urlopen(NODES_JSON_URI)
	with open(NODES_JSON_PATH, "wb") as f:
		f.write(request.read())
except urllib.error.URLError as e:
	print("nodes.json download failed: ", e.reason)
	print("Using cached data (if available)...")

# Extract position of nodes from nodes.json
coords = {}
nogeo = 0
withgeo = 0
with open(NODES_JSON_PATH, "r") as f:
	nodes = json.load(f)["nodes"]
	for node in nodes:
		if node["geo"] is not None:
			lat, lon = node["geo"]
			coords[node["name"]] = Point(lon, lat)	
			withgeo += 1
		else:
			nogeo += 1
print("Nodes with coordinates: ", withgeo)
print("Nodes without coordinates: ", nogeo)


# Tally nodes within the individual district shapes
for _,node in coords.items():
	for district, shape in district_shapes.items():
		if shape.contains(node):
			district_stats[district] += 1

print(json.dumps(district_stats, sort_keys=True, indent=4, separators=(",", ":"), ensure_ascii=False))
print("Sum of nodes with coordinates within city limits: ", sum([x for _,x in district_stats.items()]))

