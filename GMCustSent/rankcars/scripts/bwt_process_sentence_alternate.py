####THIS FILE USES THE DICTIONARY TO EXTRACT ASPECTS RATHER THAN THE
####SEMANTIC DIFFERENCE. USE BWT_PROCESS_SENTENCE.PY IF YOU WANT SEMANTIC DIFFERENCE

import csv
import string
import re
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import pickle

test_sent = "This is Brendan's test sentence, it contains GAS, gas, gas and gas and ENGINE and CLIMATE."

def processSentenceDictionary(input_sentence):

    #these solutions for removing punctuation do not work with the web interface
    #noPunctuation = str(input_sentence).translate(None, string.punctuation) 
    #noPunctuation = input_sentence.translate(input_sentence.maketrans(
    #    {key: None for key in string.punctuation})).strip()

    #create a character class from the standard string of punctuation characters
    remove_str = '[' + string.punctuation + ']'
    #replace each punctuation character with the empty string
    noPunctuation = re.sub(remove_str, '', input_sentence)
    
    #tokenize sentence into words
    sentenceWords = word_tokenize(noPunctuation)

    #create list of words with part of speech tags
    posTagged = pos_tag(sentenceWords)

    #create list of stop words
    removeTheseWords = set(stopwords.words('english'))

    #remove stop words from sentence
    stopWordsRemoved = [word.lower() for word in sentenceWords if word.lower()
                        not in removeTheseWords and
                        len(word) > 2]

    #remove stop words from list of words with part of speech tags
    posTaggedNoStopWords = [(word.lower(),pos) for (word,pos) in posTagged if word.lower()
                            not in removeTheseWords and
                            len(word) > 2]


    #remove all words except adjectives, verbs, nouns, and adverbs
    convertedPOSTags = []
    for word,pos in posTaggedNoStopWords:
        if pos.startswith('J'):
            convertedPOSTags.append(((word,wn.ADJ)))
        if pos.startswith('V'):
            convertedPOSTags.append(((word,wn.VERB)))
        if pos.startswith('N'):
            convertedPOSTags.append(((word,wn.NOUN)))
        if pos.startswith('R'):
            convertedPOSTags.append(((word,wn.ADV)))

##    #debugging code for removing stop words and all words except nouns
##    print("gmo combined remove of stop and select only nouns")
##    convertedPOSTags = [(word.lower(),'n') for (word,pos) in posTagged if word.lower()
##                            not in removeTheseWords and not word.isnumeric() and
##                            len(word) > 2 and pos.startswith('N')]

    #choose lemmatizer
    lemmatizer = WordNetLemmatizer()

    #reduce each word to its lemma root based on the part of speech tag
    lemmatizedSentence = [lemmatizer.lemmatize(word,tag) for (word,tag) in convertedPOSTags]


    taxwords = []
    taxsynonyms = []
    taxweights = []

    #read taxonomy file to get aspect words, aspect synonym words, and aspect weights    
    taxonomy = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/taxdictionarytrimmed.csv','r')
    readfile = csv.reader(taxonomy)
    for row in readfile:
        #print(row)
        if row[0] not in taxwords:
            taxwords.append(row[0])
            taxsynonyms.append([])
            taxweights.append(row[2])
        taxsynonyms[taxwords.index(row[0])].append(row[1])
    taxonomy.close()

##    #debugging print statements
##    print(taxwords)
##    print(taxsynonyms)
##    print(taxweights)
    
##    #no longer using synsets to identify aspects
##    for word in taxwords:
##        allTaxSyns.append([syns for syns in wn.synsets(word)])

    #debugging print statements
    #[[ss] for word in taxwords for ss in wn.synsets(word)]
    #print(allTaxSyns)
    #print(taxwords)

    sentenceAspects = []

    #for each word in the sentence, identify the word as an aspect if it matches the aspect word or one of the aspect word's synonyms from the taxonomy file
    for word in lemmatizedSentence:
        for tax in taxwords:
            if word.lower() == tax.lower() and tax not in sentenceAspects:
                sentenceAspects.append(tax)
            elif taxsynonyms[taxwords.index(tax)]:
                for taxsyn in taxsynonyms[taxwords.index(tax)]:
                    if word.lower() == taxsyn.lower() and tax not in sentenceAspects:
                        sentenceAspects.append(tax)
        
##    #debugging code for creating output file to track which aspects are found in each sentence
##    sentence
##        aspects
##    outputfile = open("dictionaryOutput.txt","a+")
##    outputfile.write("\n")
##    outputfile.write(input_sentence + "\n")
##    for aspect in sentenceAspects:
##	    outputfile.write("\t" + aspect+"\n")
##    outputfile.write("\n")
##    outputfile.flush()
##    outputfile.close()
    
    
    return sentenceAspects

###debugging print statement using test sentence
##print(processSentenceDictionary(test_sent))
