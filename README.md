# Campaign Starter
## Analysis of Kickstarter data, and a predictive model to estimate a campaign's success before it is launched

Visit the deployed [Campaign Starter](https://campaign-starter.herokuapp.com/ "Campaign Starter") App!

## Project Summary


## Machine Learning Modelling & Results

### Model Results

|Model|Testing Data Score|Training Data Score|Testing Data Score (w/ backer count)|Training Data Score (w/ backer count)|
| -------------|:----:|:----:|:----:|:----:|
|Neural Network| 0.82 | 0.97 | 0.97 | 0.99 |
|Random Forest| 0.78 | 1.0 | 0.95 | 1.0 |
|K Nearest Neighbors (7)| 0.66 | 0.75 | 0.92 | 0.94 | 
|Logistic Regression| 0.64 | 0.64 | 0.93 | 0.93 |


	model 	test_score 	test_score_backers 	train_score 	
0 	random_forest 	0.783823 	0.950322 	0.999985 	1.000000
1 	logistic_regression 	0.640523 	0.931518 	0.641737 	0.931130
2 	k_nearest_neigbors_7 	0.663767 	0.921546 	0.749615 	0.939086
3 	neural_network 	0.737090 	0.923665 	0.751534 	0.926527

## Dataset & Data Manipulation