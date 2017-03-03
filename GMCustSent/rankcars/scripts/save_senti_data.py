import csv
import pickle
import string
from nltk.corpus import wordnet as wn

#this script is intended to be run from the python command line

def save_senti_data():

    #read SentiWordNet data file to get list of positive and negative sentiment polarities for each word with a given part of speech
    senti_file = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/SentiWordNet_3.0.0_20130122.txt', 'r')
    data_file = csv.reader(senti_file, delimiter='\t')

    senti_dict = {}

    for row in data_file:
        #each row can contain multiple words, so handle each separately
        word_list = string.split(row[4], ' ')
        for word in word_list:
            #each word ends with # followed by the definition number
            #find end of word
            i = string.find(word, '#')
            #if the word exists, keep only the word
            if i > 0:
                word = word[:i]
                #key for dictionary is word.part_of_speech
                key = word + '.' + row[0]
                #value for dictionary is a list of tuples that contain the positive sentiment polarity and the negative sentiment polarity for one definition of the word with a given part of speech
                if key in senti_dict:
                    senti_dict[key].append((float(row[2]), float(row[3])))
                else:
                    senti_dict[key] = []
                    senti_dict[key].append((float(row[2]), float(row[3])))

    #save SentiWordNet data so it can be used later
    save_senti_dict = open('/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/senti_dict.pickle', 'wb')
    pickle.dump(senti_dict, save_senti_dict, protocol=2)
    save_senti_dict.close()

    #debugging print statement
    #print(senti_dict)

#execute script
save_senti_data()
