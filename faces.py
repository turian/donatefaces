#!/usr/bin/python
"""
Module for storing face tracking data.
"""

class Face:
    """
    A single Face.
    """

    def __init__(self, x1, y1, x2, y2):
        assert x1 < x2
        assert y1 < y2
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def is_face(self): return True

    @property
    def bbox(self): return (self.x1, self.y1, self.x2, self.y2)

    def draw(self, img, color="red"):
        """
        Draw the face on a PIL ImageDraw object.
        """
        (x1, y1, x2, y2) = self.bbox
        img.rectangle((x1-1, y1-1, x2+1, y2+1), outline=color)
        img.rectangle((x1, y1, x2, y2), outline=color)
        img.rectangle((x1+1, y1+1, x2-1, y2-1), outline=color)

    def __repr__(self):
        return `self.bbox`

    def __hash__(self):
        return hash(self.__repr__())

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

    def __eq__(self, other):
        return self.bbox == other.bbox

class Faces:
    """
    Class to store face tracking data.
    """

    def __init__(self, filename):
        """
        TODO: Store video information: filename, format information, file size, sha1sum of file, width+height, #frames, etc.
        TODO: Store information about which face detection algorithm was used, with which hyperparams
        """
        self.filename = filename
        self.frames = []

    def set_dimensions(self, width, height):
        if "width" in self.__dict__: assert self.width == width
        else: self.width = width
        if "height" in self.__dict__: assert self.height == height
        else: self.height = height

    def add_frame(self, framenumber, facelist):
        assert len(self.frames) == framenumber
        for face in facelist: assert face.is_face()
        self.frames.append(facelist)

    def __getstate__(self):
        result = self.__dict__.copy()
        result["frames"] = [[face.__getstate__() for face in frame] for frame in result["frames"]]
        return result

    def __setstate__(self, dict):
        self.__dict__ = dict
        newframes = []
        for frame in dict["frames"]:
            newfaces = []
            for face in frame:
                newface = Face(0,0,10,10)
                newface.__setstate__(face)
                newfaces.append(newface)
            newframes.append(newfaces)
        self.frames = newframes

#class FaceChain:
#    """
#    Chain of one single face.
#    self.data = a list of (framenumber, Face) tuples, where framenumber is increasing
#    """
#
#class FaceChains:
#    """
#    Class to store face tracking data.
#    Unless Faces, which stores each frame in isolation, we have a member
#    variable called "chains". "chains" is a list of type Chain.
#    """
#
#    def __init__(self, filename):
#        """
#        TODO: Store video information: filename, format information, file size, sha1sum of file, width+height, #frames, etc.
#        TODO: Store information about which face detection algorithm was used, with which hyperparams
#        """
#        self.filename = filename
#        self.frames = []
#
#    def set_dimensions(self, width, height):
#        if "width" in self.__dict__: assert self.width == width
#        else: self.width = width
#        if "height" in self.__dict__: assert self.height == height
#        else: self.height = height
#
#    def add_frame(self, framenumber, facelist):
#        assert len(self.frames) == framenumber
#        for face in facelist: assert face.is_face()
#        self.frames.append(facelist)
#
#    def __getstate__(self):
#        result = self.__dict__.copy()
#        result["frames"] = [[face.__getstate__() for face in frame] for frame in result["frames"]]
#        return result
#
#    def __setstate__(self, dict):
#        self.__dict__ = dict
#        newframes = []
#        for frame in dict["frames"]:
#            newfaces = []
#            for face in frame:
#                newface = Face(0,0,10,10)
#                newface.__setstate__(face)
#                newfaces.append(newface)
#            newframes.append(newfaces)
#        self.frames = newframes

if __name__ == "__main__":
    f = Faces("")
    f.add_frame(0, [Face(0,0,10,10)])
    f.add_frame(1, [Face(1,2,11,12)])

    g = Faces("")
    g.__setstate__(f.__getstate__())
    assert g.__getstate__() == f.__getstate__()
