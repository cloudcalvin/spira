import spira
import pyclipper
import numpy as np
from spira import param
from spira.gdsii.utils import *
from copy import copy, deepcopy
from spira.core.initializer import FieldInitializer
from numpy.linalg import norm


class __Shape__(FieldInitializer):

    center = param.PointField()
    gdslayer = param.LayerField()
    clockwise = param.BoolField(default=False)
    points = param.PointArrayField(fdef_name='create_points')
    apply_merge = param.DataField(fdef_name='create_merged_points')
    simplify = param.DataField(fdef_name='create_simplified_points')
    edges = param.DataField(fdef_name='create_edge_lines')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_points(self, points):
        return points

    def create_merged_points(self):
        """  """
        from spira.gdsii.utils import scale_polygon_up as spu
        from spira.gdsii.utils import scale_polygon_down as spd
        polygons = spu(self.points)
        self.points = []
        for poly in polygons:
            if pyclipper.Orientation(poly) is False:
                reverse_poly = pyclipper.ReversePath(poly)
                solution = pyclipper.SimplifyPolygon(reverse_poly)
            else:
                solution = pyclipper.SimplifyPolygon(poly)
            for sol in solution:
                self.points.append(sol)
        self.points = bool_operation(subj=self.points, method='union')
        self.points = spd(self.points)
        return self

    def create_simplified_points(self):
        """  """
        from shapely.geometry import Polygon as ShapelyPolygon
        value = 1
        polygons = self.points
        self.points = []
        for points in polygons:
            factor = (len(points)/100) * 1e5 * value
            sp = ShapelyPolygon(points).simplify(factor)
            pp = [[p[0], p[1]] for p in sp.exterior.coords]
            self.points.append(pp)
        return self

    def reflect(self, p1=(0,1), p2=(0,0)):
        """ Reflect across a line. """
        points = np.array(self.points[0])
        p1 = np.array(p1)
        p2 = np.array(p2)
        if np.asarray(points).ndim == 1:
            t = np.dot((p2-p1), (points-p1))/norm(p2-p1)**2
            pts = 2*(p1 + (p2-p1)*t) - points
        if np.asarray(points).ndim == 2:
            pts = np.array([0, 0])
            for p in points:
                t = np.dot((p2-p1), (p-p1))/norm(p2-p1)**2
                r = np.array(2*(p1 + (p2-p1)*t) - p)
                pts = np.vstack((pts, r))
        self.points = [pts]
        return self

    def rotate(self, angle=45, center=(0,0)):
        """ Rotate points with an angle around a center. """
        points = np.array(self.points[0])
        angle = angle*np.pi/180
        ca = np.cos(angle)
        sa = np.sin(angle)
        sa = np.array((-sa, sa))
        c0 = np.array(center)
        if np.asarray(points).ndim == 2:
            pts = (points - c0) * ca + (points - c0)[:,::-1] * sa + c0
            pts = np.round(pts, 6)
        if np.asarray(points).ndim == 1:
            pts = (points - c0) * ca + (points - c0)[::-1] * sa + c0
            pts = np.round(pts, 6)
        self.points = [pts]
        return self

    @property
    def orientation(self):
        """ Returns the orientation of the shape: 
        +1(counterclock) or -1(clock) """
        # FIXME: Error with multiple shapes: [[[s1], [s2]]]
        pts = self.points[0]
        T = np.roll(np.roll(pts, 1, 1), 1, 0)
        return -np.sign(sum(np.diff(pts * T, 1, 1)))

    @property
    def area(self):
        """ Returns the area of the shape. """
        pts = self.points[0]
        T = np.roll(np.roll(pts, 1, 1), 1, 0)
        return sum(abs(np.diff(pts * T, 1, 1))) * 0.5

    @property
    def count(self):
        """ number of points in the shape """
        return self.__len__()

    @property
    def reverse(self):
        pass

    def move(self, pos):
        p = np.array([pos[0], pos[1]])
        self.points += p
        return self

    def transform(self):
        pass

    def point_inside(self):
        pass

    def index(self, item):
        pass


class Shape(__Shape__):
    """ A shape is a geometrical object that 
    calculates the points that will be used 
    to generate a polygon object.
    
    Examples
    --------
    >>> shape = shapes.Shape(points=[])
    """

    def __init__(self, points=None, **kwargs):
        super().__init__(**kwargs)
        if points is not None:
            self.points = points

    # def __repr__(self):
    #     return 'Shape'

    # def __str__(self):
    #     return self.__repr__()

    def __deepcopy__(self, memo):
        shape = self.modified_copy(
            points = deepcopy(self.points),
            gdslayer = deepcopy(self.gdslayer)
        )
        return shape

    def __contains__(self, point):
        """ Checks if point is on the shape. """
        return np.prod(sum(self.points == np.array(point[0], point[1]), 0))

    def __eq__(self, other):
        if not isinstance(other, Shape):
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        pass









