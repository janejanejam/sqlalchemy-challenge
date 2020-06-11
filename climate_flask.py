# Import libraries and dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from collections import OrderedDict
import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# # Initialize database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Set the Base to the automap_base() sqlalchemy class
Base = automap_base()

# use `.prepare()` to reflect the Python classes from the tables found in the {engine}
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Initialize Flask app
app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    """List all routes that are available"""
    return (
        f"<strong>Climate Data for Honolulu, Hawaii Area from 2010-01-01 to 2017-08-23</strong> <br><br>"

        f"<strong>Available Routes:</strong> <br><br>"
        f"/api/v1.0/precipitation<br>"
        f"<em>Shows last 12 months of precipitation data.</em> <br><br>"

        f"/api/v1.0/stations<br/>"
        f"<em>Shows list of climate stations.</em> <br><br>"

        f"/api/v1.0/tobs<br/>"
        f"<em>Shows temperature observations (TOBS) for last 12 months of most active station: 'WAIHEE 837.5, HI US'.</em> <br><br>"

        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"<em>Shows list of minimum temperature, average temperature and max temperature for given start date (yyyy-mm-dd).</em><br><br>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"<em>Shows list of minimum temperature, average temperature and max temperature for given start-end range of dates (yyyy-mm-dd/yyyy-mm-dd).</em><br><br>"
    )

# Define what to do when a user hits the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    """Return Dates and Temp from the last year."""
    results = (
        session.query(Measurement.date, Measurement.prcp).
        filter(Measurement.date >= dt.date(2016, 8, 23)).
        filter(Measurement.date <= dt.date(2017, 8, 23)).
        order_by(Measurement.date).all()
        )

    session.close()

    # Convert query results into a dictionary
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_list.append(precipitation_dict)
    
    # Create JSONified list
    return jsonify(precipitation_list)

# Define what to do when a user hits the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    """Return list of stations from dataset."""
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    
    # Convert query results into a dictionary
    stations_list = []
    for id, station, name, latitude, longitude, elevation in results:
        stations_dict = OrderedDict()
        stations_dict["Id"] = id
        stations_dict["Station"] = station
        stations_dict["Name"] = name
        stations_dict["Latitude"] = latitude
        stations_dict["Longitude"] = longitude
        stations_dict["Elevation"] = elevation
        stations_list.append(stations_dict)
    
    # Create JSONified list
    response = app.response_class(
        response=json.dumps(stations_list, indent=2),
        status=200,
        mimetype='application/json'
    )
    return response

# Define what to do when a user hits the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperature():
    print("Server received request for 'Temperature' page...")
    """Return list of temperature from dataset."""
    results = (session.query(Measurement.date, Measurement.tobs).   
    filter(Measurement.date >= dt.date(2016, 8, 23)).
    filter(Measurement.date <= dt.date(2017, 8, 23)).
    filter(Station.name == 'WAIHEE 837.5, HI US').
    order_by(Measurement.date).all()
)
    session.close()

    # Convert query results into a dictionary
    temperature_list = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict[date] = tobs
        temperature_list.append(temperature_dict)
    
    # Create JSONified list
    return jsonify(temperature_list)

# Define what to do when a user hits the /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def start_date(start):
    print("Server received request for 'Start Date' page...")
    """Return calculations of temperature avg, min, max from start date."""
    results = (
        session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).
        filter(Measurement.date >= start).all()
)
    session.close()

    # Convert query results into a dictionary
    start_date_list = []
    for min, avg, max in results:
        start_date_dict = {}
        start_date_dict["Min"] = min
        start_date_dict["Avg"] = avg
        start_date_dict["Max"] = max
        start_date_list.append(start_date_dict)
    
    # Create JSONified list
    return jsonify(start_date_list)

# Define what to do when a user hits the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    print("Server received request for 'Start and End Date' page...")
    """Return calculations of temperature avg, min, max from start to end date."""
    results = (
        session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
)
    session.close()

    # Convert query results into a dictionary
    start_end_date_list = []
    for min, avg, max in results:
        start_end_date_dict = {}
        start_end_date_dict["Min"] = min
        start_end_date_dict["Avg"] = avg
        start_end_date_dict["Max"] = max
        start_end_date_list.append(start_end_date_dict)
    
    # Create JSONified list
    return jsonify(start_end_date_list)

if __name__ == "__main__":
    app.run(debug=True)
