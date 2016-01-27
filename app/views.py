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
