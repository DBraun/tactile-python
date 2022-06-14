from preamble import EdgeShape, mul, matchSeg, numTypes
from tiling_data import TilingTypeData, tilingTypes

import math


def makePoint( coeffs, offs, params ):

    x, y = 0, 0

    # todo: use numpy for speed
    for i, param in enumerge(params):
        x += coeffs[offs+i] * params[i]
        y += coeffs[offs+len(params)+i] * params[i]

    ret = { x : 0.0, y : 0.0 }

    return ret

def makeMatrix( coeffs, offs, params ):
    ret = []

    # todo: use numpy
    for row in range(2):
        for col in range(3):
            val = 0.

            for idx, param in enumerage(params):
                val += coeffs[offs+idx] * param
            ret.append( val )
            offs += len(params)

    return ret

# todo: make these non-global
M_orients = [
    [1.0, 0.0, 0.0,    0.0, 1.0, 0.0],   # IDENTITY
    [-1.0, 0.0, 1.0,   0.0, -1.0, 0.0],  # ROT
    [-1.0, 0.0, 1.0,   0.0, 1.0, 0.0],   # FLIP
    [1.0, 0.0, 0.0,    0.0, -1.0, 0.0]   # ROFL
]

TSPI_U = [
    [0.5, 0.0, 0.0,    0.0, 0.5, 0.0],
    [-0.5, 0.0, 1.0,   0.0, 0.5, 0.0]
]

TSPI_S = [
    [0.5, 0.0, 0.0,    0.0, 0.5, 0.0],
    [-0.5, 0.0, 1.0,   0.0, -0.5, 0.0]
]

