import collections
from collections import Counter
from nltk.corpus import stopwords
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.classify import ClassifierI
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk import word_tokenize, sent_tokenize
from nltk.sentiment.util import mark_negation
import nltk.classify.util
from nltk.metrics import precision, recall, f_measure
import nltk.probability
from nltk import ne_chunk
from sklearn import preprocessing, metrics, cross_validation
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.svm import SVC, LinearSVC, NuSVC
import ast  ##convert the string representation of a list into an actual python list
##from statistics import mode ##for choosing the best algorithm result
import bwt_process_sentence_alternate
import happybase
import argparse
import itertools
import math
import nltk, re, pprint
import pickle
import random
import time
import string
import spacy

## This script is not run from the web interface
## This script must be run from the python 3 shell/command line

## Developer Note: Running this script will:
## 1. rewrite the master features list
## 2. train various classifiers
## 3. save the various trained classifiers. The saved ("pickled") classifiers can then be used in the main sentiment_analysis script

## This script relies on the manually scored reviews within the 'all_reviews_by_sent.txt' file. Updates to the manually scored file will 
## update the results in the master feature list and, in turn, affect the results of the training.

## function to extract features from a single sentence, given the sentence as a list of words and the list of features to look for
def extract_features(user_doc, master_features_list, senti_dict):

    #make all words in the sentence lowercase
    lower_words = [word.lower() for word in user_doc]
    
    words_no_punctuation = []
    # remove punctuation
    for word in lower_words:
        temp_word = word.translate(word.maketrans({key: None for key in string.punctuation})).strip()
        if len(temp_word) > 2:
            words_no_punctuation.append(temp_word)
    
    ## remove stop words
    words_filtered = [word for word in words_no_punctuation if word not in stopwords.words('english')]

    ## remove car makes, models, and years
    words_filtered = removeNames(words_filtered)
    
    ## unigrams for this sentence is the list of words without duplicates
    user_doc_by_unigrams = set(words_filtered) #"set" will create a distinct list of words from user_doc
  
    ## use nltk bigram collocation finder to find bigrams, which may fail if there are no words or very few words
##    try:
##        bigram_finder = BigramCollocationFinder.from_words(words_filtered, 5)
##        user_doc_by_bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5)
##    except ZeroDivisionError:
##        user_doc_by_bigrams = []

    #debugging print statement
    #print("in extract", user_doc_by_words)    

    #append _NEG to word tokens that are detected as negated, this seems very inaccurate
    #user_doc_by_unigrams = mark_negation([x for x in user_doc_by_unigrams])

    #dictionary that will have each feature as a key and the value of the feature as the value
    doc_features = {}

    #print sentence and words, showing which words are marked as negated
    #print(user_doc)
    #for word in user_doc_by_unigrams:
        #print(word)
    #input()
    #this seems to have very low accuracy for marking words that are actually negated

    #create count feature for adjectives and for adverbs, nouns and verbs seem to give poor features
    #adj_count = 0
    #noun_count = 0
    #adv_count = 0
    #verb_count = 0

    sentence_polarity = 0.0
    
    #calculate sentence polarity
    tagged_doc = nltk.pos_tag(words_filtered)
    for tag in tagged_doc:
        if tag[1] in ('JJ', 'JJR', 'JJS'):
            #adj_count = adj_count + 1
            tag_key = tag[0] + '.a'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                max_diff = 0.0
                #assume the word has the strongest meaning possible
                #find the meaning of the word with the most clearly positive polarity or clearly negative polarity
                #if the given positive polarity and negative polarity are similar in magnitude, it is unclear which is being used
                for item in polar_list:
                    if abs(item[0] - item[1]) > abs(max_diff):
                        max_diff = item[0] - item[1]
                #add the maximum difference in polarity to the sentence polarity
                sentence_polarity = sentence_polarity + max_diff
