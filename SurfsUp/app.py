#################################################
# Import the dependencies.
#################################################

# Import sqlalchemy dependencies
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import numpy and datetime
import numpy as np
import datetime as dt

# Import flask
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def home():
    return (
        f"Welcome to the main page!<br/>"
        f"Here are the available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create our session (link) from Python to the DB
    session = Session(engine)
    
    # find most recent date
    ordered = session.query(Measurement).order_by(Measurement.date.desc()).first()
    most_recent_date = ordered.date

    # calculate a year pior to most recent date
    one_year_back = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=366)
    
    # query precipitation in the last 12 months of data
    results =  session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date.between(one_year_back, most_recent_date)).all()

    # close Session
    session.close() 

    # create empty variable to store results
    precepitation=[]

    # add date (key) and precipitation (value) from results to dict and append to precipitation variable
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precepitation.append(precipitation_dict)

    return jsonify(precepitation)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # create our session (link) from Python to the DB
    session = Session(engine)

    # query
    results = session.query(Station.station).all()

    # close Session
    session.close() 

    # put results into a list
    stations_list = list(np.ravel(results))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # create our session (link) from Python to the DB
    session = Session(engine)

    # find most active station
    most_active_query = session.query(Measurement.station, func.count(Measurement.station).label('count')).group_by(Measurement.station).order_by(text('count DESC')).first()
    most_active_station = most_active_query[0]

    # find last 12 months of data
    ordered = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = ordered.date
    one_year_back = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=366)

    # query last 12 months for most active station
    temps = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).\
    filter(Measurement.date >=one_year_back)

    # close Session
    session.close() 
    
    # create empty variable
    temps_all = []

    # get date and temp
    for date, temp in temps:
        temps_dict = {}
        temps_dict[date] = temp
        temps_all.append(temps_dict)

    return jsonify(temps_all)


@app.route("/api/v1.0/<start>")
def start_date(start):
    # create our session (link) from Python to the DB
    session = Session(engine)

    # query
    temps = session.query(func.min(Measurement.tobs),
                  func.max(Measurement.tobs),
                  func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()


    # close Session
    session.close() 
    
    temps_dict = {}
    temps_dict["Min"] = temps[0][0]
    temps_dict["Max"] = temps[0][1]
    temps_dict["Avg"] = temps[0][2]
   
    return jsonify(temps_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # create our session (link) from Python to the DB
    session = Session(engine)
   
    temps = session.query(func.min(Measurement.tobs),
                          func.max(Measurement.tobs),
                          func.avg(Measurement.tobs)).\
                            filter(Measurement.date.between(start,end)).all()

 
    # close Session
    session.close() 
    
    temps_dict = {}
    temps_dict["Min"] = temps[0][0]
    temps_dict["Max"] = temps[0][1]
    temps_dict["Avg"] = temps[0][2]
   
    return jsonify(temps_dict)

if __name__ == "__main__":
    app.run()