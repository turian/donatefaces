#!/bin/sh
#
#  Batch process files given as program argument

export SCRIPTDIR=/home/joseph/dev/python/donatefaces/
for var in "$@"
do
    $SCRIPTDIR/detect_faces.py $var > $var.faces.json
    $SCRIPTDIR/draw_faces.py $var $var.faces.json $var.faces.mp4
    $SCRIPTDIR/smooth_faces.py $var.faces.json > $var.facechains.json
    $SCRIPTDIR/draw_facechains.py $var $var.facechains.json $var.facechains.mp4
done
