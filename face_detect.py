#!/usr/bin/python

# face_detect.py

# Face Detection using OpenCV. Based on sample code from:
# http://python.pastebin.com/m76db1d6b

# Usage: python face_detect.py <image_file>

# Face must be 7.5% of the shot
MINFACEWIDTH_PERCENT = 0.075
MINFACEHEIGHT_PERCENT = 0.075

import sys, os, os.path, re
import tempfile
import shutil

#import common.video
import common.str
from common.stats import stats
#import common.misc

from PIL import Image, ImageDraw

from opencv.cv import *
from opencv.highgui import *

def detectObjects(image):
    """Converts an image to grayscale and prints the locations of any
         faces found"""

    grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
    cvCvtColor(image, grayscale, CV_BGR2GRAY)

    storage = cvCreateMemStorage(0)
    cvClearMemStorage(storage)
    cvEqualizeHist(grayscale, grayscale)
    cascade = cvLoadHaarClassifierCascade(
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        cvSize(1,1))

    # The default parameters (scale_factor=1.1, min_neighbors=3,
    # flags=0) are tuned for accurate yet slow face detection. For
    # faster face detection on real video images the better settings are
    # (scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING).
    # --- http://www710.univ-lyon1.fr/~bouakaz/OpenCV-0.9.5/docs/ref/OpenCVRef_Experimental.htm#decl_cvHaarDetectObjects
    # The size box is of the *minimum* detectable object size. Smaller box = more processing time. - http://cell.fixstars.com/opencv/index.php/Facedetect
    minsize = (int(MINFACEWIDTH_PERCENT*image.width+0.5),int(MINFACEHEIGHT_PERCENT*image.height))
    print >> sys.stderr, "Min size of face: %s" % `minsize`
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, 0, cvSize(MINFACEWIDTH,MINFACEHEIGHT))
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, 0, cvSize(MINFACEWIDTH,MINFACEHEIGHT))
    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, CV_HAAR_DO_CANNY_PRUNING, cvSize(*minsize))
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, scale_factor=1.1, min_neighbors=3, flags=0, cvSize(50,50))

#    print dir(faces)
    bboxes = []
    if faces:
        for f in faces:
            print >> sys.stderr, "\tFace at [(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height)
        bboxes = [(f.x, f.y, f.x+f.width, f.y+f.height) for f in faces]
    return bboxes

def find_faces(filename, outfilename):
    image = cvLoadImage(filename)

    faces = detectObjects(image)

    pil_img = Image.open(filename)

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

def main():
    assert len(sys.argv) == 2

    dir = tempfile.mkdtemp()
    inre = re.compile("in.*.jpg")
    try:
        # Decompose video into images
        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -i %s %s" % (sys.argv[1], os.path.join(dir, 'in%04d.jpg'))
#        cmd = "ffmpeg -y -t 10 -r 30 -i %s %s" % (sys.argv[1], os.path.join(dir, 'in%04d.jpg'))
        print >> sys.stderr, "Decomposing video to images:", cmd, "\n"
        common.misc.runcmd(cmd)
        print >> sys.stderr, stats()

        # Find all files to process
        infiles = []
        for f in os.listdir(dir):
            if inre.match(f):
                infiles.append(f)
        infiles.sort()

        for i, f in enumerate(infiles):
            outf = f.replace("in", "out")
            f = os.path.join(dir, f)
            outf = os.path.join(dir, outf)
            print >> sys.stderr, "Processing %s to %s, image %s" % (f, outf, common.str.percent(i+1, len(infiles)))
            print >> sys.stderr, stats()
            find_faces(f, outf)

        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -b 10000 -i %s test1800.mp4" % (os.path.join(dir, 'out%04d.jpg'))
        print >> sys.stderr, "Stitching video together as test1800.mp4"
        print >> sys.stderr, cmd
        common.misc.runcmd(cmd)
        print >> sys.stderr, stats()

    finally:
        print >> sys.stderr, "Removing dir %s" % dir
        shutil.rmtree(dir)

if __name__ == "__main__":
    main()