##        elif tag[1] in ('NN', 'NNS'):
##            #noun_count = noun_count + 1
##            tag_key = tag[0] + '.n'
##            if tag_key in senti_dict:
##                polar_list = senti_dict[tag_key]
##                max_diff = 0.0
##                #assume the word has the strongest meaning possible
##                #find the meaning of the word with the most clearly positive polarity or clearly negative polarity
##                #if the given positive polarity and negative polarity are similar in magnitude, it is unclear which is being used
##                for item in polar_list:
##                    if abs(item[0] - item[1]) > abs(max_diff):
##                        max_diff = item[0] - item[1]
##                #add the maximum difference in polarity to the sentence polarity
##                sentence_polarity = sentence_polarity + max_diff
        elif tag[1] in ('RB', 'RBR', 'RBS'):
            #adv_count = adv_count + 1
            tag_key = tag[0] + '.r'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                max_diff = 0.0
                #assume the word has the strongest meaning possible
                #find the meaning of the word with the most clearly positive polarity or clearly negative polarity
                #if the given positive polarity and negative polarity are similar in magnitude, it is unclear which is being used
                for item in polar_list:
                    if abs(item[0] - item[1]) > abs(max_diff):
                        max_diff = item[0] - item[1]
                #add the maximum difference in polarity to the sentence polarity
                sentence_polarity = sentence_polarity + max_diff
        elif tag[1] in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'):
            #verb_count = verb_count + 1
            tag_key = tag[0] + '.v'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                max_diff = 0.0
                #assume the word has the strongest meaning possible
                #find the meaning of the word with the most clearly positive polarity or clearly negative polarity
                #if the given positive polarity and negative polarity are similar in magnitude, it is unclear which is being used
                for item in polar_list:
                    if abs(item[0] - item[1]) > abs(max_diff):
                        max_diff = item[0] - item[1]
                #add the maximum difference in polarity to the sentence polarity
                sentence_polarity = sentence_polarity + max_diff

    #add has adjective and has adverb to list of extracted features
    #doc_features['has_adj'] = adj_count > 0
    #doc_features['noun_count'] = noun_count
    #doc_features['has_adv'] = adv_count > 0
    #doc_features['verb_count'] = verb_count

    #convert sentence_polarity into a discrete feature as follows:
    #greater than 1.0   -> 3
    #(0.5, 1.0]         -> 2
    #(0.0, 0.5]         -> 1
    #0.0                -> 0
    #[-0.5, 0.0)        -> -1
    #[-1.0, -0.5)       -> -2
    #less than -1.0     -> -3
    if sentence_polarity > 1.0:
        doc_features['sentence_polarity'] = 3
    elif sentence_polarity > 0.5:
        doc_features['sentence_polarity'] = 2
    elif sentence_polarity > 0.0:
        doc_features['sentence_polarity'] = 1
    elif sentence_polarity == 0.0:
        doc_features['sentence_polarity'] = 0
    elif sentence_polarity >= -0.5:
        doc_features['sentence_polarity'] = -1
    elif sentence_polarity >= -1.0:
        doc_features['sentence_polarity'] = -2
    else:
        doc_features['sentence_polarity'] = -3
    
    #for each unigram and bigram, the value is true if it appears in the sentence and false otherwise
    for feature in master_features_list:
##        if type(feature) is tuple: ##bigrams
##            doc_features[feature] = (feature in user_doc_by_bigrams)

        if feature not in ('sentence_polarity', 'has_adj', 'has_adv', 'adj_count', 'noun_count', 'adv_count', 'verb_count'): ##unigrams
            doc_features[feature] = (feature in user_doc_by_unigrams)

    return doc_features


#function to extract bigram features from the trainging set of sentences passed as a list of words
def getBigramFeats(words, score_fn=BigramAssocMeasures.chi_sq, n=15):

        #use nltk bigram collocation finder for pairs of words that appear within 5 words of each other
        bigram_finder = BigramCollocationFinder.from_words(words, 5)

        #only keep bigrams that are found at least 3 times
        bigrams_filtered = bigram_finder.apply_freq_filter(3)

        #only return strongly related bigrams
        bigrams = bigram_finder.nbest(score_fn, n)

        return list(bigrams)

#function to extract unigrams from a sentence passed as a list of words
def getUnigramFeats(rvws_by_word, senti_dict):

    ## tag parts of speech
    tagged_words = nltk.pos_tag(rvws_by_word)
    
    ## old code for filtering words by part of speech
    #rvws_by_word_filtered = [word[0] for word in tagged_words if word[1] in ('JJ', 'JJR', 'JJS', 'NN', 'NNS', 'RB', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')]
    #rvws_by_word_filtered = [word[0] for word in tagged_words if word[1] in ('JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS')]
    ## only use adjectives, nouns, adverbs, and verbs with strong sentiment polarity
    rvws_by_word_filtered = []
    for word in tagged_words:
        if word[1] in ('JJ', 'JJR', 'JJS'):
            tag_key = word[0] + '.a'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                for item in polar_list:
                    if abs(item[0] - item[1]) >= 0.75:
                        rvws_by_word_filtered.append(word[0])
                        break
##        elif word[1] in ('NN', 'NNS'):
##            tag_key = word[0] + '.n'
##            if tag_key in senti_dict:
##                polar_list = senti_dict[tag_key]
##                for item in polar_list:
##                    if abs(item[0] - item[1]) >= 0.75:
##                        rvws_by_word_filtered.append(word[0])
##                        break
        elif word[1] in ('RB', 'RBR', 'RBS'):
            tag_key = word[0] + '.r'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                for item in polar_list:
                    if abs(item[0] - item[1]) >= 0.75:
                        rvws_by_word_filtered.append(word[0])
                        break
        elif word[1] in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'):
            tag_key = word[0] + '.v'
            if tag_key in senti_dict:
                polar_list = senti_dict[tag_key]
                for item in polar_list:
                    if abs(item[0] - item[1]) >= 0.75:
                        rvws_by_word_filtered.append(word[0])
                        break
    
    ## get word frequency
    word_freq = nltk.FreqDist(rvws_by_word_filtered)
    
    ## GMO todo remove any intersect between unigram and bigram, leave it in the bigram prob`

    unigram_list = []
    #create list of most frequent words
    common_list = word_freq.most_common(30)
    for t in common_list:
        unigram_list.append(t[0])
    
    return unigram_list

