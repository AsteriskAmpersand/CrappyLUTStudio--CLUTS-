# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:40:36 2023

@author: Asterisk
"""


default = r"D:\Games SSD\MHW\chunk\light\LUT\CC_globalbase_stage_LUTM.tex"
photo_filters = ['C:/Users/Asterisk/Downloads/Rec709_Kodak_2393_D65.cube',
                'C:/Users/Asterisk/Downloads/Rec709_Kodak_2383_D65.cube',
                'C:/Users/Asterisk/Downloads/Rec709_Fujifilm_3510_D65.cube']
photoshop_filters = [
    *Path(r"C:\Program Files\Adobe\Adobe Photoshop CS6 (64 Bit)\Presets\3DLUTs").rglob("*.3dl"),
    *Path(r"C:\Program Files\Adobe\Adobe Photoshop CS6 (64 Bit)\Presets\3DLUTs").rglob("*.cube")]

raise
for filt in photo_filters + photoshop_filters:
    print(filt)
    filt = Path(filt)
    npath = Path(r"C:/Users/Asterisk/Downloads")/(filt.stem + '_compound.tex')
    LUT_Tex.stack(npath,default,filt)
    npath = Path(r"C:/Users/Asterisk/Downloads")/(filt.stem + '_bare.tex')
    LUT_Tex.convert(filt,npath)

#default = CC_globalbase_stage_LUTM
"""
from Interpolator import TrilinearInterpolator

h = LUT_Tex.parse(str(r'C:/Users/Asterisk/Downloads/Corrector.tex'))
arr = h.cube
ip = TrilinearInterpolator(arr)
res = 512
k = 0
upscaled = ip.generate_slice(res)
plt.imshow(upscaled, origin='lower')  # [0]
plt.show()


ip = PyramidalInterpolator(arr)
res = 512
k = 0
upscaled = ip.generate_slice(res)
plt.imshow(upscaled, origin='lower')  # [0]
plt.show()

h.to_3DL(str(r'C:/Users/Asterisk/Downloads/Corrector.3DL'))

inputsdl = "moonlight"
w = LUT_Tex.from_3DL(r'C:\Program Files\Adobe\Adobe Photoshop CS6 (64 Bit)\Presets\3DLUTs\%s.3dl'%inputsdl)
plt.imshow(w.array[0],origin='lower')
plt.show()
sdl = r'C:/Users/Asterisk/Downloads/%s.tex'%inputsdl
w.to_TEX(sdl)

m = LUT_Tex.parse(sdl)
plt.imshow(m.array[0],origin='lower')
plt.show()
m.to_3DL(r'C:/Users/Asterisk/Downloads/%s.3DL'%inputsdl)

w = LUT_Tex.from_3DL(r'C:/Users/Asterisk/Downloads/%s.3DL'%inputsdl)
plt.imshow(w.array[0],origin='lower')
plt.show()

inputsdl = "Candlelight"
w = LUT_Tex.from_AdobeCube(r'C:\Program Files\Adobe\Adobe Photoshop CS6 (64 Bit)\Presets\3DLUTs\%s.CUBE'%inputsdl)
plt.imshow(w.array[0],origin='lower')
plt.imshow(w.array[-1],origin='lower')
plt.show()
sdl = r'C:/Users/Asterisk/Downloads/%s.tex'%inputsdl
w.to_TEX(sdl)

m = LUT_Tex.parse(sdl)
plt.imshow(m.array[0],origin='lower')
plt.show()
m.to_3DL(r'C:/Users/Asterisk/Downloads/%s.3DL'%inputsdl)

inputsdl = "Identity"
w = LUT_Tex.from_Identity()
plt.imshow(w.array[0],origin='lower')
plt.imshow(w.array[-1],origin='lower')
plt.show()
sdl = r'C:/Users/Asterisk/Downloads/%s.tex'%inputsdl
w.to_TEX(sdl)

'C:/Users/Asterisk/Downloads/Rec709_Kodak_2393_D65.cube'
'C:/Users/Asterisk/Downloads/Rec709_Kodak_2383_D65.cube'
'C:/Users/Asterisk/Downloads/Rec709_Fujifilm_3510_D65.cube'

for lut in Path(r"D:\Games SSD\MHW\chunk\light\LUT").rglob("*.tex"):
    print(lut.stem)
    h = LUT_Tex.parse(str(lut))
    plt.imshow(h.array[0],origin='lower')
    plt.title(lut.stem + " Blue Min")
    plt.imshow(h.array[-1],origin='lower')
    plt.title(lut.stem + " Blue Max")
    plt.show()
"""
# plt.imshow(arr[31])
# plt.show()

# for k in range(h.header.depth):
#    for j in range(h.header.width):
#        for i in range(h.header.height):
#            h.pixelData[0][0].data[k][j][i] = [colorstep*i,colorstep*j,colorstep*k,alpha]

# Header.build_file(h,r'C:\Users\Asterisk\Downloads\flat.tex')