import random
import math

import numpy as np

from p5 import *

import tactile
from tactile import EdgeShape, mul, Point, Shape

def makeRandomTiling():
    # Construct a tiling
    tp = tactile.tilingTypes[ int(math.floor( 81 * random.random() )) ]
    tiling = tactile.IsohedralTiling( tp )

    # Randomize the tiling vertex parameters
    ps = tiling.getParameters()
    for i in range(len(ps)):
        ps[i] += random.random() * 0.1 - 0.05
    tiling.setParameters( ps )

    # Make some random edge shapes.  Note that here, we sidestep the 
    # potential complexity of using .shape() vs. .parts() by checking
    # ahead of time what the intrinsic edge shape is and building
    # Bezier control points that have all necessary symmetries.

    edges = []
    for i in range(tiling.numEdgeShapes()):
        ej = []
        shp = tiling.getEdgeShape( i )
        if shp == EdgeShape.I:
            pass
        elif shp == EdgeShape.J:
            ej.append( Point(**{ "x": random.random()*0.6, "y" : random.random() - 0.5 }))
            ej.append( Point(**{ "x": random.random()*0.6 + 0.4, "y" : random.random() - 0.5 }))
        elif shp == EdgeShape.S:
            ej.append( Point(**{ "x": random.random()*0.6, "y" : random.random() - 0.5 }))
            ej.append( Point(**{ "x": 1.0 - ej[0].x, "y": -ej[0].y }))
        elif shp == EdgeShape.U:
            ej.append( Point(**{ "x": random.random()*0.6, "y" : random.random() - 0.5 }))
            ej.append( Point(**{ "x": 1.0 - ej[0].x, "y": ej[0].y }))

        edges.append( ej )

    return tiling, edges


def drawRandomTiling():
        
    # var canvas = document.getElementById( 'canvas' )
    # var ctx = canvas.getContext( '2d' )

    tiling, edges = makeRandomTiling()

    # Make some random colours.
    cols = []
    for i in range(3):
        cols.append([
            int(math.floor( random.random() * 255.0 )),
            int(math.floor( random.random() * 255.0 )),
            int(math.floor( random.random() * 255.0 ))])

    # ctx.lineWidth = 1.0
    # ctx.strokeStyle = '#000'

    # Define a world-to-screen transformation matrix that scales by 50x.
    scale = 1
    ST = [ scale, 0.0, 0.0, 
                 0.0, scale, 0.0 ]

    for i in tiling.fillRegionBounds( -2, -2, 12, 12 ):
        T = mul( ST, i.T )
        fill(0,255,0)
        # fill(*cols[ tiling.getColour( i.t1, i.t2, i.aspect ) ])

        start = True
        begin_shape()

        for si in tiling.shape():
            S = mul( T, si.T )
            seg = [ mul( S, Point(**{ "x": 0.0, "y": 0.0 } )) ]

            if si.shape != EdgeShape.I:
                ej = edges[ si.id ]
                seg.append( mul( S, ej[0] ) )
                seg.append( mul( S, ej[1] ) )

            seg.append( mul( S, Point(**{ "x": 1.0, "y": 0.0 } )) )

            if si.rev:
                seg.reverse()
            print(seg)

            if start:
                start = False
                vertex(seg[0].x, seg[0].y )
                # ctx.moveTo( seg[0].x, seg[0].y )

            if len(seg) == 2:
                # ctx.lineTo( seg[1].x, seg[1].y )
                vertex(seg[1].x, seg[1].y )
            else:
                bezier_vertex(
                    seg[1].x, seg[1].y, 
                    seg[2].x, seg[2].y, 
                    seg[3].x, seg[3].y)
                # ctx.bezierCurveTo( 
                #   seg[1].x, seg[1].y, 
                #   seg[2].x, seg[2].y, 
                #   seg[3].x, seg[3].y )

        end_shape()
        # fill()
        # ctx.stroke()


# tiling = tactile.IsohedralTiling( tactile.tilingTypes[ 0 ] )
# drawRandomTiling()

def setup():
    size(1000, 1000)
    no_loop()


def draw():
    # print('draw')
    # no_stroke()
    stroke_weight(5)
    stroke(255,0,0)
    # background(204)
    drawRandomTiling()

    # begin_shape()
    # vertex(200, 200)
    # vertex(200, 500 )
    # vertex(500, 200 )
    # end_shape()

if __name__ == '__main__':

    run()