#function to remove custom stop words and car makes, models, and years
def removeNames(rvws_by_word):

    names = ['am-general', 'hummer',
             'acura', 'cl', 'ilx', 'ilx-hybrid', 'integra', 'legend', 'mdx', 'nsx', 'rdx', 'rl', 'rlx', 'rsx', 'slx', 'tl', 'tlx', 'tsx', 'tsx-sport-wagon', 'vigor', 'zdx',
             'alfa-romeo', '4c', '4c-spider', 'giulia',
             'aston-martin', 'db7', 'db9', 'db9-gt', 'dbs', 'rapide', 'rapide-s', 'v12-vanquish', 'v12-vantage', 'v12-vantage-s', 'v8-vantage', 'vanquish', 'virage',
             'audi', '100', '200', '80', '90', 'a3', 'a3-sportback-e-tron', 'a4', 'a4-allroad', 'a5', 'a6', 'a7', 'a8', 'cabriolet', 'coupe', 'q3', 'q5', 'q7', 'q7-e-tron', 'r8', 'rs-4', 'rs-5', 'rs-6', 'rs-7', 's3', 's4', 's5', 's6', 's7', 's8', 'sq5', 'tt', 'tt-rs', 'tts', 'v8', 'allroad', 'allroad-quattro',
             'bmw', '1-series', '1-series-m', '2-series', '3-series', '3-series-gran-turismo', '3-series-edrive', '4-series', '4-series-gran-coupe', '5-series', '5-series-gran-turismo', '6-series', '6-series-gran-coupe', '7-series', '8-series', 'alpina-b6-gran-coupe', 'alpina-b7', 'activehybrid-5', 'activehybrid-7', 'activehybrid-x6', 'alpina', 'm', 'm2', 'm3', 'm4', 'm4-gts', 'm5', 'm6', 'm6-gran-coupe', 'x1', 'x3', 'x4', 'x5', 'x5-m', 'x5-edrive', 'x6', 'x6-m', 'x7', 'z3', 'z4', 'z4-m', 'z8', 'i3', 'i8',
             'bentley', 'arnage', 'azure', 'azure-t', 'bentayga', 'brooklands', 'continental', 'continental-flying-spur', 'continental-flying-spur-speed', 'continental-gt', 'continental-gt-speed', 'continental-gt-speed-convertible', 'continental-gt3-r', 'continental-gtc', 'continental-gtc-speed', 'continental-supersports', 'continental-supersports-convertible', 'flying-spur', 'mulsanne', 'supersports-convertible-isr',
             'bugatti', 'veyron-164',
             'buick', 'cascada', 'century', 'electra', 'enclave', 'encore', 'envision', 'estate-wagon', 'lacrosse', 'lesabre', 'lucerne', 'park-avenue', 'rainier', 'reatta', 'regal', 'rendezvous', 'riviera', 'roadmaster', 'skylark', 'terraza', 'verano',
             'cadillac', 'ats', 'ats-coupe', 'ats-v', 'allante', 'brougham', 'ct6', 'cts', 'cts-coupe', 'cts-wagon', 'cts-v', 'cts-v-coupe', 'cts-v-wagon', 'catera', 'dts', 'deville', 'elr', 'eldorado', 'escalade', 'escalade-esv', 'escalade-ext', 'escalade-hybrid', 'fleetwood', 'srx', 'sts', 'sts-v', 'seville', 'sixty-special', 'xlr', 'xlr-v', 'xt5', 'xt7', 'xts',
             'chevrolet', 'astro', 'astro-cargo', 'avalanche', 'aveo', 'beretta', 'black-diamond-avalanche', 'blazer', 'bolt', 'bolt-ev', 'ck-1500-series', 'ck-2500-series', 'ck-3500-series', 'camaro', 'caprice', 'captiva-sport', 'cavalier', 'celebrity', 'chevy-van', 'chevy-van-classic', 'city-express', 'classic', 'cobalt', 'colorado', 'corsica', 'corvette', 'corvette-stingray', 'cruze', 'cruze-limited', 'equinox', 'express', 'express-cargo', 'hhr', 'impala', 'impala-limited', 'lumina', 'lumina-minivan', 'malibu', 'malibu-classic', 'malibu-hybrid', 'malibu-limited', 'malibu-maxx', 'metro', 'monte-carlo', 'prizm', 'rv-3500-series', 's-10', 's-10-blazer', 'ss', 'ssr', 'silverado-1500', 'silverado-1500-classic', 'silverado-1500-hybrid', 'silverado-1500hd', 'silverado-1500hd-classic', 'silverado-2500', 'silverado-2500hd', 'silverado-2500hd-classic', 'silverado-3500', 'silverado-3500-classic', 'silverado-3500hd', 'sonic', 'spark', 'spark-ev', 'sportvan', 'suburban', 'tahoe', 'tahoe-hybrid', 'tahoe-limitedz71', 'tracker', 'trailblazer', 'trailblazer-ext', 'traverse', 'trax', 'uplander', 'venture', 'volt',
             'chrysler', '200', '300', '300m', 'aspen', 'cirrus', 'concorde', 'crossfire', 'grand-voyager', 'imperial', 'lhs', 'le-baron', 'new-yorker', 'pt-cruiser', 'pacifica', 'prowler', 'sebring', 'tc', 'town-and-country', 'voyager',
             'daewoo', 'lanos', 'leganza', 'nubira',
             'dodge', 'avenger', 'caliber', 'caravan', 'challenger', 'charger', 'colt', 'dakota', 'dart', 'daytona', 'durango', 'dynasty', 'grand-caravan', 'intrepid', 'journey', 'magnum', 'monaco', 'neon', 'nitro', 'omni', 'ram-150', 'ram-250', 'ram-350', 'ram-50-pickup', 'ram-cargo', 'ram-pickup-1500', 'ram-pickup-2500', 'ram-pickup-3500', 'ram-van', 'ram-wagon', 'ramcharger', 'srt-viper', 'shadow', 'spirit', 'sprinter', 'sprinter-cargo', 'stealth', 'stratus', 'viper',
             'eagle', 'premier', 'summit', 'talon', 'vision',
             'fiat', '124-spider', '500', '500l', '500x', '500e',
             'ferrari', '360', '430-scuderia', '456m', '458-italia', '550', '575m', '599', '612-scaglietti', 'california', 'california-t', 'enzo', 'f12-berlinetta', 'f430', 'ff', 'superamerica',
             'fisker', 'karma', 
             'ford', 'aerostar', 'aspire', 'bronco', 'bronco-ii', 'c-max-energi', 'c-max-hybrid', 'contour', 'contour-svt', 'crown-victoria', 'e-150', 'e-250', 'e-350', 'e-series-van', 'e-series-wagon', 'econoline-cargo', 'econoline-wagon', 'edge', 'escape', 'escape-hybrid', 'escort', 'excursion', 'expedition', 'expedition-el', 'explorer', 'explorer-sport', 'explorer-sport-trac', 'f-150', 'f-150-heritage', 'f-150-svt-lightning', 'f-250', 'f-250-super-duty', 'f-350', 'f-350-super-duty', 'f-450-super-duty', 'festiva', 'fiesta', 'five-hundred', 'flex', 'focus', 'focus-rs', 'focus-st', 'freestar', 'freestyle', 'fusion', 'fusion-energi', 'fusion-hybrid', 'gt', 'ltd-crown-victoria', 'mustang', 'mustang-svt-cobra', 'probe', 'ranger', 'shelby-gt350', 'shelby-gt500', 'taurus', 'taurus-x', 'tempo', 'thunderbird', 'transit-connect', 'transit-van', 'transit-wagon', 'windstar', 'windstar-cargo',
             'gmc', 'acadia', 'acadia-limited', 'canyon', 'envoy', 'envoy-xl', 'envoy-xuv', 'jimmy', 'rv-3500-series', 'rally-wagon', 's-15', 's-15-jimmy', 'safari', 'safari-cargo', 'savana', 'savana-cargo', 'sierra-1500', 'sierra-1500-classic', 'sierra-1500-hybrid', 'sierra-1500hd', 'sierra-1500hd-classic', 'sierra-2500', 'sierra-2500hd', 'sierra-2500hd-classic', 'sierra-3500', 'sierra-3500-classic', 'sierra-3500hd', 'sierra-c3', 'sierra-classic-1500', 'sierra-classic-2500', 'sierra-classic-3500', 'sonoma', 'suburban', 'syclone', 'terrain', 'typhoon', 'vandura', 'yukon', 'yukon-denali', 'yukon-hybrid', 'yukon-xl',
             'genesis', 'g80', 'g90',
             'geo', 'metro', 'prizm', 'storm', 'tracker',
             'hummer', 'h1', 'h1-alpha', 'h2', 'h2-sut', 'h3', 'h3t',
             'honda', 'accord', 'accord-crosstour', 'accord-hybrid', 'accord-plug-in-hybrid', 'cr-v', 'cr-z', 'civic', 'civic-crx', 'civic-del-sol', 'clarity', 'crosstour', 'element', 'fit', 'fit-ev', 'hr-v', 'insight', 'odyssey', 'passport', 'pilot', 'prelude', 'ridgeline', 's2000',
             'hyundai', 'accent', 'azera', 'elantra', 'elantra-coupe', 'elantra-gt', 'elantra-touring', 'entourage', 'equus', 'excel', 'genesis', 'genesis-coupe', 'ioniq', 'santa-fe', 'santa-fe-sport', 'scoupe', 'sonata', 'sonata-hybrid', 'sonata-plug-in-hybrid', 'sonata-plug-in-hybrid', 'tiburon', 'tucson', 'veloster', 'veracruz', 'xg300', 'xg350',
             'infiniti', 'ex', 'ex35', 'fx', 'fx35', 'fx45', 'fx50', 'g-convertible', 'g-coupe', 'g-sedan', 'g20', 'g35', 'g37', 'g37-convertible', 'g37-coupe', 'g37-sedan', 'i30', 'i35', 'j30', 'jx', 'm', 'm30', 'm35', 'm37', 'm45', 'm56', 'q40', 'q45', 'q50', 'q60-convertible', 'q60-coupe', 'q70', 'qx', 'qx30', 'qx4', 'qx50', 'qx56', 'qx60', 'qx70', 'qx80',
             'isuzu', 'amigo', 'ascender', 'axiom', 'hombre', 'impulse', 'oasis', 'pickup', 'rodeo', 'rodeo-sport', 'stylus', 'trooper', 'vehicross', 'i-series',
             'jaguar', 'f-pace', 'f-type', 's-type', 'x-type', 'xe', 'xf', 'xj', 'xj-series', 'xjr', 'xk', 'xk-series', 'xkr',
             'jeep', 'cherokee', 'comanche', 'commander', 'compass', 'compass-x', 'grand-cherokee', 'grand-cherokee-srt', 'grand-wagoneer', 'liberty', 'patriot', 'patriot-x', 'renegade', 'wagoneer', 'wrangler',
             'kia', 'amanti', 'borrego', 'cadenza', 'forte', 'k900', 'niro', 'optima', 'optima-hybrid', 'rio', 'rondo', 'sedona', 'sephia', 'sorento', 'soul', 'soul-ev', 'spectra', 'sportage',
             'lamborghini', 'aventador', 'diablo', 'gallardo', 'huracan', 'murcielago', 'reventon',
             'land-rover', 'defender', 'discovery', 'discovery-series-ii', 'discovery-sport', 'freelander', 'lr2', 'lr3', 'lr4', 'range-rover', 'range-rover-evoque', 'range-rover-sport',
             'lexus', 'ct-200h', 'es-250', 'es-300', 'es-300h', 'es-330', 'es-350', 'gs-200t', 'gs-300', 'gs-350', 'gs-400', 'gs-430', 'gs-450h', 'gs-460', 'gs-f', 'gx-460', 'gx-470', 'hs-250h', 'is-200t', 'is-250', 'is-250-c', 'is-300', 'is-350', 'is-350-c', 'is-f', 'lc-500', 'lfa', 'ls-400', 'ls-430', 'ls-460', 'ls-600h-l', 'lx-450', 'lx-470', 'lx-570', 'nx-200t', 'nx-300h', 'rc-200t', 'rc-300', 'rc-350', 'rc-f', 'rx-300', 'rx-330', 'rx-350', 'rx-400h', 'rx-450h', 'sc-300', 'sc-400', 'sc-430',
             'lincoln', 'aviator', 'blackwood', 'continental', 'ls', 'mkc', 'mks', 'mkt', 'mkx', 'mkz', 'mkz-hybrid', 'mark-lt', 'mark-vii', 'mark-viii', 'navigator', 'navigator-l', 'town-car', 'zephyr',
             'lotus', 'elise', 'esprit', 'evora', 'evora-400', 'exige',
             'mini', 'clubman', 'convertible', 'cooper', 'cooper-clubman', 'cooper-countryman', 'cooper-coupe', 'cooper-paceman', 'cooper-roadster', 'hardtop',
             'maserati', 'coupe', 'ghibli', 'gransport', 'granturismo', 'granturismo-convertible', 'levante', 'quattroporte', 'spyder',
             'maybach', '57', '62', 'landaulet',
             'mazda', '2', '3', '323', '5', '6', '626', '929', 'b-series', 'b-series-pickup', 'b-series-truck', 'cx-3', 'cx-5', 'cx-7', 'cx-9', 'mpv', 'mx-3', 'mx-5-miata', 'mx-5-miata-rf', 'mx-6', 'mazdaspeed-3', 'mazdaspeed-6', 'mazdaspeed-mx-5-miata', 'mazdaspeed-protege', 'millenia', 'navajo', 'protege', 'protege5', 'rx-7', 'rx-8', 'tribute', 'tribute-hybrid', 'truck',
             'mclaren', '570s', '650s-coupe', '650s-spider', 'mp4-12c', 'mp4-12c-spider',
             'mercedes-benz', '190-class', '300-class', '350-class', '400-class', '420-class', '500-class', '560-class', '600-class', 'amg-gt', 'b-class-electric-drive', 'c-class', 'c36-amg', 'c43-amg', 'cl-class', 'cla-class', 'clk-class', 'cls-class', 'e-class', 'e55-amg', 'g-class', 'gl-class', 'gla-class', 'glc-class', 'glc-class-coupe', 'gle-class', 'gle-class-coupe', 'glk-class', 'gls-class', 'm-class', 'ml55-amg', 'maybach', 'metris', 'r-class', 's-class', 'sl-class', 'slc-class', 'slk-class', 'slr-mclaren', 'sls-amg', 'sls-amg-gt', 'sls-amg-gt-final-edition', 'sprinter', 'sprinter-worker',
             'mercury', 'capri', 'cougar', 'grand-marquis', 'marauder', 'mariner', 'mariner-hybrid', 'milan', 'milan-hybrid', 'montego', 'monterey', 'mountaineer', 'mystique', 'sable', 'topaz', 'tracer', 'villager',
             'mitsubishi', '3000gt', 'diamante', 'eclipse', 'eclipse-spyder', 'endeavor', 'expo', 'galant', 'lancer', 'lancer-evolution', 'lancer-sportback', 'mighty-max-pickup', 'mirage', 'mirage-g4', 'montero', 'montero-sport', 'outlander', 'outlander-sport', 'precis', 'raider', 'sigma', 'vanwagon', 'i-miev',
             'nissan', '200sx', '240sx', '300zx', '350z', '370z', 'altima', 'altima-hybrid', 'armada', 'axxess', 'cube', 'frontier', 'gt-r', 'juke', 'leaf', 'maxima', 'murano', 'murano-crosscabriolet', 'nv', 'nv-cargo', 'nv-passenger', 'nv200', 'nx', 'pathfinder', 'pulsar', 'quest', 'rogue', 'rogue-select', 'sentra', 'stanza', 'titan', 'titan-xd', 'truck', 'van', 'versa', 'versa-note', 'xterra',
             'oldsmobile', 'achieva', 'alero', 'aurora', 'bravada', 'ciera', 'custom-cruiser', 'cutlass', 'cutlass-calais', 'cutlass-ciera', 'cutlass-supreme', 'eighty-eight', 'eighty-eight-royale', 'intrigue', 'lss', 'ninety-eight', 'regency', 'silhouette', 'toronado',
             'panoz', 'esperante',
             'plymouth', 'acclaim', 'breeze', 'colt', 'grand-voyager', 'horizon', 'laser', 'neon', 'prowler', 'sundance', 'voyager',
             'pontiac', '6000', 'aztek', 'bonneville', 'firebird', 'g3', 'g5', 'g6', 'g8', 'gto', 'grand-am', 'grand-prix', 'le-mans', 'montana', 'montana-sv6', 'solstice', 'sunbird', 'sunfire', 'torrent', 'trans-sport', 'vibe',
             'porsche', '718-boxster', '718-cayman', '911', '918-spyder', '928', '944', '968', 'boxster', 'carrera-gt', 'cayenne', 'cayman', 'cayman-s', 'macan', 'panamera',
             'ram', '1500', '2500', '3500', 'cv-cargo-van', 'cv-tradesman', 'cv-tradesman', 'dakota', 'promaster-cargo-van', 'promaster-city', 'promaster-window-van',
             'rolls-royce', 'corniche', 'dawn', 'ghost', 'ghost-series-ii', 'park-ward', 'phantom', 'phantom-coupe', 'phantom-drophead-coupe', 'silver-seraph', 'wraith',
             'saab', '9-2x', '9-3', '9-3-griffin', '9-4x', '9-5', '9-7x', '900', '9000',
             'saturn', 'astra', 'aura', 'aura-hybrid', 'ion', 'l-series', 'l300', 'outlook', 'relay', 's-series', 'sky', 'vue', 'vue-hybrid',
             'scion', 'fr-s', 'ia', 'im', 'iq', 'tc', 'xa', 'xb', 'xd',
             'spyker', 'c8',
             'subaru', 'b9-tribeca', 'brz', 'baja', 'crosstrek', 'forester', 'impreza', 'impreza-wrx', 'justy', 'legacy', 'loyale', 'outback', 'svx', 'tribeca', 'wrx', 'xt', 'xv-crosstrek',
             'suzuki', 'aerio', 'equator', 'esteem', 'forenza', 'grand-vitara', 'kizashi', 'reno', 'sx4', 'samurai', 'sidekick', 'swift', 'verona', 'vitara', 'x-90', 'xl-7', 'xl7',
             'tesla', 'model-3', 'model-s', 'model-x', 'roadster',
             'toyota', '4runner', '86', 'avalon', 'avalon-hybrid', 'c-hr', 'camry', 'camry-hybrid', 'camry-solara', 'celica', 'corolla', 'corolla-im', 'cressida', 'echo', 'fj-cruiser', 'highlander', 'highlander-hybrid', 'land-cruiser', 'mr2', 'mr2-spyder', 'matrix', 'mirai', 'paseo', 'pickup', 'previa', 'prius', 'prius-plug-in', 'prius-prime', 'prius-c', 'prius-v', 'rav4', 'rav4-ev', 'rav4-hybrid', 'sequoia', 'sienna', 'supra', 't100', 'tacoma', 'tercel', 'tundra', 'venza', 'yaris', 'yaris-ia',
             'volkswagen', 'atlas', 'beetle', 'beetle-convertible', 'cc', 'cabrio', 'cabriolet', 'corrado', 'eos', 'eurovan', 'fox', 'gli', 'gti', 'golf', 'golf-alltrack', 'golf-gti', 'golf-r', 'golf-sportwagen', 'golf-sportwagen-alltrack', 'jetta', 'jetta-gli', 'jetta-hybrid', 'jetta-sportwagen', 'new-beetle', 'passat', 'phaeton', 'r32', 'rabbit', 'routan', 'tiguan', 'touareg', 'touareg-2', 'vanagon', 'e-golf',
             'volvo', '240', '740', '760', '780', '850', '940', '960', 'c30', 'c70', 'coupe', 's40', 's60', 's60-cross-country', 's70', 's80', 's90', 'v40', 'v50', 'v60', 'v60-cross-country', 'v70', 'v90', 'v90-cross-country', 'xc', 'xc60', 'xc70', 'xc90',
             'smart', 'fortwo',
             '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
             'rrb', 'lrb', 'car', 'cars', 'truck', 'trucks', 'like', 'windshield', 'dealership', 'dealer', 'instead', 'keyfob', 'let', 'crystal', 'gel', 'admit', 'weight', 'ocean', 'crosstraffic', 'greenleaf', 'washer', 'rpms', 'rotary', 'aremt', 'left', 'read', 'impalas', 'hill', 'street', 'city', 'country', 'suburb', 'suburban', 'vehiclefor', 'headrest', 'america', 'thus', 'climateentertainment', 'usb', 'rain', 'sun', 'user', 'driveway', 'nissans', 'ruff', 'onoff', 'pierre', 'cadilac', 'onboard', 'lane', 'ecoboost', 'due', 'see', 'whole', 'make', 'think', 'open', 'logical', 'single', 'tall', 'low', 'false', 'decent', 'tight', 'right', 'wrong', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'black', 'white']

    return [word for word in rvws_by_word if word not in names]
        
    
