from flask import Flask, render_template, g, jsonify, request
import config
from sqlalchemy import create_engine
import MySQLdb
import json
import pandas as pd
import sklearn
import pickle
import re
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn import *


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
    sql_routes = """SELECT route_id, route_name, routename_and_id FROM dublin_bus.routes"""

    engine1 = get_db()
    rows1 = engine1.execute(sql_routes).fetchall()
    res1 = [dict(row.items()) for row in rows1]
    data1 = json.dumps(res1)
    route_data = json.loads(data1)

    sql_stops = """SELECT * FROM dublin_bus.stops"""

    engine2 = get_db()
    rows2 = engine2.execute(sql_stops).fetchall()
    res2 = [dict(row.items()) for row in rows2]
    data2 = json.dumps(res2)
    stop_data = json.loads(data2)

    return render_template("index.html", route_data = route_data, stop_data = stop_data)

@app.route("/routes", methods=['GET', 'POST'])
def routes():
    chosenroute = request.form.get('chosenroute')
    chosenorigin = request.form.get('chosenorigin')
    chosendestination = request.form.get('chosendestination')
    chosenday = request.form.get('chosenday')
    chosentime = request.form.get('chosentime')
    chosentemp = request.form.get('chosentemp')
    chosenhumid = request.form.get('chosenhumid')
    chosenpres = request.form.get('chosenpres')
    # run the prediction model
    df = pd.read_csv('/var/www/FlaskApp/FlaskApp/cleangps.csv')

    # Delete letters from bus route and add only the chosen route to dataframe
    bus = re.sub('[^0-9]','', chosenroute)
    dataframe = df[(df.LineID == int(bus))]
    
    array = dataframe.values
    X = array[:, 0:7]
    Y = array[:, 7]
    test_size = 0.33
    seed = 7
    X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(X, Y, test_size=test_size, random_state=seed)
    # Fit the model on 33%
    model = RandomForestRegressor()
    model.fit(X_train, Y_train)
    # save the model to disk
    filename = 'var/www/FlaskApp/FlaskApp/finalized_model.sav'
    pickle.dump(model, open(filename, 'wb'))
    # calculating the average time between two adjacent stops
    chosend = float(re.search(r'\d+', chosenday).group())
    chosent = float(re.search(r'\d+', chosentime).group())
    chosenro = float(re.search(r'\d+', chosenroute).group())
    chosenro1 = str(re.search(r'\d+', chosenroute).group())
    # chosenro1=chosenroute.split(":")
    # value= str(chosenro1[0])
    chosenorig = float(re.search(r'\d+', chosenorigin).group())
    chosendest = float(re.search(r'\d+', chosendestination).group())
    data = []
    for i in range(0, len(X)):
        if X[i][0] == chosenro and X[i][2] == chosent and X[i][3] == chosend:
            data.append(X[i])

    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))
    # calculating the time between adjacent stops
    result = loaded_model.predict(data)
    total = 0
    for j in range(len(result)):
        total += (result[j])
    seconds = (total // len(result))

    # calculating the number of stops between origin and destination

    df = pd.read_csv('/var/www/FlaskApp/FlaskApp/stops.csv')

    arr = df.values
    list = []
    for j in range(len(arr)):
        if (arr[j][0]) == chosenorig or (arr[j][0]) == chosendest:
            list.append(arr[j])

    list1 = []
    for i in range(len(list)):
        if (list[i][4]) == chosenro1:
            list1.append(list[i])
    nums = abs(list1[0][6] - list1[1][6])
    second = seconds * nums
    times = str(datetime.timedelta(seconds=second))
 
    # create variables for time +1 hour and time -1hour
    chosentime1 = chosent + 1
    chosentime2 = chosent - 1
    data1 = []
    for i in range(0, len(X)):
        if X[i][0] == chosenro and X[i][2] == chosentime1 and X[i][3] == chosend:
            data1.append(X[i])

    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))

    # calculating the time between adjacent stops
    result1 = loaded_model.predict(data1)
    total1 = 0
    for j in range(len(result1)):
        total1 += (result1[j])
    seconds = (total1 // len(result1))
    second1 = seconds * nums
    time1 = str(datetime.timedelta(seconds=second1))

    # model 3
    data2 = []
    for i in range(0, len(X)):
        if X[i][0] == chosenro and X[i][2] == chosentime1 and X[i][3] == chosend:
            data2.append(X[i])

    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))

    # calculating the time between adjacent stops
    result2 = loaded_model.predict(data2)
    total2 = 0
    for j in range(len(result2)):
        total2 += (result2[j])
    seconds = (total2 // len(result2))
    second2 = seconds * nums
    time2 = str(datetime.timedelta(seconds=second2))

    sql_routes = """SELECT route_id, route_name, routename_and_id FROM dublin_bus.routes"""

    engine1 = get_db()
    rows1 = engine1.execute(sql_routes).fetchall()
    res1 = [dict(row.items()) for row in rows1]
    data1 = json.dumps(res1)
    route_data = json.loads(data1)

    sql_stops = """SELECT * FROM dublin_bus.stops"""

    engine2 = get_db()
    rows2 = engine2.execute(sql_stops).fetchall()
    res2 = [dict(row.items()) for row in rows2]
    data2 = json.dumps(res2)
    stop_data = json.loads(data2)

    chosent = int(chosent)
    chosentime1 = int(chosentime1)
    chosentime2 = int(chosentime2)

    data = [(chosent,  times), (chosentime1, time1), (chosentime2, time2)]

    # return data

    return render_template("display.html", data=data, chosenorigin=chosenorigin, chosendestination=chosendestination, chosenro1= chosenro1, route_data = route_data, stop_data = stop_data, times= times,)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
