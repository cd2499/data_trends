import happybase
import sqlite3


def loadDjangoMake(car_list):
    conn = sqlite3.connect('./db.sqlite3')
    c = conn.cursor()

    ## truncate and reload tables
    c.execute("DELETE FROM rankcars_carmake;")

    ## get distinct car makes 
    distinct_carmakes = [] 
    
    for car in car_list:
        distinct_carmakes.append(car[0])
    
    distinct_carmakes = list(set(distinct_carmakes))

    for each in distinct_carmakes:
        c.execute('INSERT INTO rankcars_carmake(name) VALUES ("' + each + '");')

    conn.commit()
    conn.close() 



def loadDjangoModel(car_list):
    
    conn = sqlite3.connect('./db.sqlite3')
    c = conn.cursor()

    ## truncate and reload tables
    c.execute("DELETE FROM rankcars_carmodel;")

    distinct_carmodels = []
    for car in car_list:

        carmake = car[0]
	carmodel = car[1]

        ## get carmake surrogate key from carmake table
        sqlquery = ' SELECT ID '
        sqlquery += 'FROM rankcars_carmake '
        sqlquery += 'WHERE name = "' + carmake + '";'
        
        makeid = c.execute(sqlquery).fetchone()
        fk_carmakeid = makeid[0]
 
        if (carmodel, fk_carmakeid) not in distinct_carmodels:
            distinct_carmodels.append((carmodel, fk_carmakeid))
            #print(carmodel, fk_carmakeid)
    
    for rec in distinct_carmodels:
        c.execute('INSERT INTO rankcars_carmodel(name, carmake_id) VALUES("' + rec[0] + '", ' + str(rec[1]) + ')')   
   
    conn.commit()
    conn.close() 




def loadDjangoYear(car_list):
    
    conn = sqlite3.connect('./db.sqlite3')
    c = conn.cursor()

    ## truncate and reload tables
    c.execute("DELETE FROM rankcars_caryear;")

    distinct_year = [] 
    
    for car in car_list:
        carmake = car[0]
        carmodel = car[1]
        caryear = car[2]

        sqlquery = " SELECT model.id "
        sqlquery += "FROM rankcars_carmodel model "
        sqlquery += "INNER JOIN "
        sqlquery += "     rankcars_carmake make ON model.carmake_id = make.id "
        sqlquery += "WHERE model.name ='" + carmodel + "' "
        sqlquery += "AND make.name = '" + carmake + "'"

        modelid = c.execute(sqlquery).fetchone()
        if (caryear, modelid[0]) not in distinct_year:
            distinct_year.append((caryear, modelid[0]))
            c.execute("INSERT INTO rankcars_caryear (name, carmodel_id) VALUES('" + caryear + "'," + str(modelid[0]) + ")")
    
    conn.commit()
    conn.close() 




def getTableKeys():
    connection = happybase.Connection('localhost')
    table = connection.table('customer_review_sentiment')

    car_list = []

    for row_key, data_dict in table.scan(columns=['review']):
	#print(row_key.split('|'))
        car_list.append(row_key.split('|'))

    loadDjangoMake(car_list)
    loadDjangoModel(car_list)
    loadDjangoYear(car_list)

getTableKeys()
