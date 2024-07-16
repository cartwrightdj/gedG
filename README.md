**Extracts individuals and families from GEDCOM file and creates a graph**  
*Graph is directional from parent to child, marriages have two edges to and from spouses*

usage: main.py [-h] filename

Process a .ged file.

positional arguments:
  filename    The path to the .ged file

options:
  -h, --help  show this help message and exit

G is saved to same folder script is run from as 'graph.gml'

Sample Graph
![Sample Image](https://github.com/cartwrightdj/gedG/blob/master/graph.png)

TODO: add ability to graph references, images, sources etc. from GEDCOM
