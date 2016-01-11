This repository contains miscellaneous tools for spatial analysis.

district-node-stats.py
----------------------

Evaluates how the nodes are distributed over districts given by
an ESRI shape file.

Requires [Fiona][Fiona] and [Shapely][Shapely].

[Fiona]: https://pypi.python.org/pypi/Fiona
[Shapely]: https://pypi.python.org/pypi/Shapely/

Some Debian-based distributions may not yet include the python3-fiona
package. In that case install with pip3:

``` sh
$ sudo apt-get install build-essential libgdal1-dev
$ sudo pip3 install fiona
```

The script may be configured inline. For example, the paths to the
nodes.json (ffmap format) and path of the ESRI shape files of
the districts (in WGS84 projection, EPSG:4327) may be given. Note that each
of the district polygons must contain a `property` with the name of
the district.

If these input constraint are satisfied, this script should be pretty
plug'n'play-y to use with no additional coding adaptations required.

By default settings, the script will analyze the distributions of nodes
over the statistical districts of the city of Aachen.

