from app import app
from config import *
from db_utils import *
from file_utils import *
from flask import render_template, session, url_for, request, g, jsonify
from .models import Customer, Expert, Topic, Category

@app.route('/')
@app.route('/index')
def index():
    content = load_json_file(EXPERT_CATEGORY_PATH)
    return "Hello, World!"

@app.route('/api/v1/customers/<customer_id>/', methods = ['GET'])
def customers(customer_id):
    user = Customer.query.filter_by(user_id = customer_id).first()
    if user is None:
	return jsonify({'customers':''})
    else:
        return jsonify({'customers':user.serialize()})

@app.route('/api/v1/customers', methods = ['POST'])
def create_customer():
    return "Customer created!"

"""
    This method loads the categories from a text file and stores it in memory.
    The key:value format of the data structure in memory is:
	category-id : ['first level category text', 'second level category text']

    The category-id is calculated by first_level_index * 100 + second_level_index

    The content of the category hierarchy is stored in a plain text file, not in db.
    Categories can only be updated (extended, modified or reduced) by the server side.
"""
@app.route('/api/v1/categories', methods = ['GET'])
def load_categories():
    #if request.method == 'POST':
    content = load_json_file(EXPERT_CATEGORY_PATH)
    categories = {}
    for i in range(len(content['level1'])):
	for j in range(len(content['level2'][i])):
	    categories[(i + 1) * CATEGORY_ID_MULTIPLIER + (j + 1)] = [content['level1'][i], content['level2'][i][j]]
    session['categories'] = categories
    return 'Categories loaded in json'

@app.route('/test')
def test():
    return "Testing!"

"""
    Create some data in the db for testing purposes.
    In the command line, run:
    curl -d "" "http://localhost:5000/api/v1/internal/data/"
"""
@app.route('/api/v1/internal/data/', methods = ['POST'])
def create_data():
    create_data_in_db()
    return "Data created!"
