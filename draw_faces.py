#!/usr/bin/python

# draw_faces.py

import os
import os.path
import re
import shutil
import sys
import tempfile

from faces import Faces

import common.json
from common.stats import stats
import common.video

from PIL import Image, ImageDraw

def draw_faces(faces, infilename, outfilename):
    pil_img = Image.open(infilename)

    # Draw red boxes around faces
    if faces:
        draw = ImageDraw.Draw(pil_img)
        for (x1, y1, x2, y2) in faces:
            draw.rectangle((x1-1, y1-1, x2+1, y2+1), outline="red")
            draw.rectangle((x1, y1, x2, y2), outline="red")
            draw.rectangle((x1+1, y1+1, x2-1, y2-1), outline="red")
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

def main(invideofilename, facefilename, outvideofilename):
    faces = Faces("")
    faces.__dict__ = common.json.loadfile(facefilename)

    dir = tempfile.mkdtemp()
    try:
        for i, f, totframes in common.video.frames(invideofilename):
            outf = f.replace("in", "out")
            print >> sys.stderr, "Processing %s to %s, image %s" % (f, outf, common.str.percent(i+1, totframes))
            print >> sys.stderr, stats()

            draw_faces(faces.frames[i], f, outf)

        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -b 10000k -i %s %s" % (os.path.join(dir, 'out%04d.jpg'), outvideofilename)
        print >> sys.stderr, "Stitching video together as test1800.mp4"
        print >> sys.stderr, cmd
        common.misc.runcmd(cmd)
        print >> sys.stderr, stats()

    finally:
        print >> sys.stderr, "Removing dir %s" % dir
        shutil.rmtree(dir)

if __name__ == "__main__":
    assert len(sys.argv) == 4
    invideofilename = sys.argv[1]
    facefilename = sys.argv[2]
    outvideofilename = sys.argv[3]

    main(invideofilename, facefilename, outvideofilename)
