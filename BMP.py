# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 07:58:29 2023

@author: Asterisk
"""
import numpy as np
from imageio.v2 import imread, imwrite

class ParserBMP():
    def __init__(self,fpath = None):
        self.cube = None
        if fpath is not None:
            self._parse(fpath)

    @property
    def raw_cube(self):
        return self.cube

    @classmethod
    def parse(cls,filename):
        self = cls()
        self._parse(filename)

    def _parse(self,filename):
        #4 x 8
        base = imread(filename)
        def recoordinate(base,i,j,k):
            col = k%4
            row = k//4
            ni = i + col*32
            nj = j + row*32
            return base[nj][ni][:3]
        cube = np.array([[[recoordinate(base,i,j,k)/255
                    for i in range(32)]
                       for j in range(32)]
                          for k in range(32)])
        self.cube = cube

    @classmethod
    def flatten_cube(cls,cube):
        if cube.shape != (32,32,32,3):
            raise ValueError("Only 32x32x32 Cubes Accepted %s Given"%(str(cube.shape[:3])))
        return np.vstack([np.hstack(cube[4*k:(k+1)*4]) for k in range(8)])

    @classmethod
    def write_cube(cls,cube,outf):
        imwrite(outf,cls.flatten_cube(cube))