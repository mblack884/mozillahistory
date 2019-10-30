Versioned Corpus Text-Processing Tools
======
These scripts were used to reproduce [Thomas et al (2011)'s DiffLDA methodology](https://dl.acm.org/citation.cfm?id=1985467) for the project described in ["A Textual History of Mozilla" (2015)](http://www.digitalhumanities.org/dhq/vol/9/3/000224/000224.html). For topic modeling, I used a custom interface for [MALLET](http://mallet.cs.umass.edu/) built in Java that allowed me to customize the model's output to support DiffLDA calculations. An updated and expanded version of this interface, called ICHASS-LDA, is available here.

Not included here are the experimental and exploratory scripts I wrote to refine and test stopword lists, search for project specific stopwords, or generate the graphs that I refer in the article. Those graphs were generated in R using ggplot2.

## Description of Workflow
These scripts were designed to maintain a record of data provenance by establishing a new copy of the corpus after each transformation. 
* **Raw data:** full source archives for each version under analysis
* **Stage 0:** extracted source files, renamed and organized into a flat directory structure
* **Stage 1:** source files transformed to delta-add and delta-remove files, shared code between versions is not carried forward
* **Stage 2:** non-alphabetical characters removed, camel-case and other compound constructions split, stop words filtered, and all remaining tokens stemmed
* **Topic modeling** performed on the delta-add and delta-remove files. Vector space model written to disk as token assigmments (sum of all tokens assigned to each topic in each document) rather than as topic membership (% of document tokens belonging to a topic, MALLET's default output)
* **Virtual Versions:** Vector space models for each version are produced by cumulatively summing the delta-add and delta-remove token assignment vectors associated with each version.

## Project Data
[Information about each of the software version analyzed by this project](http://www.digitalhumanities.org/dhq/vol/9/3/000224/000224.html#p14)

[Graphs of topic membership over time (model size: 60 topics)](http://www.mblack.us/moztm-data/index.html)

## Setup and Usage
The only dependency for the script is the [Natural Language Toolkit](https://www.nltk.org/index.html). NLTK is used by sourceprep.py to optionally stem tokens. I originally used a lighter weight, standalone Porter2 stemmer because NLTK did not support Python3 when I first worked on the project. I've updated the script to use NLTK's [Snowball Porter stemmer](https://www.nltk.org/api/nltk.stem.html?highlight=porter#nltk.stem.snowball.PorterStemmer) because the original utility is no longer maintained. 

These scripts assume that prior to usage you have established a local data repository that stores each version of the to-be-analyzed application in separate directories. These directories names should serve as version index numbers reflective of the release order of each version (e.g., 00, 01, 02, 03, etc.). For the Mozilla project, I had to organize this raw data by hand because Mozilla's archive was just a flat FTP directory, and the various tarballs it contained did have a consistent naming scheme across the 15 years I was studying. For future projects, I will be using a webscraper or an API-access script to automate raw data collection.

After data is organized in an acceptable subdirectory structure, run the scripts in the following order:

**filefilter.py:** This script will crawl the entirety of the local raw data repository, identifying and copying source code into a flat directory structure. To flatten, each file is renamed by changing all '/' in the local path to '-' and the version index number is prepended.

**delta.py:** This script begins the DiffLDA process. The script compares files in successive version pairs using the command line "diff" utility. The script parses the output of the diff command, writing out the additions and deletions to new files for use with later stages of the workflow. If whole files are added or  deleted, an entire copy of the file is created and marked as an addition or deletion.  The script also has a "reset" feature. When a reset version is being analyzed, all files in the previous version are treated as deletions and all files in the reset version are treated as additions.

**sourceprep.py:** The script is a library of utilities for source-code preprocessing. The script is meant to be called from inside a batch processing loop. The "doprep" function will fully preprocess a source code file by: removing all comments, trimming empty lines, removing all non-alphabetical characters, splitting compound constructions (camel-case and underscores), and filtering stopwords. Each of these tasks can also be performed individually as they're written as separate functions.

**Topic modeling:** At this point, you can use whichever topic modeling utility you prefer. However, the next script relies on output generated by an interface module that I wrote for MALLET, available here.

**diffpost.py:** This script completes the DiffLDA process, producing virtual versions by cumulatively summing token assignment vectors of the addition and deletion documents. Because I was only interested in comparing whole versions at this stage and not individual files, the script produces one vector for each version index number. 