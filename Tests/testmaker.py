# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 22:37:57 2023

@author: Asterisk
"""
import os
import shutil
from pathlib import Path
import subprocess
testroot = "D:/MHW Modding/Tools/LUTStudio/Tests/%s"
testMasterroot = "D:/MHW Modding/Tools/LUTStudio/Tests/Backup Cases/%s"
game0b = "CC_globalbase_LUTM.tex"
game1b = "CC_globalbase_stage_LUTM.tex"
test3dlb = "Moonlight.3DL"
testcubeb = "Candlelight.CUBE"
bases = list(map(lambda x: testroot%x,[game0b,game1b,test3dlb,testcubeb]))
game0,game1,test3dl,testcube = bases
masters = list(map(lambda x: testMasterroot%x,[game0b,game1b,test3dlb,testcubeb]))

test_runner = """runfile('D:/MHW Modding/Tools/LUTStudio/CrappyLUTStudio.py',
        wdir='D:/MHW Modding/Tools/LUTStudio',
        args = '%s')"""

def run(args):
    print(*args)
    process = subprocess.Popen(['python',"D:\MHW Modding\Tools\LUTStudio\CrappyLUTStudio.py",*args],
                     shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    out, err = process.communicate()
    print(out.decode("utf-8"))
    print(err.decode("utf-8"))
    errcode = process.returncode

def reset_tests():
    for file in bases:
        if (Path(file).exists()):
            os.remove(file)
    for master,file in zip(masters,bases):
        shutil.copy(master,file)

def check_clean_file(file):
    if Path(file).exists():
        os.remove(file)
    else:
        print("Failed to Convert ",file)
        print("ERROR IN TEST")
        raise

def check_clean(filenames):
    if type(filenames) is str:
        check_clean_file(filenames)
        return
    for file in filenames:
        check_clean_file(file)
    for file in Path(r"D:/MHW Modding/Tools/LUTStudio/Tests").glob("*"):
        if file.is_file() and file.suffix.upper() != ".PY":
            os.remove(file)
        reset_tests()
    print()
    print("="*25)
    print("="*25)

reset_tests()

print("Convert Tex (Default)")
args = [game0]
run(args)
check_clean(game0.replace(".tex",".3dl"))

print("Convert Tex with Output Name (PNG)")
args = game0 , "-o" , testroot%"tex_test.png"
run(args)
check_clean(testroot % "tex_test.png")

print("Convert Tex with Output Name (3DL)")
args = game0 , "-o" , testroot%"tex_test.3dl"
run(args)
check_clean(testroot % "tex_test.3dl")

print("Convert 3DL")
args = test3dl ,
run(args)
check_clean(test3dl.upper().replace(".3DL",".tex"))

print("Convert CUBE")
args = testcube ,
run(args)
check_clean(testcube.upper().replace(".CUBE",".tex"))

print("Convert List")
args = game0 , game1
run(args)
check_clean([game0.upper().replace(".TEX",".3dl"),
             game1.upper().replace(".TEX",".3dl")])

print("Convert Mixed List")
args = game0 , game1 , test3dl , testcube
run(args)
check_clean([game0.upper().replace(".TEX",".3dl"),
             game1.upper().replace(".CUBE",".3dl"),
             test3dl.upper().replace(".3DL",".tex"),
             testcube.upper().replace(".CUBE",".tex"),
             ])

print("Convert Mixed List with Output Name")
args = game0 , game1 , test3dl , testcube ,\
        "-o" , testroot%"CC_globalbase_LUTM.3dl"
run(args)
check_clean([game0.upper().replace(".TEX",".3dl"),
             game1.upper().replace(".CUBE",".3dl"),
             test3dl.upper().replace(".3DL",".tex"),
             testcube.upper().replace(".CUBE",".tex"),
             ])

print("Convert Stacked with Output Name")
args = game0 , game1 , test3dl , testcube ,\
        "-o" , testroot%"stack_test.tex"
run(args)
check_clean([testroot%"stack_test.tex"])

reset_tests()