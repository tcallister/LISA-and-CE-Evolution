## author: Mathieu Renzo

## Author: Mathieu Renzo <mathren90@gmail.com>
## Keywords: files

## Copyright (C) 2019-2020 Mathieu Renzo

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or (at
## your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see http://www.gnu.org/licenses/.


# import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
# sys.path.insert(0, '/scratch/mathieu/MMPS/SCRIPTS_dirty')
import glob
import time
import math
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, FuncFormatter, MaxNLocator
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
# from File_reader import reader
from termcolor import colored
# parallelization stuff
from joblib import Parallel, delayed
import multiprocessing
import subprocess
sys.path.insert(0, '/mnt/home/mrenzo/codes/python_stuff/')
import mesaPlot as mp
mmm=mp.MESA()
ppp=mp.plot()

## define some colors ----------------------------------------------------------------------

Yellow = "#DDDD77"
Green = "#88CCAA"
Blue = "#77AADD"

## constants -------------------------------------------------------------------------------
global secyer
secyer = 3.1558149984e7
global Lsun
Lsun = 3.8418e33
global Msun
Msun = 1.9892e33
global Rsun_cm
Rsun_cm = 6.9598e10 # in cm
global G_cgs
G_cgs = 6.67428e-8 # in cgs

## load files -------------------------------------------------------------------------------


def reader(myfile, ncols, nhead):
    """ This example shows how to read a large regular ascii file (consisting of ncolumns), store it in binary format.
	This provides a great spead up when reading larger files created with binary_c or MESA or whateve
	SdM  March 12, 2015	
    """

    """15.04.2016 Mathieu: modified to fit my needs for binary_c Runaway project"""

    #The new binary file will be stored with the same name but with the extention.npy
    mybinfile = str(myfile[:-4])+".npy"
    # Just for fun... time the routine
    start_time = time.time()
    if (not os.path.isfile(mybinfile)): # Check if .databin exists already... 
        print("...    reading ascci file ", myfile)
        print("...    and storing it for you in binary format")
        print("...    patience please, next time will be way faster ")
        print("...    I promise")
        # If binary does not exist, read the original ascii file:
        if (not os.path.isfile(myfile)):
            print("File does not exist ", myfile)
            return
        # Read the first "ncol" columns of the file after skipping "nhead" lines, store in a numpy.array
        data = np.genfromtxt(myfile, skip_header=nhead)#, usecols=range(ncols))
        # Save the numpy array to file in binary format
        np.save(mybinfile, data)
        # print "...    That took ", time.time() - start_time, "second"
    else:
        # print "... Great Binary file exists, reading data directly from ", mybinfile
        # If binary file exists load it directly. 
        data = np.load(mybinfile)
        # print "   That took ", time.time() - start_time, "second"
    return data


def scrub(file):
    print("... let me scrub this for you")
    os.system('python log_scrubber.py '+file)
    print("... done cleaning", file)



def getSrcCol(file, clean=True, convert=True):
    # TODO: maybe one day I'll update this to be a pandas dataframe
    # should work both for history and profiles
    # read header
    P = open(file)
    for i, line in enumerate(P):
        if i==5:
            col = line.split()
            break
    P.close()
    # check if binary exists
    mybinfile = str(file[:-4])+".npy"
    if (os.path.isfile(mybinfile)):
        # read the column and binary
        src = reader(file, len(col), 6)
        return src, col
    else: # binary file does not exist
        print("... Binary file does not yet exist")
        if clean:
            scrub(file)
        if convert:
            src = reader(file, len(col), 6)
            return src, col
        else:
            src = np.genfromtxt(file, skip_header=6)
            return src, col

## plotting useful things ---------------------------------------------------------------------

def make2Dmap(x, y, z, x1=0, x2=1, y1=0, y2=1, res=20):
    minx = min(min(x),x1)
    maxx = min(max(x),x2)
    miny = min(min(y),y1)
    maxy = min(max(y),y2)

    x_int = np.linspace(minx,maxx,res)
    y_int = np.linspace(miny,maxy,res)

    mat = np.zeros([len(x_int),len(y_int)])
    for i in range(0,len(x_int)-1):
        for j in range(0,len(y_int)-1):
            mat[j,i] = np.sum(z[(x>=x_int[i])*(x<x_int[i+1])*(y>=y_int[j])*(y<y_int[j+1])])
    return x_int, y_int, mat


def writePreliminary(ax):
    ax.text(0.5,0.5,r"{\bf PRELIMINARY}", color="#808080",
            alpha=0.4, fontsize=74,ha='center', va='center', rotation=45, transform=ax.transAxes)



def my_mark_inset(parent_axes, inset_axes, loc1a=1, loc1b=1, loc2a=2, loc2b=2, **kwargs):
    from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector
    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)

    pp = BboxPatch(rect, fill=False, **kwargs)
    parent_axes.add_patch(pp)

    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1a, loc2=loc1b, **kwargs)
    inset_axes.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2a, loc2=loc2b, **kwargs)
    inset_axes.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2


## miscellanea ---------------------------------------------------------------------------------------------

def max_array(a,b):
    # given two arrays of the same length
    # returns an array containing the max in each element
    if len(a)==len(b):
        c = np.zeros(len(a))
        for i in range(len(a)):
            c[i]=max(a[i],b[i])
        return c
    else:
        print("you gave me two array of lengths:",len(a),"=/=",len(b))
        print(colored("can't work with this...going home!","red"))

def min_array(a,b):
    # given two arrays of the same length
    # returns an array containing the max in each element
    if len(a)==len(b):
        c = np.zeros(len(a))
        for i in range(len(a)):
            c[i]=min(a[i],b[i])
        return c
    else:
        print("you gave me two array of lengths:",len(a),"=/=",len(b))
        print(colored("can't work with this...going home!","red"))

def SB_law(r,t):
    # given radius and temperature in solar radii and kelvin, returns the luminosity in solar units
    sigma  = 5.67051e-5 #cgs units
    Rsun = 6.99e10 #cm
    Lsun = 4e33 #erg/s
    r *= Rsun #convert to cm
    l = 4*math.pi*sigma*t**4*r**2
    l = l/Lsun
    return l

def tail(f, n): 
    #read the last n lines of f (modified from somewhere on the internet) 
    n=str(n)
    p = subprocess.Popen(["tail","-n",n, f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    lines = stdout.splitlines()
    return lines

def getTerminationCode(outfile):
    # assumes outfile is written in utf-8 encoding
    termcode = "dunno"
    end = tail(outfile, 50)
    # print(type(end))
    # print(end[::-1])
    for l in end[::-1]:
        # print(l)
        if "termination code" in str(l):
            # print(l)
            l = l.decode("utf-8") 
            termcode = l.split(":")[-1].rstrip().lstrip()
            break
        if "post RLOF found" in str(l):
            termcode = "post_RLOF"
    return termcode

def binarySortM1(folder):
    M1 = float(folder.split('M1_')[-1].split('M2_')[0])
    return M1
