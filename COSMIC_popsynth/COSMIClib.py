## This is a library to analyze output data from COSMIC simulations
import numpy as np

def isNSBHWD(array):
    # array is a kstar_* array of stellar types
    # assumes the stellar types from Hurley 2000
    array = np.array(array,dtype=int)
    return ((array >=10) & (array != 15))

def bothWD(array1, array2):
    # array* is a kstar_* array of stellar types
    # assumes the stellar types from Hurley 2000
    array1 = np.array(array1,dtype=int)
    array2 = np.array(array2,dtype=int)
    return(((array1[:] >= 10) & (array1[:] <13)) & ((array2[:] >= 10) & (array2[:] <13)))

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


def getGWemittingM(bpp, index):
    """
    Returns the mass emitting GWs from a cosmic bpp file, considering only the elements
    for which index == True. The stellar types kstar_* are according to Hurley et al. 2000
    """
    k1 = bpp.loc[index].kstar_1
    k2 = bpp.loc[index].kstar_2
    Mcore1 = bpp.loc[index].massc_1
    Mcore2 = bpp.loc[index].massc_2
    M1 = bpp.loc[index].mass_1
    M2 = bpp.loc[index].mass_2
    Mgw = np.zeros(len(M1)) # to be filled
    # print(len(k1),len(k2), len(Mcore1), len(Mcore2), len(M1), len(M2), len(Mgw))
    # if both MS
    ibothMS = (k1 <= 1) & (k2 <=1)
    Mgw[ibothMS] = M1[ibothMS]+M2[ibothMS]
    notbothMS = np.array(1-ibothMS, dtype=bool)
    # consider CE where both stars are non-degenerate
    inondeg = (k1<10) & (k2<10) & notbothMS
    # donor 1
    idonor1 = inondeg & (k1-k2 > 0) #NB strictly >
    Mgw[idonor1] = Mcore1[idonor1]+M2[idonor1]
    # double core
    idc = inondeg & (k1-k2 == 0)
    Mgw[idc] = Mcore1[idc]+Mcore2[idc]
    # donor 2
    idonor2 = inondeg & (k1-k2 < 0)
    Mgw[idonor2] = Mcore2[idonor2]+M1[idonor2]
    # now deal with degenerate stars
    # 1 is degenerate but 2 isn't
    ideg1nondeg2 = (k1>=10)&(k2<10)
    Mgw[ideg1nondeg2] = Mcore2[ideg1nondeg2]+M1[ideg1nondeg2]
    # 2 degenerate but 1 not
    ideg2nondeg1 = (k1<10)&(k2>=10)
    Mgw[ideg2nondeg1] = Mcore1[ideg2nondeg1]+M2[ideg2nondeg1]
    # both degenerate -- should be rare
    ibothdeg = (k1>=10) & (k2>=10)
    Mgw[ibothdeg] = M1[ibothdeg]+M2[ibothdeg]
    ## sanity check:
    # all = np.array(idonor1,dtype=int)+np.array(idonor2,dtype=int)+np.array(idc,dtype=int)+np.array(ideg1nondeg2,dtype=int)+np.array(ideg2nondeg1,dtype=int)+np.array(ibothdeg,dtype=int)
    # print(min(all), max(all)) ## should both be 1
    #print(min(Mgw), max(Mgw))
    # Mgw = Mcore1 + M2
    return Mgw
