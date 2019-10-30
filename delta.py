from shlex import split
from glob import glob
import os
import shutil
import subprocess

'''
Configuration variables

The reset list is used to mark versions in corpus where the code base was transitioned to a new application (Netscape -> Mozilla Suite -> Firefox)
'''

srcDir = 'stage0/'
deltaDir = 'stage1/'
debug = True
rootDir = os.getcwd() + '/'
reset = {'00','07','37'}

def findName(diffLine):
    '''
    Extremely simple slice function to locate a file name in diff output when reporting changes to a file
    E.g.: 'diff -w 0/BookmarkView.cpp 1/BookmarkView.cpp' will return 'BookmarkView.cpp'
    '''
    return diffLine[diffLine.rfind('/')+1:]

def prefix(label,filename):
    '''
    Accepts a filename and adds the passed in prefix to the beginning.  Handles locating end of directory name and slicing. Real purpose here is improve readability of code in the script's primary loop.
    '''
    index = filename.rfind('/')
    if index == -1:
        return label + filename
    else:
        return filename[:index+1] + label + filename[index+1:]

if debug:
    print('Changing to source directory ' + rootDir + srcDir)
os.chdir(srcDir)

## Batch process loop for version folders in srcDir
versionFolders = glob('*')
for idx,current in enumerate(versionFolders):

    '''
	Preparatory step for each iteration. Data structures need to be reset for each version. A subdirectory within the target directory must also be created for each version.
	'''
    print('\nProcessing version ' + current)
    additions = dict()
    deletions = dict()
    addDocs = list()
    delDocs = list()
    if not os.path.exists(rootDir + deltaDir + current):
        os.mkdir(rootDir + deltaDir + current)

    ## The first version of each application should be treated as nothing but additions.
    if current in reset:
        if debug:
            print('Treating base version ' + current + ' as exclusively additions')
        fileList = glob(current + '/*')
        for sourceFile in fileList:
            targetFile = rootDir + deltaDir + prefix(current + '-a-',sourceFile)
            shutil.copy(sourceFile,targetFile)
    
    ## For all subsequent versions, use diff to compare previous to current.
    else:
        previous = versionFolders[idx-1]
        if debug:
            print('Attempting diff command on ' + previous + ' and ' + current)
        
        ## The diff command with the results produced as a list of strings (one for each line of output)
        command = split('diff -w ' + previous + '/ ' + current + '/')
        diff = subprocess.Popen(command,stdout=subprocess.PIPE)
        results = str(diff.communicate()[0]).replace('\\t',' ').strip("'b").split('\\n')        

        ## This loop processes the diff results
        for line in results:
            if len(line) == 0:
                continue
            
            if line[:4] == 'diff':
                ## Identify the file being changed, prepare addition/deletion dictionaries
                changedFile = findName(line)
                additions[changedFile] = list()
                deletions[changedFile] = list()
                
            ## For both additions and deletions, track in order reported
            elif line[0] == '>':
                additions[changedFile].append(line[2:])        
            elif line[0] == '<':
                deletions[changedFile].append(line[2:])
        
            ## For whole document changes, determine whether the document has been added or removed and track in order reported
            elif line[:4] == 'Only':
                ## Index 0 and 1 can be discard. 2 will have version label (requires slice), 3 will have filename (no slice)
                parts = line.split()
                ## When slicing Index 2, version label will be all characters prior to '/'
                version = parts[2][:parts[2].find('/')]
                filename = parts[3]
                if version == previous:
                    delDocs.append(filename)
                elif version == current:
                    addDocs.append(filename)
                else:
                    quit('Error parsing file change: ' + line)
        
        ## Delta documents represent portions added or removed.  There are two sets of two, four loops.
        if debug:
            print('Diff command successful.  Writiing delta documents.')
        
        ## Write out delta-a for changes within documents
        for document in additions:
            targetFile = rootDir + deltaDir + current + '/' + prefix(current + '-a-',document)
            if debug:
                print('Writing ' + targetFile)
            with open(targetFile,mode='w',encoding='utf-8') as file:
                for change in additions[document]:
                    file.write(change + '\n')
        
        ## Write out delta-d for changes within documents
        for document in deletions:
            targetFile = rootDir + deltaDir + current + '/' + prefix(current + '-d-',document)
            if debug:
                print('Writing ' + targetFile)
                with open(targetFile,mode='w',encoding='utf-8') as file:
                    for change in deletions[document]:
                        file.write(change + '\n')
                        
        ## Write out delta-a for new documents not present in previous version
        for document in addDocs:
            if debug:
                print('New document: ' + document)
            targetFile = rootDir + deltaDir + current + '/' + prefix(current + '-a-',document)
            sourceFile = current + '/' + document
            shutil.copy(sourceFile,targetFile)
            
        ## Write out delta-d for documents removed from current version
        for document in delDocs:
            if debug:
                print('Removed document: ' + document)
            targetFile = rootDir + deltaDir + current + '/' + prefix(current + '-d-',document)
            sourceFile = previous + '/' + document
            shutil.copy(sourceFile,targetFile)