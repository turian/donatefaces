#!/usr/bin/python
"""
detect_faces.py

Face Detection using OpenCV.
Print the faces detected as a JSON object, where the "frames" key gives
a list of frames. Each frame contains a list of face bboxes.

USAGE:
    python detect_faces.py videofil > facefile

Based on sample code from:
    http://python.pastebin.com/m76db1d6b
"""

# Face must be at least 5% of the shot
MINFACEWIDTH_PERCENT = 0.05
MINFACEHEIGHT_PERCENT = 0.05
## Face must be at least 7.5% of the shot
#MINFACEWIDTH_PERCENT = 0.075
#MINFACEHEIGHT_PERCENT = 0.075

import sys

#import common.video
import common.str
from common.stats import stats
import common.json

import common.video

from opencv.cv import cvCreateImage, cvSize, cvCvtColor, cvCreateMemStorage, cvClearMemStorage, cvEqualizeHist, cvLoadHaarClassifierCascade, cvHaarDetectObjects, CV_HAAR_DO_CANNY_PRUNING, CV_BGR2GRAY
from opencv.highgui import cvLoadImage

from faces import Face, Faces

def detect_faces(image):
    """Converts an image to grayscale and prints the locations of any
         faces found"""
    grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
    cvCvtColor(image, grayscale, CV_BGR2GRAY)

    storage = cvCreateMemStorage(0)
    cvClearMemStorage(storage)
    cvEqualizeHist(grayscale, grayscale)

    # The default parameters (scale_factor=1.1, min_neighbors=3,
    # flags=0) are tuned for accurate yet slow face detection. For
    # faster face detection on real video images the better settings are
    # (scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING).
    # --- http://www710.univ-lyon1.fr/~bouakaz/OpenCV-0.9.5/docs/ref/OpenCVRef_Experimental.htm#decl_cvHaarDetectObjects
    # The size box is of the *minimum* detectable object size. Smaller box = more processing time. - http://cell.fixstars.com/opencv/index.php/Facedetect
    minsize = (int(MINFACEWIDTH_PERCENT*image.width+0.5),int(MINFACEHEIGHT_PERCENT*image.height))
    print >> sys.stderr, "Min size of face: %s" % `minsize`

    faces = []
    for cascadefile in ['/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml']:
#    for cascadefile in ['/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml', '/usr/share/opencv/haarcascades/haarcascade_profileface.xml']:
        cascade = cvLoadHaarClassifierCascade(cascadefile, cvSize(1,1))
#        faces += cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
#        faces += cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, 0, cvSize(MINFACEWIDTH,MINFACEHEIGHT))
#        faces += cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, 0, cvSize(MINFACEWIDTH,MINFACEHEIGHT))
#        faces += cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 3, CV_HAAR_DO_CANNY_PRUNING, cvSize(*minsize))
        faces += cvHaarDetectObjects(grayscale, cascade, storage, 1.1, 4, CV_HAAR_DO_CANNY_PRUNING, cvSize(*minsize))
#        faces += cvHaarDetectObjects(grayscale, cascade, storage, scale_factor=1.1, min_neighbors=3, flags=0, cvSize(50,50))

#    print dir(faces)
    bboxes = []
    if faces:
        for f in faces:
            print >> sys.stderr, "\tFace at [(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height)
        bboxes = [Face(f.x, f.y, f.x+f.width, f.y+f.height) for f in faces]
    return bboxes

def main(videofilename):
    faces = Faces(videofilename)
    for i, f, totframes in common.video.frames(videofilename):
#    for i, f, totframes in common.video.frames(videofilename, maxframes=1000):
        print >> sys.stderr, "Processing %s, image %s" % (f, common.str.percent(i+1, totframes))
        print >> sys.stderr, stats()
        image = cvLoadImage(f)
        faces.set_dimensions(image.width, image.height)
        faces.add_frame(i, detect_faces(image))

        if i % 100 == 0 and i != 0:
            print >> sys.stderr, common.json.dumps(faces.__getstate__())
    print common.json.dumps(faces.__getstate__())

if __name__ == "__main__":
    assert len(sys.argv) == 2
    videofilename = sys.argv[1]

    main(videofilename)
