from nltk.stem.snowball import PorterStemmer
from glob import glob
import re

'''
Software preprocessor library that makes the following changes to C++ source files:
- Removes comments and empty lines
- Tokenizes documents by removing all non-alphabetic characters
- Stopword filtering (see note below)
- Options to split or preserve compound names created via camel-case or underscores
- Stems all tokens so that topic keyword lists are not full of variations of the same word

The 'doPrep' function will process all files in a directory.

For the Mozilla study, I've used three different sets of stopwords. There is a - natural language stopswords (naturalStop)
- common cpp stopwords used by Thomas, et. al. (importStop)
- additional cpp stopwords hardcoded into the script (cppStop)
'''
naturalStop = set()
importStop = set()
cppStop = {'include','define','ifndef','ifdef','if','else','endif','class','public','private','virtual','inline','return','const','int','float','long','double','bool','char','void','if','else','for','do','while','true','false','null','include','priv','string','define','static_cast','static','var','set','case','switch','endif','remove','copy','continue','cout','endl','abort','static_constructor','str','struct','new','delete','find','ignore','init','obj','object','error','type','nsnull','ptr','data','result','add','valu','context','nsresult','size','list','ref','index','count','state','info','fail','value','values','print','name','out','end','start','assert','default','break'}

def trimLines(rawLines):
	'''
	This function removes empty lines and prepares lines for tokenization by stripping out comment syntax and removing function markers.
	
	While comments are potentially useful, the majority of them are repeated
	license language. This repetition distorted the topic model, producing results
	wherein several of the topic key lists were comprised solely of tokens taken
	from the license statements. 
	'''
	trimmedLines = list()
	for line in rawLines:
		## If line is part of library inclusions, skip.
		if line.find('#include') > -1:
			continue
		## Skip comments!
		if line.find('/*') > -1:
			continue
		if line.find('*/') > -1:
			continue
		if line[:2] == ' *':
			continue
		if line[:2] == '//':
			continue
		line = line.replace('//','') 
		
		## Add only non-empty lines to the corrected set
		if len(line) > 1:
			trimmedLines.append(line)
			
	return trimmedLines

def trimTokens(trimmedLines,stopWords,splitCamel=True,splitUnders=True,doStem=True):
	'''
	This function breaks each line into tokens by removing operators & other syntactical markers. Camel-case and underscore compounding are also split during this step, if enabled.
	
	After character filtering, any token not considered a stop word is returned in a list.
	'''
	possibleTokens = list()
	
	for line in trimmedLines:
		## Optionally split camel-cased method/variable names
		if splitCamel:
			roughTokens = camelSplit(line)
		else:
			roughTokens = line
		
		## Remove all non-alphabetic characters, optionally preserving underscores
		if splitUnders:
			search = re.compile('[^\w ]')
		else:
			search = re.compile('[^\w_ ]')
		roughTokens = search.sub(' ',roughTokens)
				
		## Remove any extra space between tokens produced thorugh previous step
		while '  ' in roughTokens:
			roughTokens = roughTokens.replace('  ',' ')
				
		for fragment in roughTokens.split():
			## Skip any stop words, any operators, and any hard-coded value initializations
			if fragment.lower() in stopWords or len(fragment) < 3:
				continue

			## Any surviving strings are probably tokens.  Add them in order.
			if doStem:
				possibleTokens.append(stem(fragment))
			else:
				possibleTokens.append(fragment)

			if doStem:
				return stemmer(possibleTokens)
			else:
				return possibleTokens

def camelSplit(line):
	'''
	Recursive camel-case split function. 
	'''
	## If the entire line is in lowercase, then just return as is.
	if line.islower():
		return line
	
	for idx,char in enumerate(line):
		## If the only uppercase character appears at the end of the line, then it doesn't fit the definition of camel-case. Lowercase it and return.
		if not idx < len(line) - 1:
			return line.lower()
		
		'''
		If the character at current index is lowercase and the next is uppercase, insert a space between the two characters. 
				
		Because the function is recursive, it will perform the same operation, adding spaces to	the existing line, until no uppercase characters around found text is found.
		'''
		elif line[idx].islower() and line[idx+1].isupper():
			newline = line[:idx+1] + ' ' + line[idx+1:]
			camel = line[idx+1]
			return camelSplit(newline.replace(camel,camel.lower(),1))

def stemmer(tokens):
	'''
	Simple stemming loop for general use throughout project. Will stem all tokens in a list.
	'''
	ps = PorterStemmer()
	stemmed = list()
	for t in tokens:
		stemmed.append(ps.stem(t))
	return stemmed

def doprep(srcDir,dataDir,splitCamel=True,splitUnders=True,doStem=True):
	'''
	The project's primary source code preprocessor loop.  Pass in the directory of files to process, a destination directory, and specify whether to split according to camel case and underscores.
	'''

	## Read in list of common English stops from web
	with open('common-english-words.txt',mode='r') as file:
		raw = file.read()
		words = raw.split(',')
		for x in words:
			naturalStop.add(x)
			
	## Read in list of common Source Code stops from SWT's script
	with open('common-cpp-words.txt',mode='r') as file:
		raw = file.read()
		words = raw.split(',')
		for x in words:
			importStop.add(x)

	## Combine the two lists of stop words together into a single set for easier parsing
	stopWords = set()
	stopWords.update(naturalStop)
	stopWords.update(cppStop)
	stopWords.update(importStop)

	filelist = glob(srcDir + '*.c*')
	print(str(len(filelist)) + ' files found.  Beginning pre-processing.')

	for idx,target in enumerate(filelist):
		print('Processing ' + target)

		with open(target,mode='r') as file:
			rawLines = file.readlines()

		trimmedLines = trimLines(rawLines)

		tokens = trimTokens(trimmedLines,stopWords,splitCamel,splitUnders,doStem)

		'''
		NOTE: To prevent filenames from influencing the topic model, each file is assigned an arbitrary serial number. The only parts of a filename that matter from this point forward as the version number and the delta-add/delta-delete pre-pend codes.
		
		If you want to preserve filenames for other projects where they will still matter, use:
		outfile = target.replace(srcDr,dataDir)
		outfile = outfile[outfile.find('.'):] + '.txt'
		'''
		
		outfile = target.replace(srcDir,'')
		outfile = dataDir + outfile[:5] + str(idx) + '.txt'

		print(outfile)

		with open(outfile,mode='w') as file:
			for idx,x in enumerate(tokens):
				if idx == 0:
					file.write(x)
				else:
					file.write(' ' + x)