# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 08:39:37 2023

@author: Asterisk
"""
import numpy as np

# =============================================================================
# Matrix Constants
# =============================================================================
#Pyramidal

Pyr_C0 = [
[ 1, 0, 0, 0, 0, 0, 0, 0],
[ 0, 0, 0,-1, 0, 0, 0, 1],
[-1, 0, 1, 0, 0, 0, 0, 0],
[-1, 1, 0, 0, 0, 0, 0, 0],
[ 1,-1,-1, 1, 0, 0, 0, 0]
]

Pyr_C1 = [
[1,0,0,0,0,0,0,0],
[-1,0,0,0,1,0,0,0],
[0,0,0,0,0,-1,0,1],
[-1,1,0,0,0,0,0,0],
[1,-1,0,0,-1,1,0,0]
]

Pyr_C2 = [
[1,0,0,0,0,0,0,0],
[-1,0,0,0,1,0,0,0],
[-1,0,1,0,0,0,0,0],
[0,0,0,0,0,0,-1,1],
[1,0,-1,0,-1,0,1,0]
]

Pyr_C0,Pyr_C1,Pyr_C2 = map(np.array,(Pyr_C0,Pyr_C1,Pyr_C2))


Tet_T0 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[-1, 0, 0, 0, 1, 0, 0, 0],
[0, 0, 0, 0, -1, 0, 1, 0],
[0, 0, 0, 0, 0, 0, -1, 1]]

Tet_T1 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[-1, 0, 0, 0, 1, 0, 0, 0],
[0, 0, 0, 0, 0, -1, 0, 1],
[0, 0, 0, 0, -1, 1, 0, 0]]

Tet_T2 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[0, -1, 0, 0, 0, 1, 0, 0],
[0, 0, 0, 0, 0, -1, 0, 1],
[-1, 1, 0, 0, 0, 0, 0, 0]]

Tet_T3 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[0, 0, -1, 0, 0, 0, 1, 0],
[-1, 0, 1, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, -1, 1]]

Tet_T4 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, -1, 0, 0, 0, 1],
[-1, 0, 1, 0, 0, 0, 0, 0],
[0, 0, -1, 1, 0, 0, 0, 0]]

Tet_T5 = [
[1, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, -1, 0, 0, 0, 1],
[0, -1, 0, 1, 0, 0, 0, 0],
[-1, 1, 0, 0, 0, 0, 0, 0]]

Tet = list(map(np.array,[Tet_T0,Tet_T1,Tet_T2,Tet_T3,Tet_T4,Tet_T5]))


TRILINEAR = np.array([
[1,0,0,0,0,0,0,0],
[-1,0,0,0,1,0,0,0],
[-1,0,1,0,0,0,0,0],
[-1,1,0,0,0,0,0,0],
[1,0,-1,0,-1,0,1,0],
[1,-1,-1,1,0,0,0,0],
[1,-1,0,0,-1,1,0,0],
[-1,1,1,-1,1,-1,-1,1]
])

def regularize(vec):
    return vec
    return np.array([max(min(val,1),0) for val in vec])

# =============================================================================
# Matrices End
# =============================================================================

def deltas(r,g,b,w,h,d):
    r,g,b = max(0,min(r,1)),max(0,min(g,1)),max(0,min(b,1))
    ri,gi,bi = map(int,(min(np.floor(r*w),w-1), min(np.floor(g*h),h-1), min(np.floor(b*d),d-1)))
    delta = lambda f,vi,spc : f/spc-vi
    d_r = delta(r,ri,1/(w))
    d_g = delta(g,gi,1/(h))
    d_b = delta(b,bi,1/(d))
    return ri,gi,bi,d_r,d_g,d_b

def buildTable(lut,matrix):
    depth,width,height,channels = lut.shape
    vector_table = [[[None for i in range(height-1)] for j in range(width-1)] for k in range(depth-1)]
    for k in range(depth-1):
        for j in range(width-1):
            for i in range(height-1):
                vector = [0 for i in range(8)]
                vector[0] = lut[k]  [j]  [i]
                vector[1] = lut[k]  [j+1][i]
                vector[2] = lut[k]  [j]  [i+1]
                vector[3] = lut[k]  [j+1][i+1]
                vector[4] = lut[k+1][j]  [i]
                vector[5] = lut[k+1][j+1][i]
                vector[6] = lut[k+1][j]  [i+1]
                vector[7] = lut[k+1][j+1][i+1]
                vector = np.array(vector)
                vector_table[k][j][i] = (matrix @ vector)
    return vector_table

class Interpolator():
    def __init__(self,lut):
        self.lut = lut
        self.cache = self.build_precomputed(lut)
    def interpolate(self,target):
        return regularize(self._interpolate(target,self.cache))
    def generate_slice(self,entry_count,k=0):
        side_length = 1/(entry_count - 1)
        return np.array([[self.interpolate((i*side_length,j*side_length,k*side_length))
                    for i in range(entry_count)]
                      for j in range(entry_count)])
    def generate_cube(self,entry_count):
        side_length = 1/(entry_count - 1)
        return np.array([[[self.interpolate((i*side_length,j*side_length,k*side_length))
                    for i in range(entry_count)]
                      for j in range(entry_count)]
                         for k in range(entry_count)])

class PyramidalInterpolator(Interpolator):
    def build_precomputed(self,lut):
        p0 = buildTable(lut,Pyr_C0)
        p1 = buildTable(lut,Pyr_C1)
        p2 = buildTable(lut,Pyr_C2)
        return (lut.shape[:3]),p0,p1,p2

    def _interpolate(self,floatCo,pyrList):
        d,h,w = pyrList[0]
        d,h,w = d-1,h-1,w-1
        r,g,b = floatCo
        ri,gi,bi,d_r,d_g,d_b = deltas(r,g,b,w,h,d)
        if (d_r >= d_b and d_g >= d_b):
            ix = 0
        elif (d_b >= d_r and d_g >= d_r):
            ix = 1
        else:
            ix = 2

        prod = [d_r*d_g, d_g*d_b, d_b*d_r][ix]
        dp = np.array([1,d_b,d_r,d_g,prod])
        #print(r,ri,1/(w+1))
        #print(delta)
        C = pyrList[ix+1][bi][gi][ri]
        return dp @ C

class TetrahedralInterpolator(Interpolator):
    def build_precomputed(self,lut):
        return [lut.shape[:3]]+[buildTable(lut,T) for T in Tet]

    def _interpolate(self,floatCo,pyrList):
        d,h,w = pyrList[0]
        d,h,w = d-1,h-1,w-1
        r,g,b = floatCo
        ri,gi,bi,d_r,d_g,d_b = deltas(r,g,b,w,h,d)
        ix = -1
        if (d_b >= d_r >= d_g):
            ix = 0
        elif (d_b >= d_g >= d_r):
            ix = 1
        elif (d_g >= d_b >= d_r):
            ix = 2
        elif (d_r >= d_b >= d_g):
            ix = 3
        elif (d_r >= d_g >= d_b):
            ix = 4
        elif (d_g >= d_r >= d_b):
            ix = 5
        dp = np.array([1,d_b,d_r,d_g])
        #print(r,ri,1/(w+1))
        #print(delta)
        try:
            C = pyrList[ix+1][bi][gi][ri]
        except:
            print(ix,bi,gi,ri)
        return dp @ C

class TrilinearInterpolator(Interpolator):
    def build_precomputed(self,lut):
        return buildTable(lut,TRILINEAR)

    def _interpolate(self,floatCo,trilTable):
        d,h,w = len(trilTable),len(trilTable[0]),len(trilTable[0][0])
        r,g,b = floatCo
        ri,gi,bi,d_r,d_g,d_b = deltas(r,g,b,w,h,d)
        delta = np.array([1, d_b, d_r, d_g, d_b*d_r, d_r*d_g, d_g*d_b, d_r*d_g*d_b])
        #print(r,ri,1/(w+1))
        #print(delta)
        C = trilTable[bi][gi][ri]
        return delta @ C