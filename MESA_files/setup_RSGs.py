#!/usr/local/bin/python

import sys
import os
import glob
import math
import numpy as np
from utilsLib import *

Masses = np.linspace(0.1,10.0,20)
print("Masses",Masses)
print("=================================")
# these will all become sys.argv if needed
TEMPLATE = 'LISA-and-CE-Evolution/MESA_files/RSG_template/'
ROOT = "RUNS/Radii_RSG_cores/"
DESTINATION="RESULTS/Radii_RSG_cores/"
RUNFILE=ROOT+'/runFile.txt'
print("template:",TEMPLATE)
print("root:",ROOT)
# print("destination:",DESTINATION)
go_on = input('should we go on? [Y/n]')


if (go_on == 'Y') or (go_on == 'y'):
    content = checkFolder(ROOT)
    if not content:
        go_on_root = "Y"
    else:
        print(str(ROOT), "is not empty")
        print(content)
        go_on_root = input("Go on anyways? [Y/y]")
        if (go_on_root != 'Y' and go_on_root != 'y'): sys.exit()
    content = checkFolder(DESTINATION)
    if not content:
        go_on_dest = "Y"
    else:
        print(str(DESTINATION), "is not empty")
        print(content)
        go_on_dest = input("Go on anyways? [Y/y]")
        if (go_on_dest != 'Y' and go_on_dest != 'y'): sys.exit()
    if (((go_on_root == 'Y') or (go_on_root == 'y')) and ((go_on_dest == 'Y') or (go_on_dest == 'y'))):
        description = input("push MESA file before run? If so give me a description, else type [N,n]:")
        if (description != 'N' and description != 'n'):
            os.system('git add LISA-and-CE-Evolution/MESA_files/*')
            os.system('git commit -am \''+str(description)+'\'')
            os.system('git pull -r && git push')
        # print(RUNFILE)
        F = open(RUNFILE,"a")
        headerline = "export OMP_NUM_THREADS=1 && export MESA_DIR=/mnt/home/mrenzo/codes/mesa/mesa_12115/mesa12115 && export MESASDK_ROOT=/mnt/home/mrenzo/codes/mesa/mesa_12115/mesasdk && source $MESASDK_ROOT/bin/mesasdk_init.sh"
        backline = " && ./clean && ./mk && ./rn 2>&1 | tee output ; tail -40 output | mail -s \" one model done\" mrenzo@flatironinstitute.org"+"\n"
        for M in Masses:
            M = round(M,1)
            folder_name = str(M)+"/"
            # --------------------------------------
            os.system('mkdir -p '+ROOT+'/'+folder_name)
            os.chdir(ROOT+'/'+folder_name)
            # # copy stuff
            copy = 'cp -fr '+TEMPLATE+'/* ./'
            os.system(copy)
            F.writelines(headerline+" && cd "+ROOT+'/'+folder_name+backline)
            # # modify the inlists
            os.system('perl -pi.back -e \'s/MASS/'+str(M)+'/g;\' inlist_project')
            os.chdir(ROOT)
        F.close()

print("Now go on rusty to run with sbatch")
