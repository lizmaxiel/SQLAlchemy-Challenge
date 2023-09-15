# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )

# Route: Precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def get_precipitation_data():
    # Calculate the date one year from the last data point
    prev_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year_date).all()

    # Convert the query results into a dictionary
    precip = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precip)

# Route: List of stations
@app.route("/api/v1.0/stations")
def get_stations():
    # Query and list all stations
    stations = session.query(Station.station).all()
    stations_list = [station[0] for station in stations]

    return jsonify(stations=stations_list)

# Route: Temperature observations for the most active station in the last year
@app.route("/api/v1.0/tobs")
def get_temperature_observations():
    # Calculate the date one year from the last data point
    prev_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations for the most active station
    temperature_observations = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year_date).all()

    # Convert the query results into a list
    temps = [temp[0] for temp in temperature_observations]

    return jsonify(temps=temps)

# Route: Temperature statistics for a specified start or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def get_temperature_stats(start=None, end=None):
    # Define the list of aggregate functions
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Query temperature statistics for a specified start date
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # Query temperature statistics for a specified start-end date range
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert the query results into a list of dictionaries
    temp_stats = [{"Min Temp": result[0], "Avg Temp": result[1], "Max Temp": result[2]} for result in results]

    return jsonify(temp_stats)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)