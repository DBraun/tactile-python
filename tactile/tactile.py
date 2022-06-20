from .preamble import EdgeShape, mul, matchSeg, Shape, Point
from .tiling_data import TilingTypeData, Tiling, tiling_types

import math
import copy
from typing import List


def make_point(coeffs, offs, params):

    # This is a bit messy because the tactile-js source code
    # pretends to have an extra 1.0 value tacked onto the end of the params.
    # We don't do that in this library, however. So instead, we have to 
    # account for it in this `make_point` function.
    len_params = len(params)
    len_params_plus_one = len_params+1

    x = coeffs[offs + len_params]
    y = coeffs[offs + len_params_plus_one+len_params]

    for i, param in enumerate(params):
        x += coeffs[offs + i] * param
        y += coeffs[offs + len_params_plus_one + i] * param

    point = Point(x, y)

    return point


def make_matrix(coeffs, offs, params):
    ret = []

    # This is a bit messy because the tactile-js source code
    # pretends to have an extra 1.0 value tacked onto the end of the params.
    # We don't do that in this library, however. So instead, we have to 
    # account for it in this `make_point` function.
    len_params = len(params)
    len_params_plus_one = len_params+1

    for row in range(2):
        for col in range(3):
            
            val = coeffs[offs + len_params]

            for idx, param in enumerate(params):
                val += coeffs[offs + idx] * param
            ret.append(val)
            offs += len_params_plus_one

    return ret


M_orients = [
    [1.0,  0.0, 0.0, 0.0,  1.0, 0.0],  # IDENTITY
    [-1.0, 0.0, 1.0, 0.0, -1.0, 0.0],  # ROT
    [-1.0, 0.0, 1.0, 0.0,  1.0, 0.0],  # FLIP
    [1.0,  0.0, 0.0, 0.0, -1.0, 0.0],  # ROFL
]

TSPI_U = [[0.5, 0.0, 0.0, 0.0, 0.5, 0.0], [-0.5, 0.0, 1.0, 0.0, 0.5, 0.0]]

TSPI_S = [[0.5, 0.0, 0.0, 0.0, 0.5, 0.0], [-0.5, 0.0, 1.0, 0.0, -0.5, 0.0]]


