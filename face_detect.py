#!/usr/bin/python

# face_detect.py

# Face Detection using OpenCV. Based on sample code from:
# http://python.pastebin.com/m76db1d6b

# Usage: python face_detect.py <image_file>

import sys, os

import common.video

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
    faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
                                                         CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

    print dir(faces)
    if faces:
        for f in faces:
            print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
    return faces

def main():
    pil_img = common.video.grab_frame(sys.argv[1], framenumber=0)

    # Convert to OpenCV image from PIL image, on disk
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix=".png")
    pil_img.save(tmp.name)
    image = cvLoadImage(tmp.name)

#   TODO: Convert to OpenCV image from PIL image, *IN MEMORY*
#   http://stackoverflow.com/questions/1650568/how-do-i-create-an-opencv-image-from-a-pil-image
#    cv_img = cv.CreateImageHeader(pil_img.size, cv.IPL_DEPTH_8U, 3)  # RGB image
#    cv.SetData(cv_img, pil_img.tostring(), pil_img.size[0]*3)

#    print image.imageSize
    faces = detectObjects(image)

    if faces:
        for f in faces:
            print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
    
#    tmp.close()

if __name__ == "__main__":
    main()
