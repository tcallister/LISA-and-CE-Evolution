# author: Mathieu Renzo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.



# This is a library to analyze output data from COSMIC simulations
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
    for which index == True. index should be used to pass only CE systems to this function.
    The stellar types kstar_* are according to Hurley et al. 2000
    """
    k1 = bpp.loc[index].kstar_1
    k2 = bpp.loc[index].kstar_2
    Mcore1 = bpp.loc[index].massc_1
    Mcore2 = bpp.loc[index].massc_2
    M1 = bpp.loc[index].mass_1
    M2 = bpp.loc[index].mass_2
    Mgw = np.zeros(len(M1)) # to be filled
    # print(len(k1),len(k2), len(Mcore1), len(Mcore2), len(M1), len(M2), len(Mgw))
    # one non-MS and non-degenerate and the other MS or degenerate
    star1_nondeg_star2_ms = np.array(((k1>1) & (k1<10)) & ((k2 <=1) | (k2>=10)), dtype=bool)
    Mgw[star1_nondeg_star2_ms] = Mcore1[star1_nondeg_star2_ms]+M2[star1_nondeg_star2_ms]
    # other non-MS and non-degenerate and other MS or degenerate
    star2_nondeg_star1_ms = np.array(((k2>1) & (k2<10)) & ((k1 <=1)| (k1>=10)), dtype=bool)
    Mgw[star2_nondeg_star1_ms] = Mcore2[star2_nondeg_star1_ms]+M1[star2_nondeg_star1_ms]
    # both non-MS and non-deg
    bothnonMS = np.array(((k1>1) & (k1<10)) & ((k2>1) & (k2<10)), dtype=bool)
    Mgw[bothnonMS] = Mcore1[bothnonMS] + Mcore2[bothnonMS]
    # now deal with MS and degenerate stars
    # both MS or both compact
    bothMS_or_deg = np.array(((k1<=1) & (k2<=1)) | ((k1>10) & (k2>10)), dtype=bool)
    Mgw[bothMS_or_deg] = M1[bothMS_or_deg] + M2[bothMS_or_deg]
    # one MS other degenerate
    oneMS_other_deg = np.array((k1<=1) & (k2>10), dtype=bool)
    Mgw[oneMS_other_deg] = M1[oneMS_other_deg] + M2[oneMS_other_deg]
    # other MS one degenerate
    otherMS_one_deg = np.array((k2<=1) & (k1>10), dtype=bool)
    Mgw[otherMS_one_deg] = M1[otherMS_one_deg] + M2[otherMS_one_deg]
    ## sanity check:
    all = np.array(star1_nondeg_star2_ms,dtype=int)+np.array(star2_nondeg_star1_ms,dtype=int)+np.array(bothnonMS,dtype=int)+np.array(bothMS_or_deg,dtype=int)+np.array(oneMS_other_deg,dtype=int)+np.array(otherMS_one_deg,dtype=int)
    # print("1, 1?", min(all), max(all))
    #print(min(Mgw), max(Mgw))
    return Mgw
