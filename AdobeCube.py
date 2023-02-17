# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 01:42:49 2023

@author: Asterisk
"""


import numpy as np
from colour.io.luts.iridas_cube import read_LUT_IridasCube, LUT3D, LUT3x1D
import os
from typing import Union


class ParserCUBE():
    def __init__(self,fpath = None):
        if fpath is not None:
            self.cube = None
            self.parse(fpath)
        else:
            self.lut = None
            self.cube = None

    @property
    def raw_cube(self):
        if self.cube is None:
            self.cube = self.generate_cube(32)
        return self.cube

    def parse(self,lut_path, clip=True):
        """
        Reads a LUT from the specified path, returning instance of LUT3D or LUT3x1D
        <lut_path>: the path to the file from which to read the LUT (
        <clip>: flag indicating whether to apply clipping of LUT values, limiting all values to the domain's lower and
            upper bounds
        """
        lut: Union[LUT3x1D, LUT3D] = read_LUT_IridasCube(lut_path)
        lut.name = os.path.splitext(os.path.basename(lut_path))[0]  # use base filename instead of internal LUT name

        if clip:
            if lut.domain[0].max() == lut.domain[0].min() and lut.domain[1].max() == lut.domain[1].min():
                lut.table = np.clip(lut.table, lut.domain[0, 0], lut.domain[1, 0])
            else:
                if len(lut.table.shape) == 2:  # 3x1D
                    for dim in range(3):
                        lut.table[:, dim] = np.clip(lut.table[:, dim], lut.domain[0, dim], lut.domain[1, dim])
                else:  # 3D
                    for dim in range(3):
                        lut.table[:, :, :, dim] = np.clip(lut.table[:, :, :, dim], lut.domain[0, dim], lut.domain[1, dim])
        self.lut = lut
        return lut


    def process_slice(self,im_array):
        lut = self.lut
        is_non_default_domain = not np.array_equal(lut.domain, np.array([[0., 0., 0.], [1., 1., 1.]]))
        dom_scale = None
        if is_non_default_domain:
            dom_scale = lut.domain[1] - lut.domain[0]
            im_array = im_array * dom_scale + lut.domain[0]
        #if log:
        #    im_array = im_array ** (1/2.2)
        im_array = lut.apply(im_array)
        return im_array

    def generate_cube(self,input_entry_count=32):
        valgen = lambda : np.linspace(0,1,input_entry_count)
        return np.array([self.process_slice([[np.array([red,green,blue]) for red in valgen()] for green in valgen()]) for blue in valgen()])