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

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

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

if __name__ == "__main__":
    f = Faces("")
    f.add_frame(0, [Face(0,0,10,10)])
    f.add_frame(1, [Face(1,2,11,12)])

    g = Faces("")
    g.__setstate__(f.__getstate__())
    assert g.__getstate__() == f.__getstate__()
