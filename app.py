import pandas as pd
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

from flask import(
    Flask,
    render_template,
    jsonify
)

# Database Setup
engine = create_engine("sqlite:///db/kickstarter_campaigns.sqlite")

# reflect existing database into new model
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# save reference to tables
campaigns  = Base.classes.kickstarter_campaigns

# create session to query tables
session = Session(engine)

app = Flask(__name__)

# create route to return possible parent category options for select menu
@app.route('/fetch_parent_categories')
def fetch_parent_categories():
    # get possible categories
    parent_category_list = []
    response = session.query(distinct(campaigns.parent_category)).all()
    for category in response:
        temp, = category
        parent_category_list.append(temp)

    # return response object
    return jsonify(parent_category_list)

# create route to return possible category options for select menu for month started stacked bar chart
@app.route('/fetch_categories_month_started/<parent_category>/')
def fetch_categories_month_started(parent_category):
    # get possible categories
    category_list = []
    
    # filter by parent category
    queries = []
    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)

    response = session.query(distinct(campaigns.category_name)).filter(*queries).all()
    for category in response:
        temp, = category
        category_list.append(temp)

    # return response object
    return jsonify(category_list)

# create route to return possible category options for select menu for month started stacked bar chart
@app.route('/fetch_categories_length_campaign/<parent_category>/')
def fetch_categories_length_campaign(parent_category):
    # get possible categories
    category_list = []
    
    # filter by parent category
    queries = []
    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)

    response = session.query(distinct(campaigns.category_name)).filter(*queries).all()
    for category in response:
        temp, = category
        category_list.append(temp)

    # return response object
    return jsonify(category_list)

@app.route('/month_started_chart/<parent_category>/<category>/')
def stacked_bar_chart(parent_category,category):
    # filter by category
    queries = []
    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)
    if category != 'All Categories':
        queries.append(campaigns.category_name == category)

    queries_successful = queries[:]
    queries_successful.append(campaigns.state == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.state == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.state == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.month_started, func.count(campaigns.id)).filter(
        *queries_successful).group_by(campaigns.month_started).all()
    failed_query = session.query(campaigns.month_started, func.count(campaigns.id)).filter(
        *queries_failed).group_by(campaigns.month_started).all()
    canceled_query = session.query(campaigns.month_started, func.count(campaigns.id)).filter(
        *queries_canceled).group_by(campaigns.month_started).all()

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'month_name':[]}
    month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']
    month_object = {'January':0,'February':1,'March':2,'April':3,'May':4,'June':5,'July':6,'August':7,'September':8,'October':9,'November':10,'December':11}
    for month in month_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['month_name'].append(month)
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        month_started, num_campaigns = row
        num_successful_object['num_campaigns'][month_object[month_started]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[],'month_name':[]}
    for month in month_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['month_name'].append(month)
    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        month_started, num_campaigns = row
        num_failed_object['num_campaigns'][month_object[month_started]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[],'month_name':[]}
    for month in month_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['month_name'].append(month)
    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        month_started, num_campaigns = row
        num_canceled_object['num_campaigns'][month_object[month_started]] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object}

    # return response object
    return jsonify(response_object)

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()