## This function rewrites the master features file. The master features file is used for training and classification.
def createMasterFeatures(scored_set, nlp, senti_dict):

    #randomly rearrange sentences, current order may be bad for the training/testing split
    random.shuffle(scored_set)
    
    ##gmo save output of scored_set to shuffle later when training and testing accurraccy?
    user_review_by_sentence = []
    rvws_by_word = []
    rvws_by_word_no_punctuation = []
    
    #list of conjunctions used to split sentences
    #these conjunctions usually negate the part of the sentence that follows,
    #so instead split the negated part into a separate sentence
    conjunction_neg = [' nor ',' ,nor ', ' nor, ', ' but ',' ,but ', ' but, ', ' yet ',' ,yet ', ' yet, ']
    #simplified list of conjunctions used to split sentences
    #conj = ['nor', 'but', 'yet'] 

##    #debugging code for identifying conjunctions used to split sentences
##    test_list = sent_tokenize(user_review[1].decode())
##    ttl_cntr = 0
##    conj_cntr = 0
##    for sent in test_list:
##        ttl_cntr += 1
##        if any(word in sent for word in conj):
##            conj_cntr += 1
##            print("BEFORE::", sent)
##    
##    print("totalcounting ", ttl_cntr, conj_cntr)


    ## break user review into sentences, then create as a set to pass to classifier
    ##print ("BEFORE", scored_set)
    ## use regular expressions to replace conjunctions used to split sentences with a period
    conjunction_regex = re.compile('|'.join(map(re.escape, conjunction_neg)))
    conj_2_sentence = [conjunction_regex.sub(".", sentence) for (sentence, category) in scored_set]
    ##print("AFTER", conj_2_sentence)

    ## create list of sentences using nltk sentence tokenizer
    for text in conj_2_sentence:
        user_review_by_sentence.extend(sent_tokenize(text))

    names_filtered = []
    ## use spacy to remove named entities
    for sentence in user_review_by_sentence:
        spacy_doc = nlp(sentence)
        named_ents = spacy_doc.ents
        ents = [str(e[0]) for e in named_ents]
        names_filtered.extend([word for word in word_tokenize(sentence) if word not in ents])
        
    ## get reviews down to word level and store in "rvws_by_word"
    for word in names_filtered:
        rvws_by_word.append(word.lower())  ##gmo consider these are at lowecase, how will that effect future analysis?

    # remove punctuation
    for word in rvws_by_word:
        temp_word = word.translate(word.maketrans({key: None for key in string.punctuation})).strip()
        if len(temp_word) > 2:
            rvws_by_word_no_punctuation.append(temp_word)
    
    ## remove stop words
    rvws_by_word_filtered = [word for word in rvws_by_word_no_punctuation if word not in stopwords.words('english')]

    ## remove custom stop words and car makes, models, and years
    rvws_by_word_filtered = removeNames(rvws_by_word_filtered)
    
    ## gather most common unigrams
    unigram_feat_list = getUnigramFeats(rvws_by_word_filtered, senti_dict)
    
    ## gather most common bigrams
    #bigram_feat_list = getBigramFeats(rvws_by_word_filtered)
    
    master_features_list = unigram_feat_list
    #master_features_list = list(itertools.chain(unigram_feat_list, bigram_feat_list))
    #master_features_list.extend(['adj_count', 'noun_count', 'adv_count', 'verb_count'])
    master_features_list.extend(['sentence_polarity'])
    
    ## finally, save the new feature list 
    save_master_features_list = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/master_feat_list.pickle", "wb")
    pickle.dump(master_features_list, save_master_features_list, protocol=2)
    save_master_features_list.close() 
    
    
    print("New master features list file created.")

#function to train a new Naive Bayes classifier
def trainClassifier(manually_scored_file):
    
    ## open manually scored file
    input_file = open(manually_scored_file, 'r')
    scored_set = input_file.read()
    scored_set = ast.literal_eval(scored_set) #convert string in list format to actual python list

    #remove neutral sentences from training set
    scored_set = [(sentence, category) for (sentence, category) in scored_set if category not in ('2')]

    #create an instance of the spacy English parser
    nlp = spacy.en.English()

    #retrieve SentiWordNet data
    senti_data_file = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/senti_dict.pickle', 'rb')
    senti_dict = pickle.load(senti_data_file)
    senti_data_file.close()
    
    ## write a new master features list   
    createMasterFeatures(scored_set, nlp, senti_dict)

    ## pull in master features list 
    master_features_file = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/master_feat_list.pickle", "rb")
    master_features_list = pickle.load(master_features_file)
    master_features_file.close()     

    
    ## output features list for debugging
    textFeatures = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/features.txt", "w")
    for feat in master_features_list:
        textFeatures.write(str(feat) + "\n")
    textFeatures.flush()
    textFeatures.close()

    ## dictionary for converting values to pos/neg
    def f(x):
        return{
            '0' : 'neg',
            '1' : 'neg',
            #'2' : 'pos',
            '3' : 'pos',
            '4' : 'pos'
        }[x]

    named_set = []
    
    ## use spacy to remove named entities
    for item in scored_set:
        spacy_doc = nlp(item[0])
        named_ents = spacy_doc.ents
        ents = [str(e[0]) for e in named_ents]
        word_doc = [word for word in word_tokenize(item[0]) if word not in ents]
        named_set.append((word_doc, item[1]))
    
    ## using feature list, identify which features are associated with positive/negative reviews    
    featuresets = [(extract_features(sentence, master_features_list, senti_dict), f(category)) for (sentence, category) in named_set]
    
    ## 70/30 split between training set and testing set
    set_length = len(featuresets)
    training_set_length = int(math.floor(set_length * .7))
    testing_set_length = int(training_set_length - set_length)
    
    training_set = featuresets[:training_set_length]
    testing_set = featuresets[testing_set_length:]
 
    

## BEGIN training and saving classifiers

    ## NAIVE BAYES
    naive_classifier = nltk.NaiveBayesClassifier.train(training_set)

    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/naivebayes.pickle", "wb")
    pickle.dump(naive_classifier, save_classifier, protocol=2)
    save_classifier.close()

    #calculate metrics of classifier
    #accuracy is easily calculated based on testing set as a whole
    classifier_metrics = []
    accuracy = nltk.classify.accuracy(naive_classifier, testing_set)
    classifier_metrics.append(accuracy)
    
    #precision, recall, and F-measure require tracking each classification made on the testing set
    ref_sets = collections.defaultdict(set)
    test_sets = collections.defaultdict(set)

    #record each classification made on the testing set
    #ref_sets is the correct classifications
    #test_sets is the classifications the classifier gave
    for i, (features, label) in enumerate(testing_set):
        ref_sets[label].add(i)
        output = naive_classifier.classify(features)
        test_sets[output].add(i)

    #calculate precision, recall, and F-measure separately for positive and negative sentences
    pos_precision = precision(ref_sets["pos"], test_sets["pos"])
    classifier_metrics.append(pos_precision)
    pos_recall = recall(ref_sets["pos"], test_sets["pos"])
    classifier_metrics.append(pos_recall)
    pos_f_measure = f_measure(ref_sets["pos"], test_sets["pos"])
    classifier_metrics.append(pos_f_measure)
    neg_precision = precision(ref_sets["neg"], test_sets["neg"])
    classifier_metrics.append(neg_precision)
    neg_recall = recall(ref_sets["neg"], test_sets["neg"])
    classifier_metrics.append(neg_recall)
    neg_f_measure = f_measure(ref_sets["neg"], test_sets["neg"])
    classifier_metrics.append(neg_f_measure)

    #save metrics of classifier so they can be retrieved and viewed in another script, if desired
    save_classifier_metrics = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/classifier_metrics.pickle", "wb")
    pickle.dump(classifier_metrics, save_classifier_metrics, protocol=2)
    save_classifier_metrics.close()
    
    #print("Naive Bayes classifier successfully saved")
    #print("Naive Bayes algo classifier accuracy percent:", (nltk.classify.accuracy(naive_classifier, testing_set))*100)
    print(naive_classifier.show_most_informative_features(30),"\n")

    #retrieve metrics of classifier, not necessary here but this is how it is done
    classifier_metrics_file = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/classifier_metrics.pickle", "rb")
    classifier_metrics = pickle.load(classifier_metrics_file)
    classifier_metrics_file.close()

    #print metrics of classifier
    print("Accuracy: " + str(classifier_metrics[0] * 100) + "%")
    print("Positive Precision: " + str(classifier_metrics[1] * 100) + "%")
    print("Positive Recall: " + str(classifier_metrics[2] * 100) + "%")
    print("Positive F-measure: " + str(classifier_metrics[3] * 100) + "%")
    print("Negative Precision: " + str(classifier_metrics[4] * 100) + "%")
    print("Negative Recall: " + str(classifier_metrics[5] * 100) + "%")
    print("Negative F-measure: " + str(classifier_metrics[6] * 100) + "%")
    
    ## MULTINOMIAL BAYES
