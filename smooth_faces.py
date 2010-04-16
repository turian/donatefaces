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
import common.video

import numpy

def facenumpy(face, width, height):
    (x1, y1, x2, y2) = face.bbox
    x1 /= 1. * width
    x2 /= 1. * width
    y1 /= 1. * height
    y2 /= 1. * height
    return numpy.array((x1, y1, x2, y2))


def main(facefilename, videofilename):
    faces = Faces("")
    faces.__setstate__(common.json.loadfile(facefilename))

    for i, fil, totframes in common.video.frames(videofilename):
        frame = faces.frames[i]
        for face in frame:
            f1 = facenumpy(face, faces.width, faces.height)

            if len(faces.frames) > i+1:
                for nextface in faces.frames[i+1]:
                    f2 = facenumpy(nextface, faces.width, faces.height)

                    print numpy.sum(numpy.square(f1-f2)), f1, f2


if __name__ == "__main__":
#    assert len(sys.argv) == 2
    assert len(sys.argv) == 3
    facefilename = sys.argv[1]
    videofilename = sys.argv[2]

    main(facefilename, videofilename)
