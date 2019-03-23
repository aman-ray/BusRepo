from flask import Flask, render_template, g, jsonify, request
import config
from sqlalchemy import create_engine
#import MySQLdb
import json
import pandas as pd
import sklearn
import pickle
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn import model_selection
from sklearn.model_selection import train_test_split
import datetime
app = Flask(__name__)

    
def connect_to_database():
    db_str = "mysql+mysqldb://{}:{}@{}:{}/{}"
    engine = create_engine(db_str.format(config.USER,
                                        config.PASSWORD,
                                        config.URI,
                                        config.PORT,
                                        config.DB),
                           echo=True)
    return engine

def get_db():
    engine = getattr(g, 'engine', None)
    if engine is None:
        engine = g.engine = connect_to_database()
    return engine

@app.route("/")
def main():
    with open('static/dublinbus_routes.json',encoding='utf-8') as data_file:    
        json_file_routes = json.load(data_file)
        
    with open('static/routes.json') as data_file:
        json_routes = json.load(data_file)
        
    with open('static/routes_and_stops.json') as data_file:
        json_file_stops = json.load(data_file)
    
    return render_template("index.html", json_file_routes = json_file_routes, json_file_stops = json_file_stops, json_routes = json_routes)

@app.route("/routes", methods=['GET','POST'])
def routes():
    chosenroute = request.form.get('chosenroute')

    chosenorigin = request.form.get('chosenorigin')
    chosendestination = request.form.get('chosendestination')
    chosenday = request.form.get('chosenday')
    chosentime = request.form.get('chosentime')
    chosentemp = request.form.get('chosentemp')
    chosenhumid = request.form.get('chosenhumid')
    chosenpres = request.form.get('chosenpres')
    #run the prediction model
    # dataframe = pd.read_csv('cleangps.csv')
    # array = dataframe.values
    # X = array[:,0:7]
    # Y = array[:,7]
    # test_size = 0.33
    # seed = 7
    # X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=test_size, random_state=seed)
    # # Fit the model on 33%
    # model = RandomForestRegressor()  
    # model.fit(X_train, Y_train)
    # save the model to disk
    filename = 'finalized_model.sav'
    pickle.dump(model, open(filename, 'wb'))
    #calculating the average time between two adjacent stops
    chosend=float(re.search(r'\d+', chosenday).group())
    chosent=float(re.search(r'\d+', chosentime).group())
    chosenro=float(re.search(r'\d+', chosenroute).group())
    chosenorig =float(re.search(r'\d+', chosenorigin).group())
    chosendest=float(re.search(r'\d+', chosendestination).group())
#    df = chosent
#    chosentime1 = df.astype(str).apply(lambda x: pd.to_datetime(x, format='%H%M'))]

    chosentime1 = chosent + 1
    chosentime2 = chosent - 1
#    chosent1 = str(chosent)
#    dt = datetime.datetime.strptime( chosent1, '%H.%M' )
#    chosentime1 = dt - datetime.timedelta(0, 1 * 60 * 60)
#    chosent1 = str(chosent)
#    dt = datetime.datetime.strptime( chosent1, '%H.%M' )
#    chosentime2 = dt + datetime.timedelta(0, 1 * 60 * 60)

#MODEL RUN 1 
    data =[]
    for i in range(0,len(X)):
            if X[i][0]==chosenro and X[i][2]==chosent and X[i][3]==chosend:
                data.append(X[i])
        
    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))
    #calculating the time between adjacent stops
    result = loaded_model.predict(data)
    total = 0
    for j in range(len(result)):
        total += (result[j])
    seconds = (total//len(result))
    time = str(datetime.timedelta(seconds=seconds))
    
    
#    MODEL RUN 2
    data2 =[]
    for i in range(0,len(X)):
            if X[i][0]==chosenro and X[i][2]==chosentime1 and X[i][3]==chosend:
                data2.append(X[i])
        
    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))
    #calculating the time between adjacent stops
    result2 = loaded_model.predict(data2)
    total2 = 0
    for j in range(len(result2)):
        total2 += (result2[j])
    seconds = (total2//len(result2))
    time2 = str(datetime.timedelta(seconds=seconds))
    
    
#    MODEL RUN 3
    data3 =[]
    for i in range(0,len(X)):
            if X[i][0]==chosenro and X[i][2]==chosentime2 and X[i][3]==chosend:
                data3.append(X[i])
        
    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))
    #calculating the time between adjacent stops
    result3 = loaded_model.predict(data3)
    total3 = 0
    for j in range(len(result3)):
        total3 += (result3[j])
    seconds = (total3//len(result3))
    time3 = str(datetime.timedelta(seconds=seconds))

    with open('static/routes.json') as data_file:
        json_file_routes = json.load(data_file)
        
    with open('static/routes.json') as data_file:
        json_routes = json.load(data_file)
        
    with open('static/routes_and_stops.json') as data_file:
        json_file_stops = json.load(data_file)
    
    return render_template("display.html", json_file_routes = json_file_routes, json_file_stops = json_file_stops, json_routes = json_routes, chosenroute = chosenroute, chosenorigin = chosenorigin, chosendestination = chosendestination, chosent = chosent, chosentime1 = chosentime1, chosentime2 = chosentime2, time=time, time2 = time2, time3 = time3)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        


if __name__ == "__main__":
    app.run(debug=True)
