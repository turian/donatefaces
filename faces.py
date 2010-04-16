"""
Module for storing face tracking data.
"""

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
        self.frames.append(facelist)
