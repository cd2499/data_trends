import happybase
import argparse


# Start program

def get_reviews(input_list):
    reviews = []

    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')

    # Get car male/model/year combinations
    # These were passed as one long argument string to this script

    car_list = []


    # Grab ratings from HBase
    # pull ratings 1 car at a time
    for car_key in input_list:

        # Pull data from HBase
        ratingDict = table.row(car_key, columns=['rating'])
        ratingString = ratingDict['rating:total_review_count'.encode('utf-8')]
        reviews_count = ratingString

    return reviews_count

