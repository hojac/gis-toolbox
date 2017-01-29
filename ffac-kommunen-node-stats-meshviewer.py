#!/usr/bin/env python3

import fiona
from shapely.geometry import shape, Point
import json
import urllib.request, urllib.error
import matplotlib
import datetime


#
# Some configuration
#

BASE_DIR = "/opt/gis-toolbox/"

# The district shape file in WGS84 (EPSG:4326)
DISTRICT_SHAPEFILE = BASE_DIR + "static-data/ffac_Kommunen_wgs84/ffac_Kommunen.shp"

# The name of the polygonproperty which names the districts
DISTRICT_NAME_PROPERTY = "GN"

# The location of the nodes.json
NODES_JSON_URI = "http://data.aachen.freifunk.net/nodes.json"
NODES_JSON_PATH = BASE_DIR + "data/ffac-nodes.json"

# The output path of the statistics (json format)
# Use None to print to stdout
STATISTICS_OUTPUT_PATH = BASE_DIR + "data/ffac-kommunen-statistics.json"

# The output path for the plotted map
# Set to None for interactive output
MAP_OUTPUT_PATH = BASE_DIR + "data/ffac-kommunen-nodes.png"

# Map boundaries and other parameters
MAP_BOUNDS_LAT = [50.48, 51.20]
MAP_BOUNDS_LON  = [5.85, 6.75]
MAP_TITLE = "Freifunk Region Aachen"

HBAR_OUTPUT_PATH = BASE_DIR + "data/ffac-kommunen-barchart.png"


# Read the city district boundaries from shape file
district_shapes = {}
online_district_stats = {}
known_district_stats = {}
with fiona.open(DISTRICT_SHAPEFILE, "r") as districts:
	for district in districts:
		district_name = district["properties"][DISTRICT_NAME_PROPERTY]
		district_shapes[district_name] = shape(district["geometry"])
		online_district_stats[district_name] = 0
		known_district_stats[district_name] = 0

# Download nodes.json
try:
	with urllib.request.urlopen(NODES_JSON_URI) as request:
		with open(NODES_JSON_PATH, "wb") as f:
			f.write(request.read())
except urllib.error.URLError as e:
	print("nodes.json download failed: ", e.reason)
	print("Using cached data (if available)...")

# Extract position of nodes from nodes.json
online_coords = {}
known_coords = {}
nogeo = 0
withgeo = 0
with open(NODES_JSON_PATH, "r") as f:
	nodes = json.load(f)["nodes"]
	for node in nodes:
		nodeinfo = node["nodeinfo"]
		if "location" in nodeinfo:
			location = nodeinfo["location"]
			if "latitude" in location and "longitude" in location:
				lat = location.get("latitude")
				lon = location.get("longitude")
				if node["flags"].get("online") == True:
					online_coords[nodeinfo["hostname"]] = Point(lon, lat)
				known_coords[nodeinfo["hostname"]] = Point(lon, lat)
				withgeo += 1
			else:
				nogeo += 1
		else:
			nogeo += 1


# Tally nodes within the individual district shapes
for node in online_coords.values():
	for district, shape in district_shapes.items():
		if shape.contains(node):
			online_district_stats[district] += 1

for node in known_coords.values():
	for district, shape in district_shapes.items():
		if shape.contains(node):
			known_district_stats[district] += 1


# Set up object to dump to json
data_dump = {}
data_dump["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
data_dump["counts"] = {}
data_dump["counts"]["with_geo"] = withgeo
data_dump["counts"]["without_geo"] = nogeo
data_dump["counts"]["online_within_boundary"] = sum(online_district_stats.values())
data_dump["counts"]["known_within_boundary"] = sum(known_district_stats.values())
data_dump["districts"] = {}
data_dump["districts"]["online"] = online_district_stats
data_dump["districts"]["known"] = known_district_stats


# Output statistics as json
json_dump = json.dumps(data_dump, sort_keys=True, indent=4, separators=(",", ":"), ensure_ascii=False)
if STATISTICS_OUTPUT_PATH is not None:
	try: 
		with open(STATISTICS_OUTPUT_PATH, "w") as f:
			f.write(json_dump)
			f.write("\n")
	except IOError:
		print("Could not write JSON to ", STATISTICS_OUTPUT_PATH)
else:
	print(json_dump)


# Prepare visualization plot

# Choose backend to make sure we can render to images even
# without an X server
if MAP_OUTPUT_PATH is not None:
	matplotlib.use('Agg')

# May only import them now, after backend was chosen...
from matplotlib import pyplot
from mapplot import plot_polygon, plot_coord_scatter, plot_hbar_chart

fig = pyplot.figure(dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim(MAP_BOUNDS_LAT)
ax.set_xlim(MAP_BOUNDS_LON)
ax.set_title(MAP_TITLE)


# Plot data
for polygon in district_shapes.values():
	plot_polygon(ax, polygon, color="#000000", alpha=1, linewidth=1)

plot_coord_scatter(ax, known_coords.values(), color="#ff0000", alpha=0.5)


# Output plot to either file or interactive/zoomable window
if MAP_OUTPUT_PATH is not None:
	pyplot.savefig(MAP_OUTPUT_PATH)
else:
	pyplot.show()

# Also plot a bar chart

fig = pyplot.figure(figsize=(12, 10.5), dpi=300)
ax = fig.add_subplot(111)
ax.set_title(MAP_TITLE)

plot_hbar_chart(fig, ax, online_district_stats)
fig.tight_layout()


# Output plot to either file or interactive/zoomable window
if HBAR_OUTPUT_PATH is not None:
	pyplot.savefig(HBAR_OUTPUT_PATH)
else:
	pyplot.show()

