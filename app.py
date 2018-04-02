import pandas as pd
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, case

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
def month_started_stacked_bar_chart(parent_category,category):
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

@app.route('/length_campaign_chart/<parent_category>/<category>/')
def length_campaign_stacked_bar_chart(parent_category,category):
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

    query_campaign_length = case(
        [
            (campaigns.campaign_length <= 5, '<=5'),
            (((campaigns.campaign_length > 5) & (campaigns.campaign_length <= 10)), '5-10'),
            (((campaigns.campaign_length > 10) & (campaigns.campaign_length <= 15)), '10-15'),
            (((campaigns.campaign_length > 15) & (campaigns.campaign_length <= 20)), '15-20'),
            (((campaigns.campaign_length > 20) & (campaigns.campaign_length <= 25)), '20-25'),
            (((campaigns.campaign_length > 25) & (campaigns.campaign_length <= 30)), '25-30'),
            (((campaigns.campaign_length > 30) & (campaigns.campaign_length <= 35)), '30-35'),
            (((campaigns.campaign_length > 35) & (campaigns.campaign_length <= 40)), '35-40'),
            (((campaigns.campaign_length > 40) & (campaigns.campaign_length <= 45)), '40-45'),
            (((campaigns.campaign_length > 45) & (campaigns.campaign_length <= 50)), '45-50'),
            (((campaigns.campaign_length > 50) & (campaigns.campaign_length <= 55)), '50-55'),
            (((campaigns.campaign_length > 55) & (campaigns.campaign_length <= 60)), '55-60'),
            (campaigns.campaign_length >= 60, '>60')
        ]
    )

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(query_campaign_length,func.count(campaigns.id)).filter(*queries_successful).group_by(query_campaign_length).all()
    failed_query = session.query(query_campaign_length,func.count(campaigns.id)).filter(*queries_failed).group_by(query_campaign_length).all()
    canceled_query = session.query(query_campaign_length,func.count(campaigns.id)).filter(*queries_canceled).group_by(query_campaign_length).all()

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'length_bin':[]}
    length_bins_list = ['<=5','5-10','10-15','15-20','20-25','25-30','30-35','35-40','40-45','45-50','50-55','55-60','>60']
    length_bins_object = {'<=5':0,'5-10':1,'10-15':2,'15-20':3,'20-25':4,'25-30':5,'30-35':6,'35-40':7,'40-45':8,'45-50':9,'50-55':10,'55-60':11,'>60':12}
    for length_bin in length_bins_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['length_bin'].append(length_bin)
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        length_bin, num_campaigns = row
        num_successful_object['num_campaigns'][length_bins_object[length_bin]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[],'length_bin':[]}
    for length_bin in length_bins_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['length_bin'].append(length_bin)
    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        length_bin, num_campaigns = row
        num_failed_object['num_campaigns'][length_bins_object[length_bin]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[],'length_bin':[]}
    for length_bin in length_bins_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['length_bin'].append(length_bin)
    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        length_bin, num_campaigns = row
        num_canceled_object['num_campaigns'][length_bins_object[length_bin]] = num_campaigns
    
    response_object = {'successful': num_successful_object, 'failed': num_failed_object,'canceled': num_canceled_object}

    return jsonify(response_object)   

