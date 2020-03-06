## This is a library to analyze output data from COSMIC simulations
import numpy as np

def isNSBHWD(array):
    # array is a kstar_* array of stellar types
    # assumes the stellar types from Hurley 2000
    array = np.array(array,dtype=int)
    return ((array >=10) & (array != 15))


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
