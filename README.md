# Campaign Starter
## Analysis of Kickstarter data, and a predictive model to estimate a campaign's success before it is launched

Visit the deployed [Campaign Starter](https://campaign-starter.herokuapp.com/ "Campaign Starter") App!

## Project Summary
Campaign starter uses data from over 180,000 past kickstarter campaigns to display trends in campaign success/failure across differing campaign categories and sub-categories, campaign lengths, and time of year. Additionally, there is a "Test Your Campaign" features that runs user submitted data against a machine learning model to predict success or failure of the campaign.

## Machine Learning Modelling & Results
After data was prepared for modelling (as described in the "Dataset & Manipulation" section below), training and testing datasets were run through various machine learning models and scored to gauge effectiveness of the models. Logistic Regression, Random Forest, K Nearest Neighbors, and Neural Network models were used. Results shown below.

### Model Results

|Model|Testing Data Score|Training Data Score|Testing Data Score (w/ backer count)|Training Data Score (w/ backer count)|
| -------------|:----:|:----:|:----:|:----:|
|Random Forest| 0.78 | 1.0 | 0.95 | 1.0 |
|Neural Network| 0.75 | 0.76 | 0.94 | 0.94 |
|K Nearest Neighbors (7)| 0.66 | 0.75 | 0.92 | 0.94 | 
|Logistic Regression| 0.64 | 0.64 | 0.93 | 0.93 |

## Dataset & Data Manipulation
This project uses a dataset of 180,000+ kickstarter campaigns. The dataset was first scrubbed of records for ongoing or canceled projects to ensure all results were successes or failures. Campaign data was parsed for meaningful data features - numerical features such as Goal Amount and Campaign length, categorical features such as Category and Month of the Campaign, and calculated features such as Blurb Length and Blurb Sentiment.

This data was store in a SQLite database for use by the web application, and then scaled and encoded for use by the machine learning models described above.

## Data Source
[Web Robots](https://webrobots.io/kickstarter-datasets/ "Web Robots"