@app.route('/parent_category_chart/<month_started>/<length_campaign>/')
def parent_category_stacked_bar_chart(month_started,length_campaign):
    # filter by category
    queries = []
    if month_started != 'All Months':
        queries.append(campaigns.month_started == month_started)

    if length_campaign == '<=5':
        queries.append(campaigns.campaign_length <= 5)
    elif length_campaign == '5-10':
        queries.append((campaigns.campaign_length > 5) & (campaigns.campaign_length <= 10))
    elif length_campaign == '10-15':
        queries.append((campaigns.campaign_length > 10) & (campaigns.campaign_length <= 15)) 
    elif length_campaign == '15-20':
        queries.append((campaigns.campaign_length > 15) & (campaigns.campaign_length <= 20))
    elif length_campaign == '20-25':
        queries.append((campaigns.campaign_length > 20) & (campaigns.campaign_length <= 25))
    elif length_campaign == '25-30':
        queries.append((campaigns.campaign_length > 25) & (campaigns.campaign_length <= 30))
    elif length_campaign == '30-35':
        queries.append((campaigns.campaign_length > 30) & (campaigns.campaign_length <= 35))
    elif length_campaign == '35-40':
        queries.append((campaigns.campaign_length > 35) & (campaigns.campaign_length <= 40))
    elif length_campaign == '40-45':
        queries.append((campaigns.campaign_length > 40) & (campaigns.campaign_length <= 45))
    elif length_campaign == '45-50':
        queries.append((campaigns.campaign_length > 45) & (campaigns.campaign_length <= 50))
    elif length_campaign == '50-55':
        queries.append((campaigns.campaign_length > 50) & (campaigns.campaign_length <= 55))
    elif length_campaign == '55-60':
        queries.append((campaigns.campaign_length > 55) & (campaigns.campaign_length <= 60))
    elif length_campaign == '>60':
        queries.append(campaigns.campaign_length >= 60)

    queries_successful = queries[:]
    queries_successful.append(campaigns.state == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.state == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.state == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.parent_category, func.count(campaigns.id)).filter(
        *queries_successful).group_by(campaigns.parent_category).all()
    failed_query = session.query(campaigns.parent_category, func.count(campaigns.id)).filter(
        *queries_failed).group_by(campaigns.parent_category).all()
    canceled_query = session.query(campaigns.parent_category, func.count(campaigns.id)).filter(
        *queries_canceled).group_by(campaigns.parent_category).all()

    parent_category_query = session.query(distinct(campaigns.parent_category)).filter(*queries).all()
    parent_category_list = []
    parent_category_object = {}
    for index,row in enumerate(parent_category_query):
        temp, = row
        parent_category_list.append(temp)
        parent_category_object[temp] = index

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'parent_category':[]}

    for parent_category in parent_category_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['parent_category'].append(parent_category)
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        parent_category, num_campaigns = row
        num_successful_object['num_campaigns'][parent_category_object[parent_category]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[],'parent_category':[]}

    for parent_category in parent_category_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['parent_category'].append(parent_category)
    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        parent_category, num_campaigns = row
        num_failed_object['num_campaigns'][parent_category_object[parent_category]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[],'parent_category':[]}

    for parent_category in parent_category_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['parent_category'].append(parent_category)
    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        parent_category, num_campaigns = row
        num_canceled_object['num_campaigns'][parent_category_object[parent_category]] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object}

    # return response object
    return jsonify(response_object)

@app.route('/category_chart/<month_started>/<length_campaign>/<parent_category>/')
def category_stacked_bar_chart(month_started,length_campaign,parent_category):
    # filter by category
    queries = []
    if month_started != 'All Months':
        queries.append(campaigns.month_started == month_started)

    if length_campaign == '<=5':
        queries.append(campaigns.campaign_length <= 5)
    elif length_campaign == '5-10':
        queries.append((campaigns.campaign_length > 5) & (campaigns.campaign_length <= 10))
    elif length_campaign == '10-15':
        queries.append((campaigns.campaign_length > 10) & (campaigns.campaign_length <= 15)) 
    elif length_campaign == '15-20':
        queries.append((campaigns.campaign_length > 15) & (campaigns.campaign_length <= 20))
    elif length_campaign == '20-25':
        queries.append((campaigns.campaign_length > 20) & (campaigns.campaign_length <= 25))
    elif length_campaign == '25-30':
        queries.append((campaigns.campaign_length > 25) & (campaigns.campaign_length <= 30))
    elif length_campaign == '30-35':
        queries.append((campaigns.campaign_length > 30) & (campaigns.campaign_length <= 35))
    elif length_campaign == '35-40':
        queries.append((campaigns.campaign_length > 35) & (campaigns.campaign_length <= 40))
    elif length_campaign == '40-45':
        queries.append((campaigns.campaign_length > 40) & (campaigns.campaign_length <= 45))
    elif length_campaign == '45-50':
        queries.append((campaigns.campaign_length > 45) & (campaigns.campaign_length <= 50))
    elif length_campaign == '50-55':
        queries.append((campaigns.campaign_length > 50) & (campaigns.campaign_length <= 55))
    elif length_campaign == '55-60':
        queries.append((campaigns.campaign_length > 55) & (campaigns.campaign_length <= 60))
    elif length_campaign == '>60':
        queries.append(campaigns.campaign_length >= 60)

    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)

    queries_successful = queries[:]
    queries_successful.append(campaigns.state == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.state == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.state == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.category_name, func.count(campaigns.id)).filter(
        *queries_successful).group_by(campaigns.category_name).all()
    failed_query = session.query(campaigns.category_name, func.count(campaigns.id)).filter(
        *queries_failed).group_by(campaigns.category_name).all()
    canceled_query = session.query(campaigns.category_name, func.count(campaigns.id)).filter(
        *queries_canceled).group_by(campaigns.category_name).all()

    category_query = session.query(distinct(campaigns.category_name)).filter(*queries).all()
    category_list = []
    category_object = {}
    for index,row in enumerate(category_query):
        temp, = row
        category_list.append(temp)
        category_object[temp] = index

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'category_name':[]}

    for category in category_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['category_name'].append(category)
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        category_name, num_campaigns = row
        num_successful_object['num_campaigns'][category_object[category_name]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[],'category_name':[]}

    for category in category_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['category_name'].append(category)
    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        category_name, num_campaigns = row
        num_failed_object['num_campaigns'][category_object[category_name]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[],'category_name':[]}

    for category in category_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['category_name'].append(category)
    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        category_name, num_campaigns = row
        num_canceled_object['num_campaigns'][category_object[category_name]] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object}

    # return response object
    return jsonify(response_object)

