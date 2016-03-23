from matplotlib import pyplot as plt
from numpy import arange
import operator

def plot_polygon(ax, polygon, color, alpha=1, linewidth=1):
	"""Plots a shapely.Polygon object"""
	x,y = polygon.exterior.xy
	ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth, solid_capstyle="round")

def plot_coord_scatter(ax, coords, color, alpha=0.5):
	"""Plots a list of shapely.Point as scatter plot"""
	x,y = zip(*[coord.xy for coord in coords])
	ax.scatter(x,y, color=color, alpha=alpha)

def plot_hbar_chart(fig, ax, stats):
	"""Plots a horizontal bar graph to visualize the json"""
	y,x = zip(*sorted(stats.items(), key = operator.itemgetter(1)))

	pos = arange(len(stats))
	ax.barh(pos, x)
	ax.set_yticks(pos + 0.5)
	ax.set_yticklabels(list(y))