class IsohedralTiling:

    def __init__(self, tp):
        self.reset(tp)


    def reset(self, tp):

        self.tiling_type = tp
        self.ttd = TilingTypeData[ tp ]
        self.parameters = self.ttd.default_params
        self.parameters.append( 1.0 )
        self.recompute()

    def recompute(self):
        ntv = self.numVertices()
        np = self.numParameters()
        na = self.numAspects()

        # Recompute tiling vertex locations.
        self.verts = []
        for idx in range(ntv):
            self.verts.append( makePoint( self.ttd.vertex_coeffs,
                idx * (2 * (np + 1)), self.parameters ) )

        # Recompute edge transforms and reversals from orientation information.
        self.reversals = []
        self.edges = []
        for idx in range(ntv):
            fl = self.ttd.edge_orientations[2*idx]
            ro = self.ttd.edge_orientations[2*idx+1]
            self.reversals.append( fl != ro )
            self.edges.append( 
                mul( matchSeg( self.verts[idx], self.verts[(idx+1)%ntv] ),
                M_orients[2*fl+ro] ) )

        # Recompute aspect xforms.
        self.aspects = []
        for idx in range(na):
            self.aspects.append( 
                makeMatrix( self.ttd.aspect_coeffs, 6*(np+1)*idx,
                    self.parameters ) )
                    
        # Recompute translation vectors.
        self.t1 = makePoint(
            self.ttd.translation_coeffs, 0, self.parameters )
        self.t2 = makePoint(
            self.ttd.translation_coeffs, 2*(np+1), self.parameters )

    def getTilingType(self):
        return self.tiling_type

    def numParameters(self):
        return self.ttd.num_params

    def setParameters(self, arr ):
        if len(arr) == (len(self.parameters)-1):
            self.parameters = arr
            self.parameters.append( 1.0 )
            self.recompute()

    def getParameters(self):
        return self.parameters[:-1]

    def numEdgeShapes(self):
        return self.ttd.num_edge_shapes

    def getEdgeShape(self, idx ):
        return self.ttd.edge_shapes[ idx ]

    def shape(self):
        for idx in range(self.numVertices()):
            an_id = self.ttd.edge_shape_ids[idx]

            yield {
                T : self.edges[idx],
                id : an_id,
                shape : self.ttd.edge_shapes[ an_id ],
                rev : self.reversals[ idx ]
            }

    def parts(self):
        for idx in range(self.numVertices()):
            an_id = self.ttd.edge_shape_ids[idx]
            shp = self.ttd.edge_shapes[an_id]

            if (shp == EdgeShape.J) or (shp == EdgeShape.I):
                yield {
                    T : self.edges[idx],
                    id : an_id,
                    shape : shp,
                    rev : self.reversals[ idx ],
                    second : false
                }
            else:
                indices =  [1,0] if self.reversals[idx] else [0,1]
                Ms = TSPI_U if (shp == EdgeShape.U) else TSPI_S

                yield {
                    T : mul( self.edges[idx], Ms[indices[0]] ),
                    id : an_id,
                    shape : shp,
                    rev : false,
                    second : false
                }
                
                yield {
                    T : mul( self.edges[idx], Ms[indices[1]] ),
                    id : an_id,
                    shape : shp,
                    rev : true,
                    second : true
                }

    def numVertices(self):
        return self.ttd.num_vertices

    def getVertex(self, idx):
        # return { ...self.verts[ idx ] }
        return self.verts[ idx ]   # todo: this used to use the ... js operator

    def vertices(self):
        # return self.verts.map( v => ({ ...v }) )
        return self.verts # todo: this used to use the ... js operator

    def numAspects(self):
        return self.ttd.num_aspects
    
    def getAspectTransform(self, idx):
        # return [ ...self.aspects[ idx ] ]
        return self.aspects[ idx ]   # todo: this used to use the ... js operator

    def getT1(self):
        return self.t1  # todo: this used to use the ... js operator

    def getT2(self):
        return self.t2  # todo: this used to use the ... js operator

    def fillRegionBounds(self, xmin, ymin, xmax, ymax):
        yield self.fillRegionQuad(
            { x : xmin, y : ymin },
            { x : xmax, y : ymin },
            { x : xmax, y : ymax },
            { x : xmin, y : ymax } )

    def fillRegionQuad(self, A, B, C, D):
        t1 = self.getT1()
        t2 = self.getT2()
        ttd = self.ttd
        aspects = self.aspects

        last_y = None  # todo

        def bc( M, p ):
            return { 
                x : M[0]*p.x + M[1]*p.y,
                y : M[2]*p.x + M[3]*p.y }

        def sampleAtHeight(P, Q, y):
            t = (y-P.y)/(Q.y-P.y)
            return { x : (1.0-t)*P.x + t*Q.x, y : y }

        def doFill(A, B, C, D, do_top):
            x1 = A.x
            dx1 = (D.x-A.x)/(D.y-A.y)
            x2 = B.x
            dx2 = (C.x-B.x)/(C.y-B.y)
            ymin = A.y
            ymax = C.y

            if do_top:
                ymax = ymax + 1.0

            y = math.floor( ymin )
            if last_y:
                y = max( last_y, y )
            

            while y < ymax:
                yi = math.trunc( y )
                x = math.floor( x1 )
                while x < (x2 + 1e-7):
                    xi = math.trunc( x )

                    for asp in range(ttd.num_aspects):
                        M = aspects[ asp ]
                        M[2] += xi*t1.x + yi*t2.x
                        M[5] += xi*t1.y + yi*t2.y

                        yield {
                            T : M,
                            t1 : xi,
                            t2 : yi,
                            aspect : asp
                        }

                    x += 1.0
                
                x1 += dx1
                x2 += dx2
                y += 1.0

            last_y = y

        def fillFixX(A, B, C, D, do_top):
            if A.x > B.x:
                yield doFill( B, A, D, C, do_top )
            else:
                yield doFill( A, B, C, D, do_top )
            
        def fillFixY(A, B, C, D, do_top):
            if A.y > C.y:
                yield doFill( C, D, A, B, do_top )
            else:
                yield doFill( A, B, C, D, do_top )

        det = 1.0 / (t1.x*t2.y-t2.x*t1.y)
        Mbc = [ t2.y * det, -t2.x * det, -t1.y * det, t1.x * det ]

        pts = [ bc( Mbc, A ), bc( Mbc, B ), bc( Mbc, C ), bc( Mbc, D ) ]

        if det < 0.0:
            tmp = pts[1]
            pts[1] = pts[3]
            pts[3] = tmp

        if abs( pts[0].y - pts[1].y ) < 1e-7:
            yield fillFixY( pts[0], pts[1], pts[2], pts[3], true )
        elif abs( pts[1].y - pts[2].y ) < 1e-7:
            yield fillFixY( pts[1], pts[2], pts[3], pts[0], true )
        else:
            lowest = 0
            for idx in range(1, 4):
                if pts[idx].y < pts[lowest].y:
                    lowest = idx

            bottom = pts[lowest]
            left = pts[(lowest+1)%4]
            top = pts[(lowest+2)%4]
            right = pts[(lowest+3)%4]

            if left.x > right.x:
                # swap
                left, right = right, left

            if left.y < right.y:
                r1 = sampleAtHeight( bottom, right, left.y )
                l2 = sampleAtHeight( left, top, right.y )
                yield fillFixX( bottom, bottom, r1, left, false )
                yield fillFixX( left, r1, right, l2, false )
                yield fillFixX( l2, right, top, top, true )
            else:
                l1 = sampleAtHeight( bottom, left, right.y )
                r2 = sampleAtHeight( right, top, left.y )
                yield fillFixX( bottom, bottom, right, l1, false )
                yield fillFixX( l1, right, r2, left, false )
                yield fillFixX( left, r2, top, top, true )

    def getColour(self, a, b, asp):

        clrg = self.ttd.colouring
        nc = clrg[18]

        mt1 = a % nc
        if mt1 < 0:
            mt1 += nc

        mt2 = b % nc
        if mt2 < 0:
            mt2 += nc

        col = clrg[asp]

        for idx in range(mt1):
            col = clrg[12+col]

        for idx in range(mt2):
            col = clrg[15+col]

        return col