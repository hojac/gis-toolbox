from matplotlib import pyplot as plt

def plot_polygon(ax, polygon, color, alpha=1, linewidth=1):
	"""Plots a shapely.Polygon object"""
	x,y = polygon.exterior.xy
	ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth, solid_capstyle="round")

def plot_coord_scatter(ax, coords, color, alpha=0.5):
	"""Plots a list of shapely.Point as scatter plot"""
	x,y = zip(*[coord.xy for coord in coords])
	ax.scatter(x,y, color=color, alpha=alpha)

