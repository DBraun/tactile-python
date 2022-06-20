import random
import math

import p5

from tactile import EdgeShape, mul, Point
from random_tiles import make_random_tiling


def draw_random_tiling():
        
    tiling, edges = make_random_tiling()

    # Make some random colors.
    cols = []
    for i in range(3):
        cols.append([
            int(math.floor(random.random() * 255)),
            int(math.floor(random.random() * 255)),
            int(math.floor(random.random() * 255))])

    # Define a world-to-screen transformation matrix that scales by 100x.
    scale = 100
    tx = 0
    ty = 0
    ST = [ scale, 0.0, tx, 0.0, scale, ty ]

    for i in tiling.fill_region_bounds( -2, -2, 12, 12 ):
        T = mul( ST, i.T )
        p5.fill(*cols[ tiling.get_color( i.t1, i.t2, i.aspect ) ])

        start = True
        p5.begin_shape()

        for si in tiling.shapes:
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
    # p5.no_loop()


def draw():
    # p5.stroke_weight(1)
    # p5.stroke(0,0,0)
    p5.no_stroke()
    p5.background(0)
    draw_random_tiling()
    # p5.save_frame()


if __name__ == '__main__':

    p5.run()
