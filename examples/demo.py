import random
import math

import p5

from tactile import IsohedralTiling, tiling_types, EdgeShape, mul, Point


def makeRandomTiling():
    # Construct a tiling
    tp = tiling_types[ int(math.floor( 81 * random.random() )) ]
    tiling = IsohedralTiling( tp )

    # Randomize the tiling vertex parameters
    ps = tiling.getParameters()
    for i in range(len(ps)):
        ps[i] += (random.random()-.5)*0.2
    tiling.setParameters( ps )

    # Make some random edge shapes.  Note that here, we sidestep the 
    # potential complexity of using .shape() vs. .parts() by checking
    # ahead of time what the intrinsic edge shape is and building
    # Bezier control points that have all necessary symmetries.
    # See https://github.com/isohedral/tactile-js/ for more info.

    edges = []
    for i in range(tiling.numEdgeShapes()):
        ej = []
        shp = tiling.getEdgeShape( i )
        if shp == EdgeShape.I:
            # Must be a straight line.
            pass
        elif shp == EdgeShape.J:
            # Anything works for J
            ej.append( Point(random.random()*0.6, random.random() - 0.5))
            ej.append( Point(random.random()*0.6 + 0.4, random.random() - 0.5))
        elif shp == EdgeShape.S:
            # 180-degree rotational symmetry
            ej.append( Point(random.random()*0.6, random.random() - 0.5))
            ej.append( Point(1.0 - ej[0].x, -ej[0].y))
        elif shp == EdgeShape.U:
            # Symmetry after reflecting/flipping across length.
            ej.append( Point(random.random()*0.6, random.random() - 0.5))
            ej.append( Point(1.0 - ej[0].x, ej[0].y))

        edges.append( ej )

    return tiling, edges


def drawRandomTiling():
        
    tiling, edges = makeRandomTiling()

    # Make some random colors.
    cols = []
    for i in range(3):
        cols.append([
            int(math.floor( random.random() * 255 )),
            int(math.floor( random.random() * 255 )),
            int(math.floor( random.random() * 255 ))])

    # Define a world-to-screen transformation matrix that scales by 100x.
    scale = 100
    tx = 0
    ty = 0
    ST = [ scale, 0.0, tx, 0.0, scale, ty ]

    for i in tiling.fillRegionBounds( -2, -2, 12, 12 ):
        T = mul( ST, i.T )
        p5.fill(*cols[ tiling.getColor( i.t1, i.t2, i.aspect ) ])

        start = True
        p5.begin_shape()

        for si in tiling.shape():
            S = mul( T, si.T )
            # Make the edge start at (0,0)
            seg = [ mul( S, Point(0., 0.)) ]

            if si.shape != EdgeShape.I:
                # The edge isn't just a straight line.
                ej = edges[ si.id ]
                seg.append( mul( S, ej[0] ) )
                seg.append( mul( S, ej[1] ) )

            # Make the edge end at (1,0)
            seg.append( mul( S, Point(1., 0.)) )

            if si.rev:
                seg.reverse()

            if start:
                start = False
                p5.vertex(seg[0].x, seg[0].y )
            if len(seg) == 2:
                p5.vertex(seg[1].x, seg[1].y )
            else:
                p5.bezier_vertex(
                    seg[1].x, seg[1].y, 
                    seg[2].x, seg[2].y, 
                    seg[3].x, seg[3].y)

        p5.end_shape()


def setup():
    p5.size(1000, 1000)
    # no_loop()


def draw():
    # stroke_weight(1)
    # stroke(0,0,0)
    p5.no_stroke()
    p5.background(0)
    drawRandomTiling()


if __name__ == '__main__':

    p5.run()