@app.route('/states_map/<month_started>/<length_campaign>/<parent_category>/<category_name>/')
def states_map(month_started,length_campaign,parent_category,category_name):
    states_object = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AS": "American Samoa",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "DC": "District Of Columbia",
        "FM": "Federated States Of Micronesia",
        "FL": "Florida",
        "GA": "Georgia",
        "GU": "Guam",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MH": "Marshall Islands",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "MP": "Northern Mariana Islands",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PW": "Palau",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VI": "Virgin Islands",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming"
    }
    # filter by category
    queries = [] 
    queries.append(campaigns.state_or_province.in_(states_object))
    if month_started != 'All Months':
        queries.append(campaigns.month_started == month_started)

    if length_campaign == '<=5':
        queries.append(campaigns.campaign_length <= 5)
    elif length_campaign == '5-10':
        queries.append((campaigns.campaign_length > 5) & (campaigns.campaign_length <= 10))
    elif length_campaign == '10-15':
        queries.append((campaigns.campaign_length > 10) & (campaigns.campaign_length <= 15)) 
    elif length_campaign == '15-20':
        queries.append((campaigns.campaign_length > 15) & (campaigns.campaign_length <= 20))
    elif length_campaign == '20-25':
        queries.append((campaigns.campaign_length > 20) & (campaigns.campaign_length <= 25))
    elif length_campaign == '25-30':
        queries.append((campaigns.campaign_length > 25) & (campaigns.campaign_length <= 30))
    elif length_campaign == '30-35':
        queries.append((campaigns.campaign_length > 30) & (campaigns.campaign_length <= 35))
    elif length_campaign == '35-40':
        queries.append((campaigns.campaign_length > 35) & (campaigns.campaign_length <= 40))
    elif length_campaign == '40-45':
        queries.append((campaigns.campaign_length > 40) & (campaigns.campaign_length <= 45))
    elif length_campaign == '45-50':
        queries.append((campaigns.campaign_length > 45) & (campaigns.campaign_length <= 50))
    elif length_campaign == '50-55':
        queries.append((campaigns.campaign_length > 50) & (campaigns.campaign_length <= 55))
    elif length_campaign == '55-60':
        queries.append((campaigns.campaign_length > 55) & (campaigns.campaign_length <= 60))
    elif length_campaign == '>60':
        queries.append(campaigns.campaign_length >= 60)

    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)
    
    if category_name != 'All Categories':
        queries.append(campaigns.category_name == category_name)

    queries_successful = queries[:]
    queries_successful.append(campaigns.state == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.state == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.state == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.state_or_province, campaigns.country, func.count(campaigns.id)).filter(
        *queries_successful).group_by(campaigns.state_or_province).all()
    failed_query = session.query(campaigns.state_or_province, campaigns.country, func.count(campaigns.id)).filter(
        *queries_failed).group_by(campaigns.state_or_province).all()
    canceled_query = session.query(campaigns.state_or_province, campaigns.country, func.count(campaigns.id)).filter(
        *queries_canceled).group_by(campaigns.state_or_province).all()

    state_query = session.query(distinct(campaigns.state_or_province)).filter(*queries).all()
    state_list = []
    state_object = {}
    for index,row in enumerate(state_query):
        temp, = row
        state_list.append(temp)
        state_object[temp] = index

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'state_name':[]}

    for state in state_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['state_name'].append(state)

    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        state_name, country_name, num_campaigns = row
        num_successful_object['num_campaigns'][state_object[state_name]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[], 'state_name':[]}

    for state in state_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['state_name'].append(state)

    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        state_name, country_name, num_campaigns = row
        num_failed_object['num_campaigns'][state_object[state_name]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[], 'state_name':[]}

    for state in state_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['state_name'].append(state)

    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        state_name, country_name, num_campaigns = row
        num_canceled_object['num_campaigns'][state_object[state_name]] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object, 'state': state_list}

    # return response object
    return jsonify(response_object)

