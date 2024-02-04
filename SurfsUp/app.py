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
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
database_path = Path("../Resources/hawaii.sqlite")
if database_path.is_file():
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

# Create a session
session = Session(engine)

# Find the most recent date in the data set.
Last_date_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
Last_date = dt.date.fromisoformat(Last_date_str)

# Calculate the date one year from the last date in data set.
Prev_Last_date = dt.date(Last_date.year-1,Last_date.month,Last_date.day)

# Perform a query to retrieve the data and precipitation scores
ann_prcp = session.query(Measurement.date,func.max(Measurement.prcp)).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Prev_Last_date)).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
df = pd.DataFrame(ann_prcp, columns=['date', 'prcp'])
df.set_index('date', inplace=True)

# Use Pandas to calcualte the summary statistics for the precipitation data

ann_prcp_query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Prev_Last_date)).\
    order_by(Measurement.date).all()

ann_prcp_df = pd.DataFrame(ann_prcp_query, columns=['date', 'prcp'])
ann_prcp_df.set_index('date', inplace=True)

ann_prcp_max = ann_prcp_df.groupby(["date"]).max()["prcp"]
ann_prcp_min = ann_prcp_df.groupby(["date"]).min()["prcp"]
ann_prcp_sum = ann_prcp_df.groupby(["date"]).sum()["prcp"]
ann_prcp_count = ann_prcp_df.groupby(["date"]).count()["prcp"]

ann_prcp_dict = {"Max": round(ann_prcp_max, 2), "Min": round(ann_prcp_min, 2),
                 "Sum": round(ann_prcp_sum, 2), "Count":round(ann_prcp_count, 2)}

ann_prcp_summary_df = pd.DataFrame(ann_prcp_dict)

#################################################
stations_query = session.query(Station.station,Station.name, Station.latitude, Station.longitude, Station.elevation).all()
stations_df = pd.DataFrame(stations_query, columns=['station', 'name','latitude','longitude','elevation'])
stations_df.set_index('station', inplace=True) 


#################################################
# Design a query to find the most active stations
# List the stations and the counts in descending order
most_active_stations_query = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc())

all_most_active_stations = most_active_stations_query.all()
all_most_active_stations

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
most_active_station_id = most_active_stations_query.first()[0]
most_active_station_id

temp_summ = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == most_active_station_id).all()

#################################################
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
    result={}
    for index, row in ann_prcp_summary_df.iterrows():
        result[index]=dict(row)
    return jsonify(result) 

#################################################
@app.route("/api/v1.0/stations")
def stations():
    result={}
    for index, row in stations_df.iterrows():
        result[index]=dict(row)
    return jsonify(result) 

#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    result={}
    for index, row in ann_tobs_df.iterrows():
        result[index]=dict(row)   
    return jsonify(result)

#################################################

#################################################
if __name__ == "__main__":
    app.run(debug=True)
