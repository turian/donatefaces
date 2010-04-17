#!/usr/bin/python
"""
smooth_faces.py

Load a face file, and "smooth" it.

USAGE:
    python smooth_faces.py facefile > smoothedfacefile

TODO:
    We might want to allow the smoother to skip a frame or two. (i.e. we
    can connect chains that are slightly separated.)
"""

import sys

from faces import Faces, FaceChain, FaceChains

import common.json

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

def main(facefilename):
    faces = Faces("")
    faces.__setstate__(common.json.loadfile(facefilename))

    showedcnt = 0

    prevlinks = {}
    nextlinks = {}

    for i, frame in enumerate(faces.frames):
        for face in frame:
            f1 = facenumpy(face, faces.width, faces.height)

            if i+1 >= len(faces.frames): continue

            if len(faces.frames[i+1]) == 0: continue

            # Find closestnextface, the closest face in the next frame to this face
            closestnextfacediff = 1e99
            closestnextface = None
            for nextface in faces.frames[i+1]:
                f2 = facenumpy(nextface, faces.width, faces.height)
                diff = numpy.sum(numpy.square(f1-f2))
                if diff < closestnextfacediff:
                    closestnextfacediff = diff
                    closestnextface = nextface

            # Find closestprevface, the closest face in the current frame to closestnextface
            closestprevfacediff = 1e99
            closestprevface = None
            fp1 = facenumpy(closestnextface, faces.width, faces.height)
            for prevface in faces.frames[i]:
                fp2 = facenumpy(prevface, faces.width, faces.height)
                diff = numpy.sum(numpy.square(fp1-fp2))
                if diff < closestprevfacediff:
                    closestprevfacediff = diff
                    closestprevface = prevface

            # If closestprevface == face, i.e. if we have the nearest
            # face in both directions when stepping through the frame,
            # then we have a potential link
            if face != closestprevface: continue

            # Also, the faces can't be too far apart
            if closestnextfacediff > MAXSQRERR: continue

            nextlinks[(i, face)] = (i+1, closestnextface)
            prevlinks[(i+1, closestnextface)] = (i, face)

    # Construct all chains
    chains = []
    for i, face in nextlinks:
        if (i, face) not in prevlinks:
            # We have the start of a chain
            chain = [(i, face)]
            while (i, face) in nextlinks:
                i, face = nextlinks[(i, face)]
                chain.append((i, face))
                assert chain[-1][0] == chain[-2][0]+1
            chains.append(FaceChain(chain))
    chains.sort()

    facechains = FaceChains()
    facechains.copy_from_faces(faces)
    facechains.chains = chains
    print common.json.dumps(facechains.__getstate__())

if __name__ == "__main__":
    assert len(sys.argv) == 2
    facefilename = sys.argv[1]

    main(facefilename)
