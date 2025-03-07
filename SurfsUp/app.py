# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)
recent_date = session.query(func.max(Measurement.date)).first()[0]
recent_date_dt = dt.datetime.strptime(recent_date, "%Y-%m-%d")
one_year_ago = recent_date_dt - dt.timedelta(days=365)
session.close()

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Route: Homepage
@app.route("/")
def welcome():
    return (
        f"<h2>Welcome to the Climate App API!</h2>"
        f"<p>Here are the available routes:</p>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a> - Last 12 months of precipitation data</li>"
        f"<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a> - List of weather stations</li>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a> - Temperature observations for the most active station</li>"
        f"<li><a href='/api/v1.0/&lt;start&gt;'>/api/v1.0/start</a> - Min, Avg, Max temps from a start date</li>"
        f"<li><a href='/api/v1.0/&lt;start&gt;/&lt;end&gt;'>/api/v1.0/start/end</a> - Min, Avg, Max temps for a date range</li>"
        f"</ul>"
    )

# Route: Precipitation Data
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert query results to a dictionary using date as the key and prcp as the value
    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

# Route: Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    station_list = list(np.ravel(results))
    return jsonify(station_list)

# Route: Temperature Observations for Most Active Station
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.tobs).filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= one_year_ago).all()
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps)

# Route: Min, Avg, Max Temps from Start Date
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    session.close()

    temp_stats = list(np.ravel(results))
    temp_data = {
        "Start Date": start,
        "TMIN": temp_stats[0],
        "TAVG": round(temp_stats[1], 2),
        "TMAX": temp_stats[2]
    }
    return jsonify(temp_data)

# Route: Min, Avg, Max Temps for Date Range
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_stats = list(np.ravel(results))
    temp_data = {
        "Start Date": start,
        "End Date": end,
        "TMIN": temp_stats[0],
        "TAVG": round(temp_stats[1], 2),
        "TMAX": temp_stats[2]
    }
    return jsonify(temp_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

























