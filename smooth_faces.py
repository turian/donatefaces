#!/usr/bin/python
"""
smooth_faces.py

Load a face file, and "smooth" it.

USAGE:
    python smooth_faces.py facefile > smoothedfacefile
"""

import sys

from faces import Faces

import common.json

import numpy

def main(facefilename):
    faces = Faces("")
    faces.__setstate__(common.json.loadfile(facefilename))

    for i, f in enumerate(faces.frames):
        for face in f:
            (x1, y1, x2, y2) = face.bbox

            print face.bbox


if __name__ == "__main__":
    assert len(sys.argv) == 2
    facefilename = sys.argv[1]

    main(facefilename)
