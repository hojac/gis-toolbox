#!/usr/bin/env python3

import fiona
from shapely.geometry import shape, Point
import json
import urllib.request, urllib.error
from matplotlib import pyplot

from mapplot import plot_polygon, plot_coord_scatter



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

# The output path of the statistics (json format)
# Use None to print to stdout
STATISTICS_OUTPUT_PATH = "data/ffac-district-statistics.json"

# The output path for the plotted map
# Set to None for interactive output
MAP_OUTPUT_PATH = "data/ffac-nodes.png"

# Map boundaries and other parameters
MAP_BOUNDS_LONG = [50.65, 50.90]
MAP_BOUNDS_LAT  = [5.95, 6.25]
MAP_TITLE = "Freifunk Aachen"


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
	with urllib.request.urlopen(NODES_JSON_URI) as request:
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


# Tally nodes within the individual district shapes
for _,node in coords.items():
	for district, shape in district_shapes.items():
		if shape.contains(node):
			district_stats[district] += 1


# Set up object to dump to json
data_dump = {}
data_dump["counts"] = {}
data_dump["counts"]["with_geo"] = withgeo
data_dump["counts"]["without_geo"] = nogeo
data_dump["counts"]["within_boundary"] = sum([x for _,x in district_stats.items()])
data_dump["districts"] = district_stats


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
fig = pyplot.figure(1, dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim(MAP_BOUNDS_LONG)
ax.set_xlim(MAP_BOUNDS_LAT)
ax.set_title(MAP_TITLE)


# Plot data
for _,polygon in district_shapes.items():
	plot_polygon(ax, polygon, color="#000000", alpha=1, linewidth=1)

plot_coord_scatter(ax, [node for _,node in coords.items()], color="#ff0000", alpha=0.5)


# Output plot to either file or interactive/zoomable window
if MAP_OUTPUT_PATH is not None:
	pyplot.savefig(MAP_OUTPUT_PATH)
else:
	pyplot.show()

