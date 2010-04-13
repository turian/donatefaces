#!/usr/bin/python

# face_detect.py

# Face Detection using OpenCV. Based on sample code from:
# http://python.pastebin.com/m76db1d6b

# Usage: python face_detect.py <image_file>

import sys, os, os.path
import tempfile
import shutil

import common.video
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
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, 0, cvSize(50,50))
#    faces = cvHaarDetectObjects(grayscale, cascade, storage, scale_factor=1.1, min_neighbors=3, flags=0, cvSize(50,50))

#    print dir(faces)
    bboxes = []
    if faces:
        for f in faces:
            print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
        bboxes = [(f.x, f.y, f.x+f.width, f.y+f.height) for f in faces]
    return bboxes

def find_faces(framenumber, dir):
    pil_img = common.video.grab_frame(sys.argv[1], framenumber=framenumber)

    # Convert to OpenCV image from PIL image, on disk
    tmp = tempfile.NamedTemporaryFile(suffix=".png")
    pil_img.save(tmp.name)
    image = cvLoadImage(tmp.name)

#   TODO: Convert to OpenCV image from PIL image, *IN MEMORY*
#   http://stackoverflow.com/questions/1650568/how-do-i-create-an-opencv-image-from-a-pil-image
#    cv_img = cv.CreateImageHeader(pil_img.size, cv.IPL_DEPTH_8U, 3)  # RGB image
#    cv.SetData(cv_img, pil_img.tostring(), pil_img.size[0]*3)

#    print image.imageSize
    faces = detectObjects(image)

    pil_img = Image.open(tmp.name)

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
    outfile = os.path.join(dir, "out%04d.jpg" % framenumber)
    print >> sys.stderr, "\n\nWriting to %s\n\n" % outfile
    pil_img.save(outfile, "JPEG")
#   pil_img.save("out%04d.png" % framenumber, "PNG")

def main():
    assert len(sys.argv) == 2

    dir = tempfile.mkdtemp()
    try:
        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -i %s %s" % (sys.argv[1], os.path.join(dir, 'in%04d.jpg'))
        print >> sys.stderr, "Decomposing video to images:", cmd
        common.misc.runcmd(cmd)

        infiles = []
        for f in os.listdir(dir): pass

#        for i in range(30):
#            find_faces(i, dir=dir)

        # I learned this command from here: http://electron.mit.edu/~gsteele/ffmpeg/
        cmd = "ffmpeg -y -r 30 -b 1800 -i %s test1800.mp4" % (os.path.join(dir, 'out%04d.jpg'))
        print >> sys.stderr, "Stitching video together as test1800.mp4"
        print >> sys.stderr, cmd
        common.misc.runcmd(cmd)

    finally:
        print >> sys.stderr, "Removing dir %s" % dir
        shutil.rmtree(dir)

if __name__ == "__main__":
    main()