class IsohedralTiling:

    def __init__(self, tp: Tiling):
        self.reset(tp)

    def reset(self, tp: Tiling):
        self._tiling_type = tp
        self.ttd = TilingTypeData.get_data(tp)
        self._parameters = copy.deepcopy(self.ttd.default_params)
        self._recompute()

    def _recompute(self):
        ntv = self.num_vertices
        np = self.num_parameters
        na = self.num_aspects

        # Recompute tiling vertex locations.
        self.verts = []
        for idx in range(ntv):
            self.verts.append(
                make_point(self.ttd.vertex_coeffs, idx * (2 * (np + 1)), self._parameters)
            )

        # Recompute edge transforms and reversals from orientation information.
        self.reversals = []
        self.edges = []
        for idx in range(ntv):
            fl = self.ttd.edge_orientations[2 * idx]
            ro = self.ttd.edge_orientations[2 * idx + 1]
            self.reversals.append(fl != ro)
            self.edges.append(
                mul(
                    matchSeg(self.verts[idx], self.verts[(idx + 1) % ntv]),
                    M_orients[2 * fl + ro],
                )
            )

        # Recompute aspect xforms.
        self._aspects = []
        for idx in range(na):
            self._aspects.append(
                make_matrix(self.ttd.aspect_coeffs, 6 * (np + 1) * idx, self._parameters)
            )

        # Recompute translation vectors.
        self._t1 = make_point(self.ttd.translation_coeffs, 0, self._parameters)
        self._t2 = make_point(self.ttd.translation_coeffs, 2 * (np + 1), self._parameters)

    @property
    def tiling_type(self):
        return self._tiling_type

    @property
    def num_parameters(self):
        return self.ttd.num_params

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, arr: List[float]):

        if not isinstance(arr, list):
            arg_type = type(arr)
            raise ValueError(f'The passed parameters must be a pure Python list, but an arg of type "{arg_type}" was passed.')  

        expected_length = self.num_parameters
        passed_length = len(arr)
        if passed_length != expected_length:
            raise ValueError(f"The length of the passed parameters was {passed_length}, but {expected_length} was expected.")  

        self._parameters = copy.deepcopy(arr)
        self._recompute()

    @property
    def num_edge_shapes(self):
        return self.ttd.num_edge_shapes

    @property
    def edge_shapes(self):
        return self.ttd.edge_shapes

    @property
    def shapes(self):
        for idx in range(self.num_vertices):
            an_id = self.ttd.edge_shape_ids[idx]

            yield Shape(
                **{
                    "T": self.edges[idx],
                    "id": an_id,
                    "shape": self.ttd.edge_shapes[an_id],
                    "rev": self.reversals[idx],
                }
            )

    @property
    def parts(self):
        for idx in range(self.num_vertices):
            an_id = self.ttd.edge_shape_ids[idx]
            shp = self.ttd.edge_shapes[an_id]

            if (shp == EdgeShape.J) or (shp == EdgeShape.I):
                yield Shape(
                    **{
                        "T": self.edges[idx],
                        "id": an_id,
                        "shape": shp,
                        "rev": self.reversals[idx],
                        "second": False,
                    }
                )
            else:
                indices = [1, 0] if self.reversals[idx] else [0, 1]
                Ms = TSPI_U if (shp == EdgeShape.U) else TSPI_S

                yield Shape(
                    **{
                        "T": mul(self.edges[idx], Ms[indices[0]]),
                        "id": an_id,
                        "shape": shp,
                        "rev": False,
                        "second": False,
                    }
                )

                yield Shape(
                    **{
                        "T": mul(self.edges[idx], Ms[indices[1]]),
                        "id": an_id,
                        "shape": shp,
                        "rev": True,
                        "second": True,
                    }
                )

    @property
    def num_vertices(self):
        return self.ttd.num_vertices

    @property
    def vertices(self):
        return self.verts

    @property
    def num_aspects(self):
        return self.ttd.num_aspects

    @property
    def aspects(self):
        # aspect transforms
        return self._aspects

    @property
    def t1(self):
        return self._t1

    @property
    def t2(self):
        return self._t2

    def fill_region_bounds(self, xmin: float, ymin: float, xmax: float, ymax: float):
        yield from self._fill_region_quad(
            Point(xmin, ymin),
            Point(xmax, ymin),
            Point(xmax, ymax),
            Point(xmin, ymax)
        )

    def _fill_region_quad(self, A: Point, B: Point, C: Point, D: Point):
        t1 = self.t1
        t2 = self.t2
        ttd = self.ttd
        aspects = self._aspects

        self._last_y = None

        def bc(M, p):
            return Point(M[0] * p.x + M[1] * p.y, M[2] * p.x + M[3] * p.y)

        def sample_at_height(P, Q, y):
            t = (y - P.y) / (Q.y - P.y)
            return Point((1.0 - t) * P.x + t * Q.x, y)

        def do_fill(A, B, C, D, do_top):

            x1 = A.x
            dx1 = (D.x - A.x) / (D.y - A.y)
            x2 = B.x
            dx2 = (C.x - B.x) / (C.y - B.y)
            ymin = A.y
            ymax = C.y

            if do_top:
                ymax = ymax + 1.0

            y = math.floor(ymin)
            if self._last_y:
                y = max(self._last_y, y)

            while y < ymax:
                yi = math.trunc(y)
                x = math.floor(x1)
                while x < (x2 + 1e-7):
                    xi = math.trunc(x)

                    for asp in range(ttd.num_aspects):
                        M = copy.deepcopy(aspects[asp])
                        M[2] += xi * t1.x + yi * t2.x
                        M[5] += xi * t1.y + yi * t2.y

                        yield Shape(
                            **{
                                "T": M,
                                "id": False,
                                "shape": False,
                                "rev": False,
                                "second": False,
                                "t1": xi,
                                "t2": yi,
                                "aspect": asp,
                            }
                        )

                    x += 1.0

                x1 += dx1
                x2 += dx2
                y += 1.0

            self._last_y = y

        def fill_fix_x(A, B, C, D, do_top):
            if A.x > B.x:
                yield from do_fill(B, A, D, C, do_top)
            else:
                yield from do_fill(A, B, C, D, do_top)

        def fill_fix_y(A, B, C, D, do_top):
            if A.y > C.y:
                yield from do_fill(C, D, A, B, do_top)
            else:
                yield from do_fill(A, B, C, D, do_top)

        det = 1.0 / (t1.x * t2.y - t2.x * t1.y)
        Mbc = [t2.y * det, -t2.x * det, -t1.y * det, t1.x * det]

        pts = [bc(Mbc, A), bc(Mbc, B), bc(Mbc, C), bc(Mbc, D)]

        if det < 0.0:
            tmp = pts[1]
            pts[1] = pts[3]
            pts[3] = tmp

        if abs(pts[0].y - pts[1].y) < 1e-7:
            yield from fill_fix_y(pts[0], pts[1], pts[2], pts[3], True)
        elif abs(pts[1].y - pts[2].y) < 1e-7:
            yield from fill_fix_y(pts[1], pts[2], pts[3], pts[0], True)
        else:
            lowest = 0
            for idx in range(1, 4):
                if pts[idx].y < pts[lowest].y:
                    lowest = idx

            bottom = pts[lowest]
            left = pts[(lowest + 1) % 4]
            top = pts[(lowest + 2) % 4]
            right = pts[(lowest + 3) % 4]

            if left.x > right.x:
                # swap
                left, right = right, left

            if left.y < right.y:
                r1 = sample_at_height(bottom, right, left.y)
                l2 = sample_at_height(left, top, right.y)
                yield from fill_fix_x(bottom, bottom, r1, left, False)
                yield from fill_fix_x(left, r1, right, l2, False)
                yield from fill_fix_x(l2, right, top, top, True)
            else:
                l1 = sample_at_height(bottom, left, right.y)
                r2 = sample_at_height(right, top, left.y)
                yield from fill_fix_x(bottom, bottom, right, l1, False)
                yield from fill_fix_x(l1, right, r2, left, False)
                yield from fill_fix_x(left, r2, top, top, True)

    def get_color(self, a, b, asp):

        clrg = self.ttd.coloring
        nc = clrg[18]

        mt1 = a % nc
        if mt1 < 0:
            mt1 += nc

        mt2 = b % nc
        if mt2 < 0:
            mt2 += nc

        col = clrg[asp]

        for idx in range(mt1):
            col = clrg[12 + col]

        for idx in range(mt2):
            col = clrg[15 + col]

        return col
