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

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.externals import joblib
from keras.utils import to_categorical
from keras.models import load_model
from sklearn.externals import joblib

model_file = 'models/nn_model.hdf5'
model = load_model(model_file)

scaler_file = 'models/X_scalar.save'
scaler = joblib.load(scaler_file)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# from sklearn import tree
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.externals import joblib

# #load models
# model_name = 'knn'
# model_name_backers = 'knn_backers'

# loaded_model = joblib.load(f'models/{model_name}.pkl')
# loaded_model_backers = joblib.load(f'models/{model_name_backers}.pkl')


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

@app.route("/predict/<titleText>/<blurbText>/<goalText>/<campaignLengthText>/<startMonth>/<parentCategory>/<category>/<country>/")
def predict(titleText,blurbText,goalText,campaignLengthText,startMonth,parentCategory,category,country):
    print(titleText)
    print(blurbText)
    print(goalText)
    print(campaignLengthText)
    print(startMonth)
    print(parentCategory)
    print(category)
    print(country)

    category_name_dic = {'Flight': 0, 'Letterpress': 1, 'Apps': 2, 'Camera Equipment': 3, 'Nonfiction': 4, 'Electronic Music': 5, 'Weaving': 6, 'Faith': 7, 'Animals': 8, 'Video Art': 9, 'Tabletop Games': 10, 'Ready-to-wear': 11, 'Music Videos': 12, 'Graphic Novels': 13, 'Comedy': 14, 'Hardware': 15, 'Gaming Hardware': 16, 'Robots': 17, 'Food Trucks': 18, 'Photo': 19, 'Couture': 20, 'Civic Design': 21, 'Metal': 22, 'Art Books': 23, 'Taxidermy': 24, 'Film & Video': 25, 'Residencies': 26, 'Calendars': 27, 'Action': 28, 'Drama': 29, 'Sculpture': 30, 'Audio': 31, 'Performances': 32, 'Pet Fashion': 33, 'Fiction': 34, 'Technology': 35, 'Vegan': 36, 'Graphic Design': 37, 'Hip-Hop': 38, 'Drinks': 39, '3D Printing': 40, 'Fabrication Tools': 41, 'Textiles': 42, 'Playing Cards': 43, 'Places': 44, 'Community Gardens': 45, 'Academic': 46, 'Kids': 47, 'Gadgets': 48, 'Theater': 49, 'Television': 50, 'Conceptual Art': 51, 'Crafts': 52, 'Video Games': 53, 'Young Adult': 54, 'Puzzles': 55, 'Woodworking': 56, 'Architecture': 57, 'Restaurants': 58, 'Games': 59, 'Festivals': 60, 'Webcomics': 61, 'Country & Folk': 62, 'Apparel': 63, 'Jewelry': 64, 'Indie Rock': 65, 'Family': 66, 'Plays': 67, 'Printing': 68, 'Food': 69, 'Blues': 70, 'Experimental': 71, 'Literary Spaces': 72, 'Movie Theaters': 73, 'Anthologies': 74, 'Painting': 75, 'Jazz': 76, 'Webseries': 77, 'Art': 78, 'Chiptune': 79, 'Immersive': 80, 'Farms': 81, 'People': 82, 'DIY Electronics': 83, 'Accessories': 84, 'Footwear': 85, 'Fantasy': 86, 'World Music': 87, 'Documentary': 88, 'Zines': 89, 'Embroidery': 90, 'Radio & Podcasts': 91, 'Classical Music': 92, 'Thrillers': 93, 'Product Design': 94, 'Translations': 95, 'Digital Art': 96, 'Cookbooks': 97, 'Comic Books': 98, 'Photography': 99, 'Shorts': 100, 'Comics': 101, 'Poetry': 102, 'Periodicals': 103, 'Pottery': 104, 'Installations': 105, 'Narrative Film': 106, 'Events': 107, 'Ceramics': 108, 'Publishing': 109, 'Candles': 110, 'Photobooks': 111, 'Interactive Design': 112, 'Dance': 113, 'Web': 114, 'Typography': 115, 'DIY': 116, 'Knitting': 117, 'Wearables': 118, 'Mixed Media': 119, 'Childrenswear': 120, 'Stationery': 121, 'Video': 122, 'Spaces': 123, 'Nature': 124, 'Bacon': 125, 'Print': 126, 'Mobile Games': 127, 'Rock': 128, 'Design': 129, 'Live Games': 130, 'Sound': 131, 'Punk': 132, 'Illustration': 133, 'Fine Art': 134, "Farmer's Markets": 135, 'Journalism': 136, "Children's Books": 137, 'Software': 138, 'Quilts': 139, 'Music': 140, 'Animation': 141, 'Horror': 142, 'R&B': 143, 'Pop': 144, 'Crochet': 145, 'Musical': 146, 'Public Art': 147, 'Workshops': 148, 'Space Exploration': 149, 'Romance': 150, 'Glass': 151, 'Science Fiction': 152, 'Makerspaces': 153, 'Performance Art': 154, 'Small Batch': 155, 'Latin': 156, 'Literary Journals': 157}
    parent_category_dic = {'none': 0, 'Food': 1, 'Technology': 2, 'Crafts': 3, 'Film & Video': 4, 'Games': 5, 'Publishing': 6, 'Journalism': 7, 'Dance': 8, 'Photography': 9, 'Art': 10, 'Comics': 11, 'Design': 12, 'Music': 13, 'Theater': 14}
    month_dic = {'February': 0, 'October': 1, 'March': 2, 'July': 3, 'June': 4, 'September': 5, 'August': 6, 'November': 7, 'January': 8, 'April': 9, 'May': 10, 'December': 11}
    country_dic = {'Norway': 0, 'Austria': 1, 'Canada': 2, 'Spain': 3, 'Switzerland': 4, 'Luxembourg': 5, 'Germany': 6, 'Australia': 7, 'Belgium': 8, 'Denmark': 9, 'Singapore': 10, 'Japan': 11, 'United States': 12, 'Great Britain': 13, 'New Zealand': 14, 'Mexico': 15, 'France': 16, 'Italy': 17, 'Netherlands': 18, 'Ireland': 19, 'Sweeden': 20, 'Hong Kong': 21}
    country_dic = {'Sweeden': 0, 'Italy': 1, 'Denmark': 2, 'Germany': 3, 'Ireland': 4, 'Hong Kong': 5, 'New Zealand': 6, 'Great Britain': 7, 'France': 8, 'Japan': 9, 'Luxembourg': 10, 'Canada': 11, 'Canada': 12, 'Austria': 13, 'Norway': 14, 'Australia': 15, 'Netherlands': 16, 'Mexico': 17, 'Switzerland': 18, 'Belgium': 19, 'Spain': 20, 'United States': 21}

    category_name = category_name_dic[category]
    parent_category = parent_category_dic[parentCategory]
    month = month_dic[startMonth]
    goal = float(goalText)
    campaign_length = float(campaignLengthText)
    country = country_dic[country]
    
    try:
        title_length = len(titleText)
        sentiment = analyzer.polarity_scores(titleText)
    except TypeError:
        title_length = 0
        sentiment = {'compound':0,'pos':0,'neg':0,'neu':1}
    title_compound = sentiment['compound']
    title_positive = sentiment['pos']
    title_negative = sentiment['neg']
    title_neutral = sentiment['neu']

    try:
        blurb_length = len(blurbText)
        sentiment = analyzer.polarity_scores(titleText)
    except TypeError:
        blurb_length = 0
        sentiment = {'compound':0,'pos':0,'neg':0,'neu':1}
    blurb_compound = sentiment['compound']
    blurb_positive = sentiment['pos']
    blurb_negative = sentiment['neg']
    blurb_neutral = sentiment['neu']

    #value for usd
    currency = 5

    #what datatype does X need to be?
    X = [[campaign_length,blurb_length,blurb_compound,blurb_positive,blurb_negative,blurb_neutral, title_length, title_compound, title_positive,title_negative,title_neutral,goal,country,currency,category_name,parent_category,month]]
    
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled).tolist()

    # #models are loaded at very beginning of app
    # prediction = loaded_model.predict(X)
    # prediction_list = prediction.tolist()

    # #what values do we want to test our model with?
    # backers_list = []

    # backers_predictions = []
    # for backer in backers_list:
    #     backers_predictions.append(loaded_model_backers.predict([X,backer]))

    #need to figure out how to deal with output so that we can jsonify it!
    response_object = {'prediction': prediction}
    return jsonify(response_object)

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stats/")
def stats():
    return render_template("stats.html")

@app.route("/location/")
def location():
    return render_template("location.html")

@app.route("/writing/")
def writing():
    return render_template("writing.html")

@app.route("/complete/")
def complete():
    return render_template("complete.html")

if __name__ == "__main__":
    app.run()