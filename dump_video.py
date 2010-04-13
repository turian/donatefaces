#! /bin/env python
import sys, os
import pymedia.muxer as muxer
import pymedia.video.vcodec as vcodec
import pygame

def dumpVideo( inFile, outFilePattern, fmt ):
    dm= muxer.Demuxer( inFile.split( '.' )[ -1 ] )
    i= 1
    f= open( inFile, 'rb' )
    s= f.read( 400000 )
    r= dm.parse( s )
    v= filter( lambda x: x[ 'type' ]== muxer.CODEC_TYPE_VIDEO, dm.streams )
    if len( v )== 0:
        raise 'There is no video stream in a file %s' % inFile
    
    v_id= v[ 0 ][ 'index' ]
    print 'Assume video stream at %d index: ' % v_id
    c= vcodec.Decoder( dm.streams[ v_id ] )
    while len( s )> 0:
        for fr in r:
            if fr[ 0 ]== v_id:
                d= c.decode( fr[ 1 ] )
                # Save file as RGB BMP

                if d:
                    dd= d.convert( fmt )
                    img= pygame.image.fromstring( dd.data, dd.size, "RGB" )
                    pygame.image.save( img, outFilePattern % i )
                    i+= 1
        
        s= f.read( 400000 )
        r= dm.parse( s )
    
    print 'Saved %d frames' % i

# ----------------------------------------------------------------------------------

# Dump the whole video file into the regular BMP images in the directory and file name specified

# http://pymedia.org/

if __name__ == "__main__":
    if len( sys.argv )!= 4:
        print 'Usage: dump_video <file_name> <image_pattern> <format_number>\n<format_number> can be: RGB= 2'+\
                '\n<image_patter> should include %d in the name. ex. test_%d.bmp.'+ \
                '\nThe resulting image will be in a bmp format'
    else:
        pygame.init()
        dumpVideo( sys.argv[ 1 ], sys.argv[ 2 ], int( sys.argv[ 3 ] ) )
        pygame.quit()
