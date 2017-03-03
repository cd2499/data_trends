import happybase
import pickle


# Start program

def car_reviews():

    #retrieve input_list used by sent_analysis.py

    input_list_file = open("/home/sysadmin/gmrepo/GMCustSent/rankcars/scripts/input_list.pickle", "rb")
    input_list = pickle.load(input_list_file)
    input_list_file.close()

    review_list = []

    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')
    output_text = []

    for car_key in input_list:

        # Pull data from HBase
        ratingDict = table.row(car_key, columns=['review'])
        # ratingString = ratingDict['rating:total_review_count'.encode('utf-8')]
        # reviews_list = ratingDict

        data_dict = table.row(car_key, columns=['review'])
        output_text.append("Reviews for " + str(car_key))

        for key, rvw in data_dict.items():
            output_text.append(rvw)
            output_text.append('________________________________________')

    print(output_text)
    return output_text
