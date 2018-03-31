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
#engine = create_engine("sqlite:///db/winter_olympics.sqlite")

# reflect existing database into new model
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# save reference to tables
campaigns  = Base.classes.campaigns

# create session to query tables
session = Session(engine)

app = Flask(__name__)

# create route to return possible category options for select menu
@app.route('/fetch_categories')
def fetch_categories():
    # get possible categories
    category_list = []
    response = session.query(distinct(campaigns.categories)).all()
    for category in response:
        temp, = category
        category_list.append(temp)

    # return response object
    return jsonify(category_list)

# create route to return possible subcategory options for select menu
def fetch_subcategories():
    # get possible categories
    subcategory_list = []
    response = session.query(distinct(campaigns.subcategories)).all()
    for category in response:
        temp, = category
        subcategory_list.append(temp)

    # return response object
    return jsonify(subcategory_list)

@app.route('/month_started_chart/<category>/<subcategory>/')
def stacked_bar_chart(category, subcategory):
    # filter by category
    queries = []
    if category != 'All Categories':
        queries.append(campaigns.categories == category)
    if subcategory != 'All Subcategories':
        queries.append(campaigns.subcategories == subcategory)

    #find month started, length of campaign, category, subcategory, location, successful
    query = session.query(campaigns.month_started, campaigns.category, campaigns.subcategory)

    queries_successful = queries[:]
    queries_successful.append(campaigns.successful == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.successful == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.successful == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.month_started, func.count(campaigns.id))
        .filter(*queries_successful).group_by(campaigns.month_started).all()
    failed_query = session.query(campaigns.month_started, func.count(campaigns.id))
        .filter(*queries_failed).group_by(campaigns.month_started).all()
    canceled_query = session.query(campaigns.month_started, func.count(campaign.id))
        .filter(*queries_successful).group_by(campaigns.month_started).all()

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {}
    month_list = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for month in month_list:
        num_successful_object[month] = 0
        num_successful_object['month_name'] = month
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        month_started, num_campaigns = row
        num_successful_object[month_started] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {}
    for month in month_list:
        num_failed_object[month] = 0
        num_successful_object['month_name'] = month
    # unpack list of tuples for number of medals
    for row in failed_query:
        month_started, num_campaigns = row
        num_failed_object[month_started] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {}
    for month in month_list:
        num_canceled_object[month] = 0
        num_successful_object['month_name'] = month
    # unpack list of tuples for number of medals
    for row in canceled_query:
        month_started, num_campaigns = row
        num_canceled_object[month_started] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object}

    # return response object
    return jsonify(response_object)