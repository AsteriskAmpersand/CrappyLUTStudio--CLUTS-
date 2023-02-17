# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 02:58:47 2023

@author: Asterisk
"""
import construct as C
from matplotlib import pyplot as plt
from collections.abc import Iterable
import numpy as np
import struct
from pathlib import Path
from Interpolator import TetrahedralInterpolator
from LUT_3DL import Parser3DL
from AdobeCube import ParserCUBE
from BMP import ParserBMP
from pathlib import Path

def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


C_PixelData = C.Struct("offset"/C.Int64ul,
                       "data" / C.Pointer(C.this.offset,
                                          C.Int16ul[4][C.this._.header.height]
                                          [C.this._.header.width]
                                          [C.this._.header.depth]
                                          )
                       )

C_Header = C.Struct(
    "signature" / C.Const([0x54, 0x45, 0x58, 0x00], C.Byte[4]),
    "version" / C.Const(16, C.Int64ul),
    "datablock" / C.Const(0, C.Int32ul),
    "format" / C.Const(3, C.Int32ul),
    "mipCount" / C.Const(1, C.Int32ul),
    "width" / C.Int32ul,
    "height" / C.Int32ul,
    "mipListCount" / C.Const(1, C.Int32ul),
    "typeData" / C.Const(2, C.Int32ul),
    "depth" / C.Int32ul,
    "NULL0" / C.Const([0]*3, C.Int32ul[3]),
    "NEG0" / C.Const(-1, C.Int32sl),
    "NULL1" / C.Const([0]*2, C.Int32sl[2]),
    "Special" / C.Const(1, C.Int32sl),
    "NULL2" / C.Const([0]*4, C.Int32sl[4]),
    "NEG1" / C.Const([-1]*8, C.Int32sl[8]),
    "flags" / C.Int8ul[32],
    "NULLX" / C.Const([0]*8, C.Int32sl[8]),
)

C_LUTTex = C.Struct(
    "header" / C_Header,
    "pixelData" /
    C_PixelData[C.this.header.mipCount][C.this.header.mipListCount],
)



class TexHeader():
    def __init__(self):
        self.signature = [0x54, 0x45, 0x58, 0x00]
        self.version = 16
        self.datablock = 0
        self.format = 3
        self.mipCount = 1
        self.width = 0
        self.height = 0
        self.mipListCount = 1
        self.typeData = 2
        self.depth = 0
        self.NULL0 = [0]*3
        self.NEG0 = -1
        self.NULL1 = [0, 0]
        self.Special = 1
        self.NULL2 = [0]*4
        self.NEG1 = [-1]*8
        self.flags = [32, 0, 0, 0, 32, 0, 32, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 32, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 32, 0]
        self.NULLX = [0] * 8

    def build(self):
        return C_Header.build({c.name: getattr(self, c.name) for c in C_Header.subcons})


class DepthData():
    def __init__(self, input_depth, output_depth, input_space=None, output_space=None):
        self.input_depth = input_depth
        self.output_depth = output_depth
        self.color_space = 2**output_depth if output_space is None else output_space
        self.input_space = 2**input_depth if input_space is None else input_space
        self.colorstep = self.color_space//self.input_space
        # self.colorstep * (self.input_space-1)
        gamelim = self.color_space - 1 -2*self.colorstep
        true = self.color_space - 1
        renormalizer = 2 * true**2/gamelim
        #
        self.alpha = 0x2b88
        self.normalizer = true#self.color_space-1# + 2*self.colorstep


class LUT_Tex():
    def __init__(self, filename=None):
        if filename is not None:
            rawTex = C_LUTTex.parse_file(filename)
            self.header = rawTex.header
            self.pixelData = rawTex.pixelData
            self.depth_data = DepthData(5, 14)
            self.cube = self.pixelData[0][0].data
        else:
            self.header = TexHeader()
            self.depth_data = DepthData(0, 0)
            self.cube = None

    def build_array(self, pxData, title=""):
        normalizer = self.depth_data.normalizer
        img = [[[np.array((red[0]/normalizer, red[1]/normalizer, red[2]/normalizer))
                 for red in green]
                for green in blue]
               for blue in pxData]
        return np.array(img)

    @property
    def array(self):
        return self.build_array(self.cube)
    @property
    def raw_cube(self):
        return self.array

    @classmethod
    def parse(cls, filename):
        return cls(filename)

    def to_TEX(self,outf):
        with open(outf,"wb") as outfb:
            outfb.write(self.serialize())

    @classmethod
    def from_cube(cls, cube, output_depth=14):
        entry_count = cube.shape[0]
        self = cls()
        self.header.height = self.header.width = self.header.depth = entry_count
        self.depth_data = DepthData(np.ceil(np.log2(entry_count)), output_depth, input_space = entry_count)
        normalizer = self.depth_data.normalizer
        alpha = self.depth_data.alpha
        self.cube = np.array([[[(red[0]*normalizer, red[1]*normalizer, red[2]*normalizer, alpha)
                       for red in green] for green in blue] for blue in cube])
        return self

    def serialize_cube(self, cube):
        return b''.join([struct.pack("HHHH", *map(lambda x: int(np.round(x)),red)) for blue in cube for green in blue for red in green])

    def serialize(self):
        bin_header = self.header.build()
        offsets = struct.pack("Q", 192)
        bin_cube = self.serialize_cube(self.cube)
        return bin_header + offsets + bin_cube

    def to_3DL(self, outf=None, override_defaults = False):
        p = Parser3DL()
        if override_defaults:
            p.input_depth = self.depth_data.input_depth
            p.output_depth = self.depth_data.output_depth
        p.load_cube(self.array)
        if outf:
            with open(outf, "w") as outf:
                outf.write(p.write_cube())
        else:
            return p

    @classmethod
    def from_3DL(cls, infn, input_entry_count=32, output_depth=14, interpolator=None):
        if interpolator is None:
            interpolator = TetrahedralInterpolator
        p = Parser3DL.parse(infn)
        if input_entry_count is not None and input_entry_count != p.input_entry_count:
            ip = interpolator(p.cube)
            cube = ip.generate_cube(input_entry_count)
        if output_depth is None:
            output_depth = p.output_depth
        return cls.from_cube(cube, output_depth)

    @classmethod
    def from_AdobeCube(cls, infn, input_entry_count=32, output_depth=14, interpolator=None):
        pcube = ParserCUBE(infn)
        cube = pcube.generate_cube(input_entry_count)
        return cls.from_cube(cube, output_depth)

    @classmethod
    def identity(cls,input_entry_count = 32):
        arange = lambda : np.linspace(0,1,input_entry_count)
        cube = np.array([[[(red,green,blue)
                               for red in arange()]
                                  for green in arange()]
                                 for blue in arange()])
        return cube

    @classmethod
    def from_Identity(cls, infn = None, input_entry_count=32, output_depth=14, interpolator=None):
        return cls.from_cube(cls.identity(input_entry_count),output_depth)

    @classmethod
    def from_2D(cls, infn, input_entry_count=32, output_depth=14, interpolator=None):
        return cls.from_cube(ParserBMP(infn).raw_cube,output_depth)

    def to_2D(self,outf,*args,**kwargs):
        ParserBMP.write_cube(self.array,outf)

    @classmethod
    def compound(cls,cube0,cube1,interpolator = TetrahedralInterpolator):
        ip = interpolator(cube1)
        return np.array([[[ip.interpolate(red) for red in green] for green in blue] for blue in cube0])

    def convert_target(self,outfn=None):
        outfn = Path(outfn)
        if outfn.suffix.upper() == ".PNG":
            self.to_2D(outfn)
        elif outfn.suffix.upper() == ".BMP":
            self.to_2D(outfn)
        elif outfn.suffix.upper() == ".3DL":
            self.to_3DL(outfn)
        else:
            print("NO MATCH "+outfn.suffix.upper())

    @classmethod
    def convert(cls,infn,outfn = None):
        infP = Path(infn)
        if str(infP).lower() == "idem":
            if outfn is None:
                print("IDEM Requires Output Path")
            cls.from_cube(cls.identity()).convert_target(outfn)
            return
        if outfn is None:
            outfn = infP.with_suffix(".3dl")
        outfn = Path(outfn)
        if infP.suffix.upper() == ".PNG":
            cls.from_2D(infn).to_TEX(outfn.with_suffix(".tex"))
        elif infP.suffix.upper() == ".BMP":
            cls.from_2D(infn).to_TEX(outfn.with_suffix(".tex"))
        elif infP.suffix.upper() == ".CUBE":
            cls.from_AdobeCube(infn).to_TEX(outfn.with_suffix(".tex"))
        elif infP.suffix.upper() == ".3DL":
            cls.from_3DL(infn).to_TEX(outfn.with_suffix(".tex"))
        elif infP.suffix.upper() == ".TEX":
            cls.parse(infn).convert_target(outfn)
        else:
            print("NO MATCH"+infP.suffix.upper())

    @classmethod
    def stack(cls,outfn,*args):
        stack = []
        for filename in args:
            filename = Path(filename)
            cube = None
            if filename.suffix.upper() == ".PNG":
                cube = ParserBMP(filename).raw_cube
            if filename.suffix.upper() == ".BMP":
                cube = ParserBMP(filename).raw_cube
            if filename.suffix.upper() == ".CUBE":
                cube = ParserCUBE(filename).raw_cube
            if filename.suffix.upper() == ".3DL":
                cube = Parser3DL(filename).raw_cube
            if filename.suffix.upper() == ".TEX":
                cube = cls.parse(filename).array
            if str(filename).lower() == "idem":
                cube = cls.identity()
            if cube is None:
                raise ValueError(str(filename) + " is not a recognized LUT Format")
            stack.append(cube)
        base = stack[0]
        for layer in stack:
            base = cls.compound(base,layer)
        cls.from_cube(base).to_TEX(outfn)