##    MNB_classifier = SklearnClassifier(MultinomialNB())
##    MNB_classifier.train(training_set)
    
##    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/multinombayes.pickle", "wb")
##    pickle.dump(MNB_classifier, save_classifier)
##    save_classifier.close()

##    print("Multinomial Bayes classifier successfully saved")
##    print("MultinomialNB accuracy percent:",nltk.classify.accuracy(MNB_classifier, testing_set),"\n")
        

    ## BERNOULLI
##    BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
##    BernoulliNB_classifier.train(training_set)
    
##    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/bernoulli.pickle", "wb")
##    pickle.dump(BernoulliNB_classifier, save_classifier)
##    save_classifier.close()

##    print("Bernoulli classifier successfully saved")
##    print("BernoulliNB accuracy percent:",nltk.classify.accuracy(BernoulliNB_classifier, testing_set),"\n") 

    ## SVC
    # normal support vector is commonly low, remove it   
##    SVC_classifier = SklearnClassifier(SVC())
##    SVC_classifier.train(training_set)

##    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/svc.pickle", "wb")
##    pickle.dump(SVC_classifier, save_classifier)
##    save_classifier.close()

##    print("Support Vector classifier successfully saved")
##    print("Support Vector accuracy percent:",nltk.classify.accuracy(SVC_classifier, testing_set),"\n")
    

    ## LINEAR SVC
##    LinearSVC_classifier = SklearnClassifier(LinearSVC())
##    LinearSVC_classifier.train(training_set)
    
##    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/linearsvc.pickle", "wb")
##    pickle.dump(LinearSVC_classifier, save_classifier)
##    save_classifier.close()

##    print("Linear Support Vector classifier successfully saved")
##    print("Linear Support Vector accuracy percent:",nltk.classify.accuracy(LinearSVC_classifier, testing_set),"\n")

##    NuSVC_classifier = SklearnClassifier(NuSVC())
##    NuSVC_classifier.train(training_set)
    
##    save_classifier = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/nu_svc.pickle", "wb")
##    pickle.dump(NuSVC_classifier, save_classifier)
##    save_classifier.close()

##    print("Nu Support Vector classifier successfully saved")
##    print("Nu Support Vector accuracy percent:",nltk.classify.accuracy(NuSVC_classifier, testing_set),"\n")

## execution of script starts here, change file name here if needed
trainClassifier('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/all_reviews_by_sent.txt')