@app.route('/countries_map/<month_started>/<length_campaign>/<parent_category>/<category_name>/')
def countries_map(month_started,length_campaign,parent_category,category_name):
    # filter by category
    queries = [] 
    if month_started != 'All Months':
        queries.append(campaigns.month_started == month_started)

    if length_campaign == '<=5':
        queries.append(campaigns.campaign_length <= 5)
    elif length_campaign == '5-10':
        queries.append((campaigns.campaign_length > 5) & (campaigns.campaign_length <= 10))
    elif length_campaign == '10-15':
        queries.append((campaigns.campaign_length > 10) & (campaigns.campaign_length <= 15)) 
    elif length_campaign == '15-20':
        queries.append((campaigns.campaign_length > 15) & (campaigns.campaign_length <= 20))
    elif length_campaign == '20-25':
        queries.append((campaigns.campaign_length > 20) & (campaigns.campaign_length <= 25))
    elif length_campaign == '25-30':
        queries.append((campaigns.campaign_length > 25) & (campaigns.campaign_length <= 30))
    elif length_campaign == '30-35':
        queries.append((campaigns.campaign_length > 30) & (campaigns.campaign_length <= 35))
    elif length_campaign == '35-40':
        queries.append((campaigns.campaign_length > 35) & (campaigns.campaign_length <= 40))
    elif length_campaign == '40-45':
        queries.append((campaigns.campaign_length > 40) & (campaigns.campaign_length <= 45))
    elif length_campaign == '45-50':
        queries.append((campaigns.campaign_length > 45) & (campaigns.campaign_length <= 50))
    elif length_campaign == '50-55':
        queries.append((campaigns.campaign_length > 50) & (campaigns.campaign_length <= 55))
    elif length_campaign == '55-60':
        queries.append((campaigns.campaign_length > 55) & (campaigns.campaign_length <= 60))
    elif length_campaign == '>60':
        queries.append(campaigns.campaign_length >= 60)

    if parent_category != 'All Parent Categories':
        queries.append(campaigns.parent_category == parent_category)
    
    if category_name != 'All Categories':
        queries.append(campaigns.category_name == category_name)

    queries_successful = queries[:]
    queries_successful.append(campaigns.state == 'successful')
    queries_failed = queries[:]
    queries_failed.append(campaigns.state == 'failed')
    queries_canceled = queries[:]
    queries_canceled.append(campaigns.state == 'canceled')

    # find number of successful, failed, and canceled campaigns
    successful_query = session.query(campaigns.country, func.count(campaigns.id)).filter(
        *queries_successful).group_by(campaigns.country).all()
    failed_query = session.query(campaigns.country, func.count(campaigns.id)).filter(
        *queries_failed).group_by(campaigns.country).all()
    canceled_query = session.query(campaigns.country, func.count(campaigns.id)).filter(
        *queries_canceled).group_by(campaigns.country).all()

    country_query = session.query(distinct(campaigns.country)).filter(*queries).all()
    country_list = []
    country_object = {}
    for index,row in enumerate(country_query):
        temp, = row
        country_list.append(temp)
        country_object[temp] = index

    # set up query list for each success state
    #set up return object for successful campaigns
    num_successful_object = {'num_campaigns':[],'country_name':[]}

    for country in country_list:
        num_successful_object['num_campaigns'].append(0)
        num_successful_object['country_name'].append(country)
    # unpack list of tuples for number of campaigns per month
    for row in successful_query:
        country_name, num_campaigns = row
        num_successful_object['num_campaigns'][country_object[country_name]] = num_campaigns

    #set up return object for failed campaigns
    num_failed_object = {'num_campaigns':[],'country_name':[]}

    for country in country_list:
        num_failed_object['num_campaigns'].append(0)
        num_failed_object['country_name'].append(country)
    # unpack list of tuples for number of campaigns per month
    for row in failed_query:
        country_name, num_campaigns = row
        num_failed_object['num_campaigns'][country_object[country_name]] = num_campaigns

    #set up return object for canceled campaigns
    num_canceled_object = {'num_campaigns':[],'country_name':[]}

    for country in country_list:
        num_canceled_object['num_campaigns'].append(0)
        num_canceled_object['country_name'].append(country)
    # unpack list of tuples for number of campaigns per month
    for row in canceled_query:
        country_name, num_campaigns = row
        num_canceled_object['num_campaigns'][country_object[country_name]] = num_campaigns

   # build response object
    response_object = {'successful': num_successful_object, 'failed': num_failed_object, 'canceled': num_canceled_object}

    # return response object
    return jsonify(response_object)

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)