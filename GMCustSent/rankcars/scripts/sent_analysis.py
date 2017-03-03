#from nltk.tokenize import RegexTokenizer
import collections
from collections import Counter
from nltk import word_tokenize, sent_tokenize
from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.corpus import stopwords
from nltk.sentiment.util import mark_negation
import nltk.classify.util
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.metrics import precision, recall, f_measure
import nltk.probability
from sklearn import preprocessing, metrics, cross_validation
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.svm import SVC, LinearSVC, NuSVC
##from statistics import mode ##for choosing the best algorithm result
import ast  ##convert the string representation of a list into an actual python list
#import bwt_process_sentence
import bwt_process_sentence_alternate
import happybase
import nltk, re, pprint
import pickle
import random
#import argparse
import string
import spacy
import csv  # To read AspectWeights.csv which contains aspects and their weights (CAC)
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()
import edmunds_reviews as cnt #Sanjana - import script for count of reviews


## remember to start thrift before running this script---->   hbase thrift start -threadpool

#function to remove punctuation using regualr expressions
#def strip_punctuation(word):
#    x = 0
#    for w in word:
#        word[x] = re.sub(r'[^A-Za-z0-9 ]', "", input[x])
#        x += 1
#    return word

#function to extract features from a single sentence, given the sentence as a list of words and the list of features to look for
def extract_features(user_doc, master_features_list, senti_dict):

    #make all words in the sentence lowercase
    lower_words = [word.lower() for word in user_doc]
    no_punc_doc = []

    #remove punctuation
    for word in lower_words:

        #these solutions for removing punctuation do not work with the web interface
        #temp_word = word.translate(word.maketrans({key: None for key in string.punctuation})).strip()
        #temp_word = RegexpTokenizer(r'\w+').tokenize(word)
        #temp_word = word.translate(None, string.punctuation)

        #create a character class from the standard string of punctuation characters
        remove_str = '[' + string.punctuation + ']'
        #replace each punctuation character with the empty string
        temp_word = re.sub(remove_str, '', word)
        #temp_word = word
        if len(temp_word) > 2:
            no_punc_doc.append(temp_word)

    #remove stop words
    filtered_doc = [w for w in no_punc_doc if w not in stopwords.words('english')]

    #remove custom stop words and car makes, models, and years
    filtered_doc = removeNames(filtered_doc)

    #unigrams for this sentence is the list of words without duplicates
    user_doc_by_unigrams = set(filtered_doc) #"set" will create a distinct list of words from user_doc

    #use nltk bigram collocation finder to find bigrams, which may fail if there are no words or very few words
##    try:
##        bigram_finder = BigramCollocationFinder.from_words(filtered_doc, 5)
##        user_doc_by_bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, 5)
##    except ZeroDivisionError:
##        user_doc_by_bigrams = []
    
    #debugging print statement
    #print("in extract", user_doc_by_words)    

    #append _NEG to word tokens that are detected as negated, this seems very inaccurate
    #user_neg_doc_by_words = mark_negation([x for x in user_doc_by_words])
    
    ##dictionary that will have each feature as a key and the value of the feature as the value
    doc_features = {}

    #print sentence and words, showing which words are marked as negated
    #print(user_doc)
    #for word in user_neg_doc_by_words:
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
    tagged_doc = nltk.pos_tag(filtered_doc)
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
        
#function to combines output of feature and aspect extraction
#input: user_review: a tuple that contains the HBase row key and the text of the review
#       nlp: an instance of the spacy english parser
#output: car_agg_dict: a dictionary where the key is the aspect name and
#        the value is a tuple that contains the frequency of that aspect in positive sentences and the frequency of that aspect in negative sentences
def preprocess(user_review, nlp, senti_dict):

    # read master feature list from file
    master_features_file = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/master_feat_list.pickle", "rb")
    master_features_list = pickle.load(master_features_file)
    master_features_file.close()     

    ## output features for debugging purposes
    textFeatures = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/features.txt", "w")
    for feat in master_features_list:
        textFeatures.write(str(feat) + "\n")
    textFeatures.flush()
    textFeatures.close()

    ##dictionary for converting values to pos/neg
##    def f(x):
##        return{
##            '0' : 'neg',
##            '1' : 'neg',
##            #'2' : 'pos',
##            '3' : 'pos',
##            '4' : 'pos'
##        }[x]


    ## open trained classifier    
    classifier_file = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/naivebayes.pickle", "rb")
    classifier = pickle.load(classifier_file)
    classifier_file.close()

    ## list of conjunctions used to split sentences
    ## these conjunctions usually negate the part of the sentence that follows,
    ## so instead split the negated part into a separate sentence
    conjunction_neg = [' nor ',' ,nor ', ' nor, ', ' but ',' ,but ', ' but, ', ' yet ',' ,yet ', ' yet, ']
    ## simplified list of conjunctions used to split sentences
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
    ##print ("BEFORE", user_review[1].decode())
    ## use regualar expressions to replace conjunctions used to split sentences with a period
    conjunction_regex = re.compile('|'.join(map(re.escape, conjunction_neg)))
    conj_2_sentence = conjunction_regex.sub(".", user_review[1].decode('utf-8'))
    ##print("AFTER", conj_2_sentence)     

    ## create list of sentences using nltk sentence tokenizer
    user_review_by_sentence = sent_tokenize(conj_2_sentence)

    named_set = []
    #nlp is already passed into function
    #nlp = spacy.en.English()
    #use spacy to remove named entities
    for item in user_review_by_sentence:
        spacy_doc = nlp(item)
        named_ents = spacy_doc.ents
        ents = [str(e[0]) for e in named_ents]
        names_filtered = [item for item in word_tokenize(item) if item not in ents]
        #append will keep the list of words from each sentence in a nested list
        named_set.append(names_filtered)

    #extract features for each sentence
    userreview_set = [[extract_features(sentence, master_features_list, senti_dict), sentence] for sentence in named_set]                  

    #loop through each sentence for aspect extraction
    car_agg_dict = {}
    #output sentence and aspects extracted from it to file for debugging
    textAspects = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/aspects.txt", "a")
    for each in userreview_set:
        #debugging print statements for now calls to old aspect extraction script 
        #print(bwt_process_sentence.processSentence(each[1])) 
        #print(each[1], classifier.classify(each[0]), bwt_process_sentence.processSentence(each[1]))
        aspect_sentence = ""
        #aspect extraction script expects a sentence as a string, so rebuild sentence string from word tokens
        for i in each[1]:
            aspect_sentence = aspect_sentence + " " + i
        aspectList = bwt_process_sentence_alternate.processSentenceDictionary(aspect_sentence)
        textAspects.write(str(each[1]).encode('ascii'))
        #loop through list of aspects extracted from this sentence
        for item in aspectList:
            itemLine = "\n\t" + str(item)
            textAspects.write(itemLine.encode('ascii'))
            #based on classification of this sentence, either increment the postive sentence frequency or the negative sentence frequency for this aspect
            if classifier.classify(each[0]) == "pos":		
                if item in car_agg_dict:
                    car_agg_dict[item] = (car_agg_dict[item][0] + 1, car_agg_dict[item][1])
                else:
                    car_agg_dict[item] = (1, 0)
            elif classifier.classify(each[0]) == "neg":
                if item in car_agg_dict:
                    car_agg_dict[item] = (car_agg_dict[item][0], car_agg_dict[item][1] + 1)
                else:
                    car_agg_dict[item] = (0, 1)
        textAspects.write("\n".encode('ascii'))
    textAspects.flush()
    textAspects.close()
    return car_agg_dict


#main function of script, conncects to HBase,
#then uses preprocess function to handle analysis of each review,
#finally calculates overall sentiment score for each car and outputs the analysis results
def hbase_connect(input_list):

    review_count_list = [] #Sanjana - store individual count returned from edmunds_review script
    total_review_count = 0  #Sanjana - store a total count of reviews

    #save input_list so it can be read by other scripts
    save_input_list = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/input_list.pickle", "wb")
    pickle.dump(input_list, save_input_list, protocol=2)
    save_input_list.close()
    
    #connect to HBase
    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')

    #clear out output debugging files
    dictFile = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/dictionaryOutput.txt", "w")
    dictFile.close()
    textAspects = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/aspects.txt", "w")
    textAspects.close()
    
    #each element of car_list will be a nested list
    #each nested list will contain:
    #     car_aspect_dict: a dictionary where the key is the aspect name and
    #          the value is a tuple that contains that aspect's frequency in positive sentences and that aspect's frequency in negative sentences
    #     car_key: the HBase row key for that car, which follows the form make|model|year
    #     car_overall_score: the overall sentiment score for the car
    #     aspect_score_dict: a dictionary where the key is the aspect name and
    #          the value is a tuple that contains that aspect's sentiment score and that aspect's total frequency
    #     review_count: the number of reviews analyzed for that car
    car_list = []
