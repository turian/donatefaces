#!/usr/bin/python
"""
Module for storing face tracking data.
"""

import numpy

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

class FaceChain:
    """
    Chain of one single face.
    self.data = a list of (framenumber, Face) tuples, where framenumber is increasing
    """

    def __init__(self, data):
        self.data = data
        self.sanity_check()

    def sanity_check(self):
        """
        Make sure the chain frame numbers are increasing incrementally.
        """
        for j, (i, face) in enumerate(self.data):
            assert face.is_face()
            if len(self.data) > j+1:
                assert self.data[j+1][0] == self.data[j][0]+1

    def join(self, chain):
        """
        Join this chain to a subsequent chain.
        """
        self.data += chain.data
        self.sanity_check()

    @property
    def firstitem(self):
        self.sanity_check()
        return self.data[0]

    @property
    def lastitem(self):
        self.sanity_check()
        return self.data[-1]

    @property
    def firstframe(self):
        return self.firstitem[0]

    @property
    def lastframe(self):
        return self.lastitem[0]

    @property
    def firstface(self):
        return self.firstitem[1]

    @property
    def lastface(self):
        return self.lastitem[1]

    def __cmp__(self, other):
        return cmp(self.data, other.data)

    def __repr__(self):
        return `self.data`

    def __hash__(self):
        return hash(self.__repr__())

    def __getstate__(self):
        result = self.__dict__.copy()
        result["data"] = [(i, face.__getstate__()) for i, face in result["data"]]
        return result

class FaceChains:
    """
    Class to store face tracking data.
    Unless Faces, which stores each frame in isolation, we have a member
    variable called "chains". "chains" is a list of type FaceChain.
    """

    def __init__(self):
        self.chains = []

    def copy_from_faces(self, faces):
        """
        Copy data from a faces object.
        """
        dict = faces.__dict__.copy()
        del dict["frames"]
        self.__dict__.update(dict)

#
#    def set_dimensions(self, width, height):
#        if "width" in self.__dict__: assert self.width == width
#        else: self.width = width
#        if "height" in self.__dict__: assert self.height == height
#        else: self.height = height

    @property
    def totalfaces(self):
        tot = 0
        for chain in self.chains:
            tot += len(chain.data)
        return tot


    def join_nearby(self, framediff, MAXSQRERR = 0.01):
        """
        Find face chains that are framediff frames apart, and then join them if they are near to each other.

        Maximum squared error between the bounding boxes of subseq faces
            MAXSQRERR = 0.01
            #MAXSQRERR = 0.02 # too high
        """

        origtotalfaces = self.totalfaces

        firstframe_to_chains = {}
        for chain in self.chains:
            if chain.firstframe not in firstframe_to_chains:
                firstframe_to_chains[chain.firstframe] = []
            firstframe_to_chains[chain.firstframe].append(chain)
        lastframe_to_chains = {}
        for chain in self.chains:
            if chain.lastframe not in lastframe_to_chains:
                lastframe_to_chains[chain.lastframe] = []
            lastframe_to_chains[chain.lastframe].append(chain)

        prevlinks = {}
        nextlinks = {}

        def facenumpy(face, width, height):
            (x1, y1, x2, y2) = face.bbox
            x1 /= 1. * width
            x2 /= 1. * width
            y1 /= 1. * height
            y2 /= 1. * height
            return numpy.array((x1, y1, x2, y2))
    
        for chain1 in self.chains:
            f1 = facenumpy(chain1.lastface, self.width, self.height)

            # Find closestnextchain, the closest face in the next frame to this face
            closestnextchaindiff = 1e99
            closestnextchain = None

            nextstartframe = chain1.lastframe + framediff
            if nextstartframe not in firstframe_to_chains: continue
            for chain2 in firstframe_to_chains[nextstartframe]:
                f2 = facenumpy(chain2.firstface, self.width, self.height)
                diff = numpy.sum(numpy.square(f1-f2))
                if diff < closestnextchaindiff:
                    closestnextchaindiff = diff
                    closestnextchain = chain2

            # Find closestprevchain, the closest face in the current frame to closestnextchain
            closestprevchaindiff = 1e99
            closestprevchain = None
            prevlastframe = chain1.lastframe
            fp1 = facenumpy(closestnextchain.firstface, self.width, self.height)
            for pchain1 in lastframe_to_chains[prevlastframe]:
                fp2 = facenumpy(pchain1.lastface, self.width, self.height)
                diff = numpy.sum(numpy.square(fp1-fp2))
                if diff < closestprevchaindiff:
                    closestprevchaindiff = diff
                    closestprevchain = pchain1

            # If closestprevchain == chain1, i.e. if we have the nearest
            # face in both directions when stepping through the frame,
            # then we have a potential link
            if chain1 != closestprevchain: continue
    
            # Also, the faces can't be too far apart
            if closestnextchaindiff > MAXSQRERR: continue

            nextlinks[chain1] = closestnextchain
            prevlinks[closestnextchain] = chain1

        newchains = []
        usedalready = {}
        for chain1 in self.chains:
            if chain1 in usedalready: continue
#            print "Orig chain", chain1
            curchain = chain1
            usedalready[curchain] = True
            while curchain in nextlinks:
                nextchain = nextlinks[curchain]
                chain1.join(nextchain)
                curchain = nextchain
                usedalready[curchain] = True
#            print "New chain", chain1
            newchains.append(chain1)
        self.chains = newchains

#        print origtotalfaces, self.totalfaces
        assert origtotalfaces == self.totalfaces

    def deleteshortchains(self, MINLENGTH=15):
        newchains = []
        for chain in self.chains:
            if len(chain.data) >= MINLENGTH:
                newchains.append(chain)
        self.chains = newchains

    def __getstate__(self):
        result = self.__dict__.copy()
        result["chains"] = [chain.__getstate__() for chain in result["chains"]]
        return result

    def __setstate__(self, dict):
        self.__dict__ = dict
        import sys
        chains = []
        for c in dict["chains"]:
            chain = []
            for i, face in c["data"]:
                f = Face(0,0,1,1)
                f.__setstate__(face)
                chain.append((i, f))
            chains.append(FaceChain(chain))
        self.chains = chains

if __name__ == "__main__":
    f = Faces("")
    f.add_frame(0, [Face(0,0,10,10)])
    f.add_frame(1, [Face(1,2,11,12)])

    g = Faces("")
    g.__setstate__(f.__getstate__())
    assert g.__getstate__() == f.__getstate__()
