import re
import math
import numpy as np
from db_wrapper import get_node_id

# Euclidean distance between two points
def euclidean_dist(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def linestring_to_point_array(linestring):
    # Linestring is in format: 'LINESTRING(lon1 lat1, lon2 lat2, ... , )'
    # First slice all unnecessary things off the string
    linestring = linestring[11:-1]
    # split the string into points
    points = linestring.split(',')
    # split to a tuple of long and lat
    points = [tuple(map(float, p.split())) for p in points]
    points = tuple(points)  # Order is important, so make it tuple
    return points
    
# Distance of point to linesegment
# u == vector from endpoints[0] to endpoints[1]
# v == vector from endpoints[0] to point
def point_to_lineseg_dist(endpoints, point):
    endpoints = np.array(endpoints)
    p = np.array(point)
    u = endpoints[1] - endpoints[0]
    v = p - endpoints[0]
    # Magnitude of projection of v to u in terms of the magnitude of u
    projection = np.dot(u,v) / np.dot(u,u)
    # If magnitude of projection is less than 0, it means that
    # the projection of point to line lies outside the linesegment
    # and the distance of point to linesegment is the distance from
    # point to endpoints[0]
    if projection < 0:
        return euclidean_dist(endpoints[0], point)
    # Same as above
    elif projection > 1:
        return euclidean_dist(endpoints[1], point)
    # If projection in [0,1], distance from point to line is the
    # distance from point to its orthogonal projection on the line
    projection_vec = endpoints[0] + projection*u
    return euclidean_dist(projection_vec, point)

def get_node_ids(matches):
    node_ids = []
    for i, match in enumerate(matches):
        if match[0] is None:
            node_ids.append(None)
            continue
        # Don't query the same point twice
        if i == 0 or match[0] != matches[i-1][0] or match[1] != matches[i-1][1]:
            start_node = get_node_id(match[0], match[1])
            start_node = re.findall(r'\d+', str(start_node))[0]
            end_node = get_node_id(match[0], match[1] + 1)
            end_node = re.findall(r'\d+', str(end_node))[0]
        node_ids.append((start_node, end_node))
    return node_ids
 
def write_to_file(node_ids, filename):
    with open(filename, 'w') as f:
        f.write('Segment start id, Segment end id\n')
        for node in node_ids:
            if node is None:
                f.write('NA\n')
            else:
                f.write(node[0] + ', ' + node[1] + '\n')
