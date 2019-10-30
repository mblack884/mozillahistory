from glob import glob
import os
import fnmatch
import shutil

'''
This script searches recursively through all the unpacked source code archive directories,
identifying all files that were written using C or C++. 

In addition to copying the files over into a working directory, it flattens the directory
structure by replacing all forward slashes in the source path to dashes in the destination
path. These overly long filenames should be unique; however, there is an interactive prompt
that will pause filtering if duplicates filename are created via substitution.
'''

rawDir = 'raw/'
cleanDir = 'stage0/'

def findSource(target,duplicate=True,debug=False):
    '''
    A simple set of loops using os.walk to filter for C/C++ source code files.  Currently ignores headers.  Automatically checks for duplicate filenames.
    '''
    ## Locate all c, cp, or cpp files
    filelist = list()
    for root, dirs, files in os.walk(target):
        for filename in fnmatch.filter(files,'*,c'):
            filelist.append(os.path.join(root,filename))
        for filename in fnmatch.filter(files,'*.cp'):
            filelist.append(os.path.join(root,filename))
        for filename in fnmatch.filter(files,'*.cpp'):
            filelist.append(os.path.join(root,filename))
    
    ## Check for duplicate filenames in target directory (unless False passed in at call)
    if duplicate:
        checkset = set(filelist)
        if len(checkset) != len(filelist):
            print(str(len(filelist) - len(checkset))," duplicate filenames discovered in ",target + '.')
            x = input('Continue? (y/n): ')
            while x.lower() != 'y' or x.lower() != 'n':
                x = input('Invalid response. Please enter again: ')
            if x.lower() == 'n':
                quit('Terminating process.')
                
    return filelist

def newName (oldPath,oldDir):
    name = oldPath.replace(oldDir,'')
    name = name[name.find('/')+1:]
    return '/' + name.replace('/','-')
    

## Move to clean folder

for version in glob(rawDir + '*'):
    print('Preparing files for Version ' + version.replace(rawDir,''))
    codeFiles = findSource(version)
    targetDir = version.replace(rawDir,cleanDir)
    if os.path.exists(targetDir):
        print('Old directory found. Removing.')
        shutil.rmtree(targetDir)
    if not os.path.exists(targetDir):
        print('Directory created.')
        os.mkdir(targetDir)
    print('Copying files.')
    for filename in codeFiles:
        ##shutil.copy(filename,targetDir) Old naming schema, allows for duplicate filenames
        shutil.copy(filename,targetDir + newName(filename,rawDir))
    print('Complete.\n')
    
    