#!/usr/bin/python
"""
draw_facechains.py

Load a video and a face chains file, and output a new video drawing red boxes
around the faces.

USAGE:
    python draw_faces.py invideofil facechainfile outvideofile
"""

import os
import os.path
import re
import shutil
import sys
import tempfile

from faces import FaceChains

import common.json
from common.stats import stats
import common.video

from PIL import Image, ImageDraw

def draw_faces(faces, infilename, outfilename):
    pil_img = Image.open(infilename)

    # Draw red boxes around faces
    draw = ImageDraw.Draw(pil_img)
    for face, color in faces:
#        print face, color
        face.draw(draw, color=color)
    del draw

#    # REMOVEME: Scale image to height of 320
#    newwidth = 320
#    newheight = newwidth * pil_img.size[1] / pil_img.size[0]
##    print pil_img.size
##    print newwidth, newheight
#    pil_img= pil_img.resize((newwidth, newheight), Image.ANTIALIAS) 

    # Save to out.png
    print >> sys.stderr, "Writing to %s" % outfilename
    print >> sys.stderr, stats()
    pil_img.save(outfilename, "JPEG")
#   pil_img.save("out%04d.png" % framenumber, "PNG")

def main(invideofilename, facechainfilename, outvideofilename):
    faces = FaceChains()
    faces.__setstate__(common.json.loadfile(facechainfilename))

    dir = tempfile.mkdtemp()
    try:
        from collections import defaultdict
        frames = defaultdict(list)
        maxframe = 0
        for chain in faces.chains:
#            print chain
            color = ["red", "yellow", "green", "blue", "purple", "orange"][chain.__hash__() % 6]
            for i, face in chain.data:
                frames[i].append((face, color))
                if i > maxframe: maxframe = i
#        print >> sys.stderr, frames


        for i, f, totframes in common.video.frames(invideofilename, maxframes=maxframe):
            outf = os.path.join(dir, "out%05d.jpg" % i)
            print >> sys.stderr, "Processing %s to %s, image %s" % (f, outf, common.str.percent(i+1, totframes))
            print >> sys.stderr, stats()

            draw_faces(frames[i], f, outf)

        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -b 10000k -i %s %s" % (os.path.join(dir, 'out%05d.jpg'), outvideofilename)
        print >> sys.stderr, "Stitching video together as test1800.mp4"
        print >> sys.stderr, cmd
#        import time
#        time.sleep(30)
        common.misc.runcmd(cmd)
        print >> sys.stderr, stats()

    finally:
        print >> sys.stderr, "Removing dir %s" % dir
        shutil.rmtree(dir)

if __name__ == "__main__":
    assert len(sys.argv) == 4
    invideofilename = sys.argv[1]
    facechainfilename = sys.argv[2]
    outvideofilename = sys.argv[3]

    main(invideofilename, facechainfilename, outvideofilename)