#   #input_list is no longer passed as a string
#   input_list = ast.literal_eval(requested_cars) #convert string in list format to actual python list
#   #code for taking command line arguments as input
#   parser = argparse.ArgumentParser()
#   parser.add_argument('cars', nargs='+', type=str)
#   args = parser.parse_args()
#   input_list = args.cars
#   #debugging print statement
#   print("input_list", input_list)

    #create an instance of the spacy English parser
    nlp = spacy.en.English()
    
    #retrieve SentiWordNet data
    senti_data_file = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/senti_dict.pickle', 'rb')
    senti_dict = pickle.load(senti_data_file)
    senti_data_file.close()

    #loop to analyze all reviews for each car
    for car_key in input_list:

        #old format of nested for loop
        ##for key, rvw in data_dict.iteritems():   ##iteritems is python 2.x
	
        #connect to HBase -- hopefully this will keep the connection alive if it takes a long time for this script to execute
        connection = happybase.Connection('localhost')
        
        #Sanjana - get review count per car from edmunds_review script
        review_count = cnt.get_reviews([car_key])

        
        #Sanjana - store review count in a list
        review_count_list.append(int(review_count))
        #Sanjana - sum of the reviews
        total_review_count += int(review_count)
        
        #data is returned as a dictionary with the column name as the key and the data as the value
        data_dict = table.row(car_key, columns=['review'])
        #ratingString = data_dict['review:avg_review_rating'.encode('utf-8')] #Sanjana - Do I need this?
        car_aspect_dict = {}
        #loop through each review found
        for key, rvw in data_dict.items():
            #debugging print statement
            #print(car_key, rvw)
            ret_dict = preprocess((car_key, rvw), nlp, senti_dict)
            #loop through each aspect found in this review and keep track of aspect frequency across reviews
            for x in ret_dict:
                if x in car_aspect_dict:
                    car_aspect_dict[x] = (car_aspect_dict[x][0] + ret_dict[x][0], car_aspect_dict[x][1] + ret_dict[x][1])
                else:
                    car_aspect_dict[x] = ret_dict[x]
        empty_dict = {}
        #add results of feature extraction and aspect extraction for this car to list
        #third and fourth elements are placeholders, actual calculations follow
        car_list.append([car_aspect_dict, car_key, 0.0, empty_dict, review_count])
    #debugging print statement
    #print(car_key, car_aspect_dict)
    #close connection to HBase
    connection.close()

    # We want to change this from frequencies to weights.  CAC

    #total frequency of all aspects is no longer used
    #total_freq = 0
    #loop through list of results and calculate aspect sentiment scores, aspect total frequencies, and car overall sentiment score
    for nested in car_list:
        car_score_dict = nested[0]
        aspect_score_dict = {}
        #print(nested[1])

        weight = {}
        # This is weighting by frequencies of how often the aspect appears in the reviews
        # Open the file
        aspect_weights = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/taxdictionarytrimmed.csv','r') # I need the path to the file, but I don't know what it is yet
        readfile = csv.reader(aspect_weights)

        # Read in the weight            
        for row in readfile:
            if row[0] not in weight:
                #weights are small, so they are all scaled up by a factor of 10
                weight[row[0]] = float(row[2]) * 10.0

        for aspect in car_score_dict:

            # Use the weights from AspectWeights.csv in the calculation
        
            score = float(car_score_dict[aspect][0]) / float(car_score_dict[aspect][0] + car_score_dict[aspect][1])
            score = (score * 4.0) + 1.0  #score is scaled to run from 1 to 5
            freq = car_score_dict[aspect][0] + car_score_dict[aspect][1]
            #total_freq = total_freq + freq
            aspect_score_dict[aspect] = (score, freq)
            
        total_weight = 0.0
        #loop through each aspect and add up scores to calculate car overall score
        for x in aspect_score_dict:

            #calculation based only on aspect frequency
            #weighted_freq = aspect_score_dict[x][1] / total_freq
            #nested[2] = nested[2] + (aspect_score_dict[x][0] * weighted_freq)
            #calculation based on taxonomy weight
            nested[2] = nested[2] + (aspect_score_dict[x][0] * weight[x])
            total_weight = total_weight + weight[x]
            #print("\t" + str(x))

        #keep car overall score on a scale of 1 to 5, with 5 meaning every aspect scored 5
        max_score = 5.0 * total_weight
        #car overall score is stored in car_list
        try:
            nested[2] = ((nested[2] / max_score) * 4.0) + 1.0
        except ZeroDivisionError:
            nested[2] = 0.0
        
        #should not happen, but if car overall score is less than 1, round up to 1
        if nested[2] < 1.0:
            nested[2] = 1.0
            
        #score and total frequency for each aspect are stored in car_list
        nested[3] = aspect_score_dict
        #debugging print statement
        #print("Overall: " + str(nested[2]) + "\n\n")

    #sort car_list based on car overall score
    sorted_list = sorted(car_list, key=lambda car: car[2], reverse=True)
   
    output_ranking = []

    #print statements show up in terminal
    #output_ranking is a list of output lines to display in web interface
    print("Ranking:")
    output_ranking.append('Ranking:')
    output_ranking.append(' ')
    num = 1
    #short output with just the ranking number and overall sentiment score for each car
    for i in sorted_list:
        print(str(num) + ". " + str(i[1]) + "\tOverall: " + str(i[2]) + '\tCount of Reviews: ' + str(i[4])) #Sanjana - added count of reviews
        output_ranking.append(str(num) + ". " + str(i[1]) + '    Overall: ' + str(i[2]) + '\tCount of Reviews: ' + str(i[4])) #Sanjana - added count of reviews
        output_ranking.append(' ')
        num = num + 1
    print("\n\n")
    output_ranking.append('________________________________________')
    output_ranking.append(' ')
    
    num = 1
    #allAspects is a list of column labels for the pandas DataFrame used to graph the results
    allAspects = ['', 'Overall']
    #detailed output with the ranking number and overall sentiment score for each car, and the sentiment score and total frequency for each aspect for each car
    for j in sorted_list:

        print(str(num) + ". " + str(j[1]))
        output_ranking.append(str(num) + '. ' + str(j[1]))
        output_ranking.append(' ')
        
        print("Overall: " + str(j[2]))
        output_ranking.append('Overall: ' + str(j[2]))
        output_ranking.append(' ')

        #make a list of tuples that will be easier to sort
        #each tuple will have an aspect, its sentiment score, and its total frequency
        item_aspects = [(key, value[0], value[1]) for (key, value) in j[3].items()]
        #sort the aspects for this car based on total frequency
        sorted_aspects = sorted(item_aspects, key= lambda a: a[2], reverse=True)
        #only keep the top 10 aspects
        sorted_aspects = sorted_aspects[:10]
        
        #output the aspect, its sentiment score, and its total frequency
        for k, s, f in sorted_aspects:
            #add each aspect displayed to the list of all aspects only once
            if str(k) not in allAspects:
                allAspects.append(str(k))
            print("\t" + str(k) + ": Score: " + str(s) + ", Frequency: " + str(f))
            output_ranking.append('    ' + str(k) + ': Score: ' + str(s) + ", Frequency: " + str(f))
            output_ranking.append(' ')

        print('')
        output_ranking.append('________________________________________')
        num = num + 1
    print("\n")   
    output_ranking.append(' ')

    #arrList is a two-dimensional array that holds all data that will be used in the pandas DataFrame
    arrList = [allAspects]
    #loop through the data for each car
    for car in sorted_list:
        #the row for each car starts with the car's HBase row key and the car's overall sentiment score
        carRow = [str(car[1]), float(car[2])]
        #loop through the list of all aspects to display for each car
        for a in allAspects[2:]:
            #retrieve the score for this aspect, or 0.0 if it was not found for this car
            if a in car[3]:
                carRow.append(float(car[3][a][0]))
            else:
                carRow.append(0.0)
        arrList.append(carRow)
    #convert arrList into a numpy two-dimensional array of strings
    carData = np.array(arrList)
    #convert sentiment score elements back to float data type
    numericData = np.array(carData[1:, 1:], dtype=float)
    #load panadas DataFrame with data
    df = pd.DataFrame(data=numericData, index=carData[1:, 0], columns=carData[0, 1:])
    #draw graph of data
    graph = df.plot.bar()
    #display graph
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    #plt.show()
    #save graph
    fig = graph.get_figure()
    fig.set_size_inches(20, 10)
    fig.savefig('/home/sysadmin/gmrepo/GMCustSent/rankcars/static/rankcars/content/bar.png', bbox_inches='tight')
    #graph = plt.figure()
    #graph.savefig('/home/sysadmin/gmrepo/GMCustSent/rankcars/static/rankcars/content/bar.png')
    #plt.savefig('/home/sysadmin/gmrepo/GMCustSent/rankcars/static/rankcars/content/bar.png')
    
    return output_ranking, total_review_count #Sanjana - added total review count

    #first version of overall score calculation
    #very basic overall score calculation
    #overall_score = total_score / len(aspect_score_dict)
    #aspect_score_dict['overall'] = overall_score

#hbase_connect()



