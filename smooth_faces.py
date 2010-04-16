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

# Maximum squared error between the bounding boxes of subseq faces
MAXSQRERR = 0.01
#MAXSQRERR = 0.02 # too high

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

    showedcnt = 0

    for i, fil, totframes in common.video.frames(videofilename):
        frame = faces.frames[i]
        for face in frame:
            f1 = facenumpy(face, faces.width, faces.height)

            if len(faces.frames) > i+1:
                for nextface in faces.frames[i+1]:
                    f2 = facenumpy(nextface, faces.width, faces.height)

                    diff = numpy.sum(numpy.square(f1-f2))
                    if diff > MAXSQRERR and diff < MAXSQRERR*1.1 and showedcnt < 25:
                        from PIL import Image, ImageDraw
                        pil_img = Image.open(fil)
                        draw = ImageDraw.Draw(pil_img)
                        face.draw(draw)
                        nextface.draw(draw, color="green")
                        pil_img.show()
                        print diff, f1, f2
                        showedcnt += 1


if __name__ == "__main__":
#    assert len(sys.argv) == 2
    assert len(sys.argv) == 3
    facefilename = sys.argv[1]
    videofilename = sys.argv[2]

    main(facefilename, videofilename)
