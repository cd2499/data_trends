# Coded by Catherie Celice
# for Senior Project Fall 2016
# GM Customer Sentiment group

# put library calls here



import edmunds_reviews as cnt  #import script for count of reviews
import happybase
import argparse

# Start program


def get_ratings(input_list):

    ratings = []
    review_count_list = [] #store individual count returned from edmunds_review script
    total_review_count = 0  #store a total count of reviews
    cars_ranked = []
    cars_unranked = []

    #connect to HBase
    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')
    
    # Get car make/model/year combinations
    # These were passed as a list of HBase row keys to this script

    #code for taking car make/model/year combinations as command line arguments
    #car_list = []
    #parser = argparse.ArgumentParser()
    #parser.add_argument('cars', nargs='+', type=str)
    #args = parser.parse_args()
    #input_list = args.cars


    # Grab ratings from HBase
    # pull ratings 1 car at a time
    for car_key in input_list:
        
        # Connect to HBase -- hopefully this keeps the connection alive even if this script takes a long time to execute
        connection = happybase.Connection('localhost')
        
        #get review count per car from edmunds_review script
        review_count = cnt.get_reviews([car_key])

        #store review count in a list
        review_count_list.append(int(review_count))
        #sum of the reviews
        total_review_count += int(review_count)
        
        # Pull data from HBase    
        ratingDict = table.row(car_key, columns=['rating'])
        ratingString = ratingDict['rating:avg_review_rating'.encode('utf-8')]

        # Convert to floats so sorting is based on numerical order, not lexical order
        f = float(ratingString)
        ratings.append(f)


        
        

    # Order the cars by average ratings

    length = len(ratings)

    #create list of tuples, where each tuple contains the car make/model/year and rating
    ranked = []
    for i in range(0, length):
        ranked.append((input_list[i], ratings[i], review_count_list[i]))

    #sort list of tuples based on rating
    sortedlist = sorted(ranked, key=lambda x: x[1], reverse=True)
    
    #output is returned as a list of lines of output text
    output_ranking = []
    output_ranking.append('Ranking:')
    output_ranking.append(' ')

    #loop through sorted list to number each car in order
    count = 1
    for j in sortedlist:
        print(str(count) + '. ' + str(j[0]) + '\tAverage: ' + str(j[1]) + '\tCount of Reviews: ' + str(j[2]))
        output_ranking.append(str(count) + '. ' + str(j[0]) + '    Average: ' + str(j[1]) + '     Count of Reviews: ' + str(j[2]))
        count = count + 1
    
    output_ranking.append(' ')
    return output_ranking, total_review_count

    #code for sorting cars without the built in sort function
    #if length > 1:

        #for i in xrange(1, length):
        

            #for j in xrange(i+1, length):
                #if ratings[j] > ratings[i]:
                    #temp = ratings[j]
                    #ratings[j] = ratings[i]
                    #ratings[i] = temp

                    #tempcar = input_list[j]
                    #input_list[j] = input_list[i]
                    #input_list[i] = tempcar

    #output car make/model/year and rating in sorted order
    #for i in xrange(1, length):
        #print()
        #print '%s ..... %d' % (input_list[i], ratings[i])
        #print()
    
                
#this script is called from the web interface, it is not executed directly
#get_ratings()

