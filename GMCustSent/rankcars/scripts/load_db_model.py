import happybase
import sqlite3


def loadDjangoModel(car_list):
    conn = sqlite3.connect('../../db.sqlite3')
    c = conn.cursor()

    ## Just dropping and recreating table. This is intentional 
    ##c.execute('DROP TABLE IF EXISTS car_list;')

    ##c.execute('CREATE TABLE car_list (car_make VARCHAR NOT NULL, car_model VARCHAR NOT NULL, car_year INT NOT NULL, PRIMARY KEY(car_make, car_model, car_year));')

    ## truncate and reload tables
    c.execute("select * from carmake")

    ## load car make into car_make table
    distinct_carmakes = [] 
    for car in car_list:
        distinct_carmakes.append(car[0])
        #c.execute('INSERT INTO  car_list values (?,?,?);', car)

    distinct_carmakes = set(distinct_carmakes)
#    c.execute('INSERT INTO rankcars_carmake VALUES (?);', distinct_carmakes)

    conn.commit()
    conn.close() 


def getTableKeys():
    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')

    car_list = []

    for row_key, data_dict in table.scan(columns=['review']):
        car_list.append(row_key.split('|'))

    loadDjangoModel(car_list)


getTableKeys()
