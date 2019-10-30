'''
This script uses the results of the topic model to produce a virtual vector space by
cumulatively summing the delta-add and delta-delete vectors for each version of each document
in the corpus. 

This script also addresses the possibility that DiffLDA may result in "negative" topic 
membership as outlined in Thomas et al. (2011). There is a possibility that the fuzziness of Bayesian probability will mean that a virtual document could have less than 0 tokens in it or
that a virtual version could have less than 0 tokens assigned to a topic. As I explain in my
DHQ article, removing comments during preprocessing reduced this problem significantly, but I
opted to leave this normalization step in to address the minimal amount that remained.
'''

### Script handles one topic model at time. Provide the set label as 'vectorName'
dataDir = 'vectors/'
vectorName = '50-mozilla-v8'
reset = {'00','07','37'}

addDict = dict()
delDict = dict()
order = list()

## Read in the delta-a vector and store values as integers
with open(dataDir + vectorName + '-raw-a.csv',mode='r') as file:
    matrix = file.readlines()
    
for row in matrix:
    vector = row.rstrip().split(',')
    version = vector[0]
    order.append(version)
    addDict[version] = list()
    intVector = list()
    for value in vector[1:]:
        addDict[version].append(int(value))

## Read in delta-d vector and store values as integers
with open(dataDir + vectorName + '-raw-d.csv',mode='r') as file:
    matrix = file.readlines()
    
for row in matrix:
    vector = row.rstrip().split(',')
    version = vector[0]
    delDict[version] = list()
    for value in vector[1:]:
        delDict[version].append(int(value))
        
## Convert delta vectors to token counts per topic cumulatively
sumDict = dict()
totalDict = dict()
for idx,version in enumerate(order):
    
    ## This check handles the cumulative summing.  When the code-base is re-written, the cumulative totals should be reset to 0.
    if version in reset:
        sumDict[version] = [0] * len(addDict[version])
    else:
        sumDict[version] = sumDict[order[idx-1]].copy()
    
    ## Apply the delta-a and delta-a token memberships for each topic, correcting negative values
    for idx,addValue in enumerate(addDict[version]):
        sumDict[version][idx] += addValue - delDict[version][idx]
        ## Normalization: if below 0, then set to 0
        if sumDict[version][idx] < 0:
            sumDict[version][idx] = 0
    
    ## Calculate total size of each version using the adjusted token counts (using the adjusted totals rather than calculating from original delta sums)
    totalDict[version] = 0
    for tokens in sumDict[version]:
        totalDict[version] += tokens
        
memberships = dict()
for version in order:
    memberships[version] = list()
    for tokens in sumDict[version]:
        memberships[version].append(float(tokens/totalDict[version]))
        
with open(dataDir + 'normalized/' + vectorName + '-percent.csv',mode='w') as file:
    for version in order:
        file.write(version)
        for value in memberships[version]:
            file.write(',' + str(value))
        file.write('\n')
        
with open(dataDir + 'normalized/' + vectorName + '-counts.csv',mode='w') as file:
    for version in order:
        file.write(version)
        for value in sumDict[version]:
            file.write(',' + str(value))
        file.write('\n')