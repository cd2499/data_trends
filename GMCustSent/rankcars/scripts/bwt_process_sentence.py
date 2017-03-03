import csv
import string
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from itertools import product

test_sent = "This is Brendan's test sentence, it contains GAS and ENGINE."

def processSentence(input_sentence):
    noPunctuation = input_sentence.translate(input_sentence.maketrans(
        {key: None for key in string.punctuation})).strip()

    sentenceWords = word_tokenize(noPunctuation)

    posTagged = pos_tag(sentenceWords)

    removeTheseWords = set(stopwords.words('english'))

    stopWordsRemoved = [word.lower() for word in sentenceWords if word.lower()
                        not in removeTheseWords and not word.isnumeric() and
                        len(word) > 2]
    
    posTaggedNoStopWords = [(word.lower(),pos) for (word,pos) in posTagged if word.lower()
                            not in removeTheseWords and not word.isnumeric() and
                            len(word) > 2]

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

    lemmatizer = WordNetLemmatizer()

    lemmatizedSentence = [lemmatizer.lemmatize(word,tag) for (word,tag) in convertedPOSTags]

    taxonomy = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/taxonomy.txt','r')
    readfile = csv.reader(taxonomy)
    wordlist = map(tuple,readfile)
    

    taxwords = []
    for word,weight in wordlist:
        taxwords.append(word)
    allTaxSyns = []
    for word in taxwords:
        allTaxSyns.append([syns for syns in wn.synsets(word)])
    #[[ss] for word in taxwords for ss in wn.synsets(word)]
    #print(allTaxSyns)
    #print(taxwords)
    
    sentenceAspects = []

    for word in lemmatizedSentence:
        allWordSyns = set(ss for ss in wn.synsets(str(word)))
        if allWordSyns:
            for word_index in range(len(taxwords)):
                #print("Comparing ", word, " and ", taxwords[word_index])
                bestSim = max((wn.wup_similarity(s1,s2) or 0,s1,s2) for s1,s2 in
                              product(allWordSyns, allTaxSyns[word_index]))
                #print(bestSim)
                if bestSim[0] > .85 and taxwords[word_index] not in sentenceAspects:
                    sentenceAspects.append(taxwords[word_index])
    
    return sentenceAspects

    
