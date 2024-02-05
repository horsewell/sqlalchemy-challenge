# Module 10 Challenge

Congratulations! You've decided to treat yourself to a long holiday vacation in Honolulu, Hawaii. To help with your trip planning, you decide to do a climate analysis about the area. The following sections outline the steps that you need to take to accomplish this task.

## Part 1: Analyse and Explore the Climate Data

Must run SurfsUp/climate.ipynb as a jupyter notebook. It accessess the hawaii.sqlite file that is in the /Resources folder using SQLAlchemy

### Precipitation Analysis

* Find the most recent date in the dataset
* Create a query that collects the data and precipitation for the last year and create a Pandas DataFrame
* Sort the DataFrame by date
* Plot the results
* Print the summary statistics

### Station Analysis

* Find the number of stations
* List the stations and observation counts in decending order
* Find the min, max and average temperatues for the most active station
* get the previous 12 monhts of temperature observations and save in a Pandas DataFrame
* Plot a histogram with 12 bins

## Part 2: Design Your Climate App

Need to navigate the command line to the folder that SurfsUp/app.py is in and run it. Then go to the browser location that the Flask app is running (default is http://127.0.0.1:5000/). Get the data via a SQLAlchemy session by accessing the hawaii.sqlite in the /Resources folder.

The flask app should show the following:

* Display a landing page with the available routes

### Static Routes

* Return precipitation data as JSON
* Return stations data as JSON
* Return tobs data for the most active station  as JSON

### Dynamic Routes

* When one date is given return the min, max and average temperatures from that date to the end of the dataset as JSON
* When two dates are given return the min, max and average temperatures from the first date to the second date as JSON

Student: Tyson Horsewell