#!/usr/bin/python
# -*- coding: utf-8 -*-
from enum import Enum
from collections import namedtuple


class EdgeShape(Enum):

    J = 10001
    U = 10002
    S = 10003
    I = 10004

Point = namedtuple('Point', ['x', 'y'])

Shape = namedtuple('Shape', [
    'T',
    'id',
    'shape',
    'rev',
    'second',
    't1',
    't2',
    'aspect',
    ], defaults=[
    None,
    None,
    None,
    None,
    False,
    None,
    None,
    None,
    ])


def mul(A, B):
    if hasattr(B, 'x'):

        # Matrix * Point

        x = A[0] * B.x + A[1] * B.y + A[2]
        y = A[3] * B.x + A[4] * B.y + A[5]

        return Point(x, y)
    else:

        # Matrix * Matrix

        return [
            A[0] * B[0] + A[1] * B[3],
            A[0] * B[1] + A[1] * B[4],
            A[0] * B[2] + A[1] * B[5] + A[2],
            A[3] * B[0] + A[4] * B[3],
            A[3] * B[1] + A[4] * B[4],
            A[3] * B[2] + A[4] * B[5] + A[5],
            ]


def matchSeg(p, q):
    return [
        q.x - p.x,
        p.y - q.y,
        p.x,
        q.y - p.y,
        q.x - p.x,
        p.y,
        ]
