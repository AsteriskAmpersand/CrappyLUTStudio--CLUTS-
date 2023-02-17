# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 20:13:16 2023

@author: Asterisk
"""
import numpy as np
from Interpolator import TetrahedralInterpolator

def peek_line(f):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    if not line.replace(" ","").replace("\t","").replace("\r","").replace("\n",""):
        return ""
    return line

def reorderCube(c):
    return c.swapaxes(0,2)


class Parser3DL():
    def __init__(self,fpath = None):
        self.cube = None
        self.input_depth = 4
        self.output_depth = 12
        if fpath is not None:
            self._parse(fpath)

    @property
    def input_entry_count(self):
        return 2**self.input_depth + 1

    @property
    def normalizer(self):
        return 2**self.output_depth - 1

    @property
    def raw_cube(self):
        return self.cube

    def _parse(parser,filename):
        with open(filename,'r') as infile:
            while("#" in peek_line(infile) or not peek_line(infile)):
                infile.readline()
            if ("3DMESH" in peek_line(infile).upper()):
                infile.readline()
                mesh, inputdepth, outputdepth = infile.readline().split(" ")
                parser.input_depth = int(inputdepth)
                parser.output_depth = int(outputdepth)
                infile.readline()
                while("#" in peek_line(infile) or not peek_line(infile)):
                    infile.readline()
            else:
                infile.readline()
            def readln():
                while("#" in peek_line(infile) or not peek_line(infile)):
                    infile.readline()
                r, g, b = map(int, infile.readline().replace("\t", " ").split(" "))
                r, g, b = r/parser.normalizer, g/parser.normalizer, b/parser.normalizer
                return r, g, b

            def e_count(): return range(parser.input_entry_count)
            parser.cube = reorderCube(np.array([[[readln() for i in e_count()]
                            for j in e_count()] for k in e_count()]))
        return parser

    @classmethod
    def parse(cls, infile):
        parser = cls()
        return parser._parse(infile)

    def load_cube(self, cube, interpolator = None):
        d,h,w,ch = cube.shape
        if d != h or h != w or w != self.input_entry_count:
            if interpolator is None:
                interpolator = TetrahedralInterpolator
            cube = interpolator(cube).generate_cube(self.input_entry_count)
        self.cube = cube

    def cube_bounds(self):
        pure_depth = 2**self.input_depth
        return ' '.join([str(int(np.floor(i * 1024/pure_depth)))
                         for i in range(pure_depth)])+" 1023"

    def write_entry(self, entry):
        rgb = tuple(
            int(np.round(self.normalizer * entry[i])) for i in range(3))
        return "%d %d %d" % rgb

    def write_cube(self):
        result = ""
        def writeln(x):
            nonlocal result
            result += x+"\n"
        writeln("#Tokens required by applications - do not edit")
        writeln("")
        writeln("3DMESH")
        writeln("Mesh %d %d"%( self.input_depth, self.output_depth))
        writeln(self.cube_bounds())
        writeln("")
        for red in reorderCube(self.cube):
            for green in red:
                for blue in green:
                    writeln(self.write_entry(blue))
        writeln("")
        writeln("#Tokens required by applications - do not edit")
        writeln("")
        writeln("LUT8")
        writeln("gamma 1.0")
        return result