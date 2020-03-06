import glob
import sys
import os

def gitPush(description=""):
    push = input('should we push to the git repo first? [Y/n]')
    if ((push == 'Y') or (push == 'y')):
        pwd = os.getcwd() # where am I?
        os.chdir('/mnt/home/mrenzo/Templates/ppisn/')
        os.system('git add . && git commit -am \'about to start a run:'+description+'\' && git push')
        os.chdir(pwd) # go back to previous folder

def checkFolder(folder):
    # checks if folder exists, if not, it creates it, and returns its content
    found=glob.glob(folder)
    if found:
        print("Found folder:", folder)
        content = glob.glob(folder+'/*')
        return content
    if not found:
        os.system("mkdir -p "+str(folder))
        return glob.glob(folder+'/*') ## will be empty
        
def MoveIntoFolder(folder, description=""):
    content = checkFolder(folder)
    if content:
        os.chdir(folder)
        os.system('pwd')
        return 0
    else:
        print("content:", content)
        mkfolder=input(str(folder)+" is not empty. Proceed? [Y/n]")
        if ((mkfolder == 'Y') or (mkfolder == 'y')):
            os.chdir(folder)
            os.system("echo "+description+" > run_description.txt")
            print("******************")
            print(description)
            print("******************")
            return 0
        else:
            print("Ok, fix it yourself!Bye!")
            return 1     



    
