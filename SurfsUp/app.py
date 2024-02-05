# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

from pathlib import Path
from flask import Flask, jsonify

#################################################
# Functions
#################################################

def create_JSON_from_dict(df):
    result={}
    for index, row in df.iterrows():
        result[index]=dict(row)   
    return jsonify(result)

def create_JSON_date_range(start, end=None):
    session = Session(engine)

    if end is None:
        fr_start_date_query = session.query(
                func.max(Measurement.tobs).label("TMAX"),
                func.avg(Measurement.tobs).label("TAVG"),
                func.min(Measurement.tobs).label("TMIN")
                ).filter(Measurement.date >= start).all()
    else:
        fr_start_date_query = session.query(
                func.max(Measurement.tobs).label("TMAX"),
                func.avg(Measurement.tobs).label("TAVG"),
                func.min(Measurement.tobs).label("TMIN")
                ).filter(Measurement.date >= start, Measurement.date <= end).all()

    fr_start_date_query = pd.DataFrame(fr_start_date_query, columns=['TMAX', 'TAVG', 'TMIN'])
    result = fr_start_date_query.iloc[0].to_dict()

    session.close()
    return jsonify(result)

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
database_path = Path("../Resources/hawaii.sqlite")
if database_path.is_file(): # check that the path is correct
    engine = create_engine(f"sqlite:///{database_path}")
else:
    print(f'The file {database_path} does not exist')
 
# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Create a session
session = Session(engine)

# Find the most recent date in the data set.
Last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
Last_date = dt.date.fromisoformat(Last_date_str)

# Calculate the date one year from the last date in data set.
Prev_Last_date = dt.date(Last_date.year-1,Last_date.month,Last_date.day)

# print the dates
print(f"Most Recent Data: {Last_date_str}, and a year before: {Prev_Last_date}")

################################################# Get the measurement data
ann_prcp_query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Prev_Last_date)).\
    order_by(Measurement.date).all()

ann_prcp_df = pd.DataFrame(ann_prcp_query, columns=['date', 'prcp'])
ann_prcp_df.set_index('date', inplace=True)

## get the summary of the various dates
ann_prcp_max   = ann_prcp_df.groupby(["date"]).max()["prcp"]
ann_prcp_min   = ann_prcp_df.groupby(["date"]).min()["prcp"]
ann_prcp_sum   = ann_prcp_df.groupby(["date"]).sum()["prcp"]
ann_prcp_count = ann_prcp_df.groupby(["date"]).count()["prcp"]

ann_prcp_dict = {"Max": round(ann_prcp_max, 2), "Min": round(ann_prcp_min, 2),
                 "Sum": round(ann_prcp_sum, 2), "Count":round(ann_prcp_count, 2)}

ann_prcp_summary_df = pd.DataFrame(ann_prcp_dict)

################################################# Get the station information
stations_query = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
stations_df = pd.DataFrame(stations_query, columns=['station', 'name','latitude','longitude','elevation'])
stations_df.set_index('station', inplace=True) 

################################################# Get some summary statistics for the most active station
most_active_stations_query = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc())

all_most_active_stations = most_active_stations_query.all()
most_active_station_id = most_active_stations_query.first()[0]

# print the most active station
print(f"Most Active Station: {most_active_station_id}")

ann_tobs_query = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Prev_Last_date), Measurement.station == most_active_station_id).\
    order_by(Measurement.date).all()

ann_tobs_df = pd.DataFrame(ann_tobs_query, columns=['date', 'tobs'])
ann_tobs_df.set_index('date', inplace=True)

# Close Session
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    return create_JSON_from_dict(ann_prcp_summary_df)

#################################################
@app.route("/api/v1.0/stations")
def stations():
    return create_JSON_from_dict(stations_df)

#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    return create_JSON_from_dict(ann_tobs_df)

#################################################
@app.route("/api/v1.0/<start>")
def fromstartdate(start):
    return create_JSON_date_range(start, end=None)

#################################################
@app.route("/api/v1.0/<start>/<end>")
def fromrange(start, end):
    return create_JSON_date_range(start, end)

#################################################
if __name__ == "__main__":
    app.run(debug=True)
