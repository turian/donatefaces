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

def main(facefilename):
    faces = Faces("")
    faces.__setstate__(common.json.loadfile(facefilename))

    showedcnt = 0

    # Construct one chain per face
    chains = []
    for i, frame in enumerate(faces.frames):
        for face in frame:
            assert face.is_face()
            chain = [(i, face)]
            chains.append(FaceChain(chain))
    chains.sort()

    facechains = FaceChains()
    facechains.copy_from_faces(faces)
    facechains.chains = chains

    facechains.join_nearby(1)
    facechains.deleteshortchains()

    print common.json.dumps(facechains.__getstate__())

if __name__ == "__main__":
    assert len(sys.argv) == 2
    facefilename = sys.argv[1]

    main(facefilename